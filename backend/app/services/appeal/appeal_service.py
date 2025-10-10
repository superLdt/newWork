from typing import Dict, Any, List
from datetime import datetime
import logging

from app.services.dispatch.dispatch_service import DispatchService
from flask_jwt_extended import get_current_user
from app.models.task import ManualDispatchTask
from app.models.dispatch_status_history import DispatchStatusHistory
from app.models.common.file_record import FileRecord

logger = logging.getLogger(__name__)


class AppealService:
    """
    申诉相关服务层，承载数据库操作与状态流转，供控制器或业务层调用。
    """

    @staticmethod
    def process_appeal_review(task_id: str, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理申诉审核（管理员/调度员角色）。

        Args:
            task_id: 任务ID
            review_data: 审核数据，包含审核结果、最终吨位、审核备注

        Returns:
            Dict: 处理结果
        """
        try:
            # 获取任务信息
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'success': False,
                    'message': '任务不存在'
                }

            # 检查任务状态是否为申诉待审核
            if task.get('status') != '申诉待审核':
                return {
                    'success': False,
                    'message': f'任务状态不允许审核操作，当前状态：{task.get("status")}'
                }

            # 获取当前用户信息
            current_user = get_current_user()
            if not current_user:
                return {
                    'success': False,
                    'message': '无法获取当前用户信息'
                }

            # 审核结果（默认通过）
            review_result = review_data.get('review_result', 'approved')

            # 更新任务状态为已完成，并记录审核信息
            update_data = {
                'status': '已完成',
                'current_handler_user_id': getattr(current_user, 'id', None),
                'appeal_reviewed_by': getattr(current_user, 'id', None),
                'appeal_reviewed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'appeal_review_result': review_result,
                'final_confirmed_tonnage': review_data.get('final_tonnage'),
                'appeal_review_notes': review_data.get('review_notes', ''),
                'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 如果审核通过且提供了最终吨位，更新actual_weight字段
            if review_result == 'approved' and review_data.get('final_tonnage'):
                update_data['actual_weight'] = review_data.get('final_tonnage')

            DispatchService.update_task(task_id, update_data)

            # 记录审核完成状态历史
            result_text = '申诉通过' if review_result == 'approved' else '申诉驳回'
            comment_parts = [result_text]
            if review_data.get('final_tonnage'):
                comment_parts.append(f'最终确定吨位：{review_data.get("final_tonnage")}')
            if review_data.get('review_notes'):
                comment_parts.append(f'审核备注：{review_data.get("review_notes")}')

            # 第一条状态历史：申诉待审核 -> 申诉通过/申诉驳回
            status_history_data = {
                'previous_status': '申诉待审核',
                'new_status': result_text,
                'changed_by': getattr(current_user, 'id', None),
                'changed_at': datetime.now(),
                'comment': '。'.join(comment_parts),
                'next_handler_role': None
            }

            DispatchService.update_task_status(task_id, result_text, status_history_data)
            
            # 第二条状态历史：将任务置于已完成
            completion_history_data = {
                'previous_status': result_text,
                'new_status': '已完成',
                'changed_by': getattr(current_user, 'id', None),
                'changed_at': datetime.now(),
                'comment': '已完成',
                'next_handler_role': None
            }

            DispatchService.update_task_status(task_id, '已完成', completion_history_data)

            return {
                'success': True,
                'data': {
                    'task_id': task_id,
                    'status': '已完成',
                    'appeal_reviewed_by': getattr(current_user, 'id', None),
                    'appeal_reviewed_at': update_data['appeal_reviewed_at'],
                    'appeal_review_result': update_data['appeal_review_result'],
                    'final_confirmed_tonnage': update_data['final_confirmed_tonnage'],
                    'appeal_review_notes': update_data['appeal_review_notes']
                },
                'message': f'申诉审核完成，任务已完成。审核结果：{result_text}'
            }

        except Exception as e:
            logger.error(f'处理申诉审核失败: {str(e)}')
            return {
                'success': False,
                'message': f'处理申诉审核失败: {str(e)}'
            }

    @staticmethod
    def get_appeal_info(task_id: str) -> Dict[str, Any]:
        """
        获取任务申诉详情信息

        Args:
            task_id: 任务ID

        Returns:
            Dict[str, Any]: 申诉详情信息
        """
        try:
            # 获取任务信息
            task: ManualDispatchTask = ManualDispatchTask.query.get(task_id)
            if not task:
                return {
                    'success': False,
                    'message': '任务不存在'
                }

            # 从状态历史中获取最新的申诉提交记录（状态变更文本包含“申诉待审核”）
            appeal_history: DispatchStatusHistory = (
                DispatchStatusHistory.query
                .filter(
                    DispatchStatusHistory.task_id == task_id,
                    DispatchStatusHistory.status_change.like('%申诉待审核%')
                )
                .order_by(DispatchStatusHistory.timestamp.desc())
                .first()
            )

            if not appeal_history:
                return {
                    'success': False,
                    'message': '未找到申诉记录'
                }

            # 申诉人信息
            appeal_user_name = appeal_history.operator or '未知用户'

            # 从备注中提取申诉原因和申诉说明（使用note字段）
            appeal_reason = ''
            appeal_description = ''
            try:
                note_text = appeal_history.note or ''
                
                # 解析note字段，格式可能是：申诉原因：xxx；申诉说明：xxx
                if '申诉原因：' in note_text:
                    # 提取申诉原因
                    reason_part = note_text.split('申诉原因：', 1)[1]
                    if '；申诉说明：' in reason_part:
                        appeal_reason = reason_part.split('；申诉说明：', 1)[0].strip()
                        appeal_description = reason_part.split('；申诉说明：', 1)[1].strip()
                    elif ';申诉说明:' in reason_part:
                        appeal_reason = reason_part.split(';申诉说明:', 1)[0].strip()
                        appeal_description = reason_part.split(';申诉说明:', 1)[1].strip()
                    else:
                        appeal_reason = reason_part.strip()
                        appeal_description = ''
                else:
                    # 如果没有标准格式，整个note作为申诉说明
                    appeal_description = note_text.strip()
            except Exception:
                appeal_reason = ''
                appeal_description = note_text if 'note_text' in locals() else ''

            # 获取申诉证明材料（从 FileRecord 获取）
            evidence_files: List[Dict[str, Any]] = []
            try:
                files = FileRecord.query.filter_by(
                    business_type='supplier_appeal',
                    business_id=task_id,
                    is_deleted=False
                ).all()

                for file_record in files:
                    evidence_files.append({
                        'id': getattr(file_record, 'id', None),
                        'filename': getattr(file_record, 'original_filename', ''),
                        'url': getattr(file_record, 'file_url', ''),  # 使用file_url，已包含完整路径
                        'file_size': getattr(file_record, 'file_size', 0),
                        'upload_time': file_record.upload_time.strftime('%Y-%m-%d %H:%M:%S') if getattr(file_record, 'upload_time', None) else ''
                    })
            except Exception as e:
                logger.warning(f'获取申诉证明材料失败: {str(e)}')

            # 格式化申诉提交时间
            submitted_at = ''
            try:
                ts = getattr(appeal_history, 'timestamp', None)
                submitted_at = ts.strftime('%Y-%m-%d %H:%M:%S') if ts else ''
            except Exception:
                submitted_at = ''

            return {
                'success': True,
                'data': {
                    'task_id': task_id,
                    'appeal_submitted_at': submitted_at,
                    'appeal_user_id': None,
                    'appeal_user_name': appeal_user_name,
                    'appeal_reason': appeal_reason,
                    'appeal_description': appeal_description,  # 使用解析出的申诉说明
                    'evidence_files': evidence_files,
                    'task_status': getattr(task, 'status', ''),
                    'mail_route_name': getattr(task, 'mail_route_name', ''),
                    'organizing_unit': getattr(task, 'organizing_unit', '')
                },
                'message': '获取申诉信息成功'
            }
        except Exception as e:
            logger.error(f'获取申诉信息失败: {str(e)}')
            return {
                'success': False,
                'message': f'获取申诉信息失败: {str(e)}'
            }

    @staticmethod
    def get_supplier_appeal_tasks(supplier_id: int = None, page: int = 1, per_page: int = 10, 
                                status: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        获取供应商申诉任务列表
        
        Args:
            supplier_id: 供应商ID，如果为None则获取当前用户的申诉任务
            page: 页码
            per_page: 每页数量
            status: 申诉状态筛选
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 申诉任务列表和分页信息
        """
        try:
            from app.models.task import ManualDispatchTask
            from app.models.dispatch_status_history import DispatchStatusHistory
            from app.models.user import User
            from sqlalchemy import and_, or_
            
            # 角色感知的过滤逻辑
            current_user = get_current_user()
            if not current_user:
                return {
                    'success': False,
                    'message': '用户未登录'
                }

            query_conditions = []
            # 供应商仅查看所属派车单位的任务；管理员/区域调度员可查看全部
            is_supplier = current_user.has_role('供应商')
            is_admin_or_dispatch = current_user.is_admin() or current_user.has_role('区域调度员')

            if supplier_id is None and is_supplier:
                # 使用当前用户的派车单位做过滤
                organizing_unit_id = getattr(current_user, 'dispatch_unit_id', None)
                if organizing_unit_id is not None:
                    query_conditions.append(ManualDispatchTask.organizing_unit_id == organizing_unit_id)
            elif supplier_id is not None:
                # 外部传入的 supplier_id 用作单位过滤（兼容原逻辑）
                query_conditions.append(ManualDispatchTask.organizing_unit_id == supplier_id)
            else:
                # 管理员或区域调度员，不加单位过滤
                pass
            
            # 只查询有申诉记录的任务（状态包含申诉相关状态）
            appeal_statuses = ['申诉待审核', 'appeal_pending']
            
            # 添加状态筛选
            if status:
                if status in appeal_statuses:
                    query_conditions.append(ManualDispatchTask.status == status)
                else:
                    # 如果是其他状态，查询申诉审核结果
                    query_conditions.append(ManualDispatchTask.appeal_review_result == status)
            else:
                # 查询所有有申诉记录的任务
                query_conditions.append(
                    or_(
                        ManualDispatchTask.status.in_(appeal_statuses),
                        ManualDispatchTask.appeal_review_result.isnot(None)
                    )
                )
            
            # 添加日期筛选
            # 处理日期筛选（支持 YYYY-MM-DD 字符串）
            from datetime import datetime, timedelta
            def parse_date(d):
                try:
                    return datetime.strptime(d, '%Y-%m-%d')
                except Exception:
                    return None
            if start_date:
                sd = parse_date(start_date)
                if sd:
                    query_conditions.append(ManualDispatchTask.created_at >= sd)
            if end_date:
                ed = parse_date(end_date)
                if ed:
                    # 包含当天结束时间
                    query_conditions.append(ManualDispatchTask.created_at < (ed + timedelta(days=1)))
            
            # 执行查询
            query = ManualDispatchTask.query.filter(and_(*query_conditions))
            
            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # 安全格式化日期时间为字符串
            def safe_format_dt(value):
                try:
                    if value is None:
                        return None
                    # datetime对象
                    if hasattr(value, 'strftime'):
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    # 已是字符串则直接返回
                    if isinstance(value, str):
                        return value
                    # 其他类型尽量转为字符串
                    return str(value)
                except Exception:
                    return None

            tasks = []
            for task in pagination.items:
                # 获取申诉提交记录
                appeal_history = (
                    DispatchStatusHistory.query
                    .filter_by(task_id=task.task_id)
                    .filter(DispatchStatusHistory.status_change.like('%申诉待审核%'))
                    .order_by(DispatchStatusHistory.timestamp.desc())
                    .first()
                )
                
                # 获取申诉审核人信息
                appeal_reviewer_name = None
                if task.appeal_reviewed_by:
                    reviewer = User.query.get(task.appeal_reviewed_by)
                    appeal_reviewer_name = reviewer.username if reviewer else '未知用户'
                
                task_data = {
                    'id': task.task_id,
                    'dispatch_number': task.task_id,
                    'source_location': task.origin_bureau,
                    'destination_location': task.mail_route_name,
                    'tonnage': task.required_weight,
                    'volume': task.required_volume,
                    'status': task.status,
                    'created_at': safe_format_dt(getattr(task, 'created_at', None)),
                    'appeal_submitted_at': safe_format_dt(appeal_history.timestamp) if appeal_history else None,
                    'appeal_reason': getattr(task, 'appeal_reason', '') or (appeal_history.note if appeal_history else ''),
                    'appeal_review_result': task.appeal_review_result,
                    'appeal_reviewed_at': safe_format_dt(getattr(task, 'appeal_reviewed_at', None)),
                    'appeal_reviewed_by': task.appeal_reviewed_by,
                    'appeal_reviewer_name': appeal_reviewer_name,
                    'appeal_review_notes': task.appeal_review_notes
                }
                tasks.append(task_data)
            
            return {
                'success': True,
                'data': {
                    'tasks': tasks,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                },
                'message': '获取申诉任务列表成功'
            }
            
        except Exception as e:
            logger.error(f'获取供应商申诉任务列表失败: {str(e)}')
            return {
                'success': False,
                'message': f'获取申诉任务列表失败: {str(e)}'
            }

    @staticmethod
    def submit_appeal(task_id: str, appeal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提交供应商申诉

        Args:
            task_id: 任务ID
            appeal_data: 申诉数据，包含申诉原因和照片

        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            # 获取任务信息
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'success': False,
                    'message': '任务不存在'
                }

            # 检查任务状态是否允许申诉（只有待确认状态可以申诉）
            if task.get('status') != '待确认':
                return {
                    'success': False,
                    'message': f'任务状态不允许申诉，当前状态：{task.get("status")}'
                }

            # 获取当前用户信息
            current_user = get_current_user()
            if not current_user:
                return {
                    'success': False,
                    'message': '无法获取当前用户信息'
                }

            # 更新任务状态为申诉待审核
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_data = {
                'status': '申诉待审核',
                'current_handler_role': '超级管理员/区域调度员',
                'current_handler_user_id': None,
                'appeal_submitted_at': now_str,
                'appeal_reason': appeal_data.get('appeal_reason', ''),
                'appeal_photos': appeal_data.get('appeal_photos', [])
            }

            DispatchService.update_task(task_id, update_data)

            # 记录申诉状态历史
            appeal_reason = appeal_data.get("appeal_reason", "")
            appeal_description = appeal_data.get("appeal_description", "")
            
            # 构建完整的申诉信息
            appeal_info_parts = []
            if appeal_reason:
                # 将申诉原因代码转换为中文描述
                reason_map = {
                    'downgrade_error': '降档操作有误',
                    'merge_calculation_error': '合并吨位计算错误', 
                    'volume_mismatch': '实际容积与记录不符',
                    'other': '其他原因'
                }
                reason_text = reason_map.get(appeal_reason, appeal_reason)
                appeal_info_parts.append(f"申诉原因：{reason_text}")
            
            if appeal_description:
                appeal_info_parts.append(f"申诉说明：{appeal_description}")
            
            appeal_info = "；".join(appeal_info_parts) if appeal_info_parts else "无详细信息"
            
            status_history_data = {
                'previous_status': '待确认',
                'new_status': '申诉待审核',
                'changed_by': getattr(current_user, 'id', None),
                'changed_at': datetime.now(),
                'comment': f'供应商提交申诉。{appeal_info}',
                'next_handler_role': '超级管理员/区域调度员'
            }

            DispatchService.update_task_status(task_id, '申诉待审核', status_history_data)

            return {
                'success': True,
                'data': {
                    'task_id': task_id,
                    'status': '申诉待审核',
                    'appeal_submitted_by': getattr(current_user, 'id', None),
                    'appeal_submitted_at': now_str,
                    'appeal_reason': update_data['appeal_reason']
                },
                'message': '申诉提交成功，等待管理员审核'
            }
        except Exception as e:
            logger.error(f'提交申诉失败: {str(e)}')
            return {
                'success': False,
                'message': f'提交申诉失败: {str(e)}'
            }