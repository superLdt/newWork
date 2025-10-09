from app.models.task import ManualDispatchTask
from app.models.dispatch_status_history import DispatchStatusHistory
from app.models.dispatch.operation_log import OperationLog
from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_merge_record import VehicleMergeRecord
from app.models.vehicle.vehicle_downgrade_record import VehicleDowngradeRecord
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any
import logging
import uuid
from app.models.company import DispatchUnit
from sqlalchemy import or_
from flask import g, has_request_context # 导入 has_request_context
from app.models.user import User # 导入 User 模型

logger = logging.getLogger(__name__)


class DispatchService:
    """
    派车服务类，处理派车流程相关的数据操作
    """
    
    @staticmethod
    def get_dispatch_task_by_dispatch_number(dispatch_number: str) -> Optional[Dict]:
        """
        根据派车单号获取派车任务信息
        
        Args:
            dispatch_number: 派车单号
            
        Returns:
            Optional[Dict]: 任务信息字典，如果不存在则返回None
        """
        try:
            # 通过关联的车辆表查找任务
            from app.models.vehicle.vehicle import Vehicle
            vehicle = Vehicle.query.filter_by(dispatch_number=dispatch_number).first()
            if not vehicle or not vehicle.task_id:
                return None
            
            task = ManualDispatchTask.query.get(vehicle.task_id)
            if not task:
                return None
            return task.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"根据派车单号获取任务信息失败: {str(e)}")
            raise
    
    @staticmethod
    def _is_large_capacity_vehicle(required_weight: str) -> bool:
        """
        判断是否为大容积车辆（需求吨位>=30吨）
        
        Args:
            required_weight: 需求吨位字符串，如"30吨"
            
        Returns:
            bool: 是否为大容积车辆
        """
        if not required_weight:
            return False
        
        # 提取数字部分
        try:
            weight_num = int(required_weight.replace('吨', '').replace('A', '').replace('B', ''))
            return weight_num >= 30
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def get_task_list(page: int = 1, per_page: int = 10, filters: Optional[Dict] = None) -> Tuple[List[Dict], int]:
        """
        获取派车任务列表
        
        Args:
            page: 页码
            per_page: 每页数量
            filters: 过滤条件
            
        Returns:
            Tuple[List[Dict], int]: 任务列表和总数
        """
        try:
            query_obj = ManualDispatchTask.query
            
            # 权限过滤：根据用户角色和关联单位过滤任务
            current_user = getattr(g, 'current_user', None)
            if current_user:
                user_roles = [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
                
                # 1. 超级管理员和区域调度员：默认排除已完成（当未显式按状态筛选时）
                if '超级管理员' in user_roles or '区域调度员' in user_roles:
                    if not (filters and filters.get('status')):
                        query_obj = query_obj.filter(ManualDispatchTask.status.notin_(['completed', '任务完成', '已完成']))
                
                # 2. 车间地调：仅展示自己创建的任务，或当前处理角色为“车间地调”的任务，排除已完成状态（中英文）
                elif '车间地调' in user_roles:
                    user_id = getattr(current_user, 'id', None)
                    conditions = []
                    # 自己创建的任务
                    if user_id:
                        conditions.append(ManualDispatchTask.initiator_user_id == user_id)
                    # 需要车间地调处理的任务（任何状态，只要当前处理角色是车间地调）
                    conditions.append(ManualDispatchTask.current_handler_role == '车间地调')
                    
                    if conditions:
                        query_obj = query_obj.filter(or_(*conditions))
                        # 默认排除已完成（当未显式按状态筛选时）
                        if not (filters and filters.get('status')):
                            query_obj = query_obj.filter(ManualDispatchTask.status.notin_(['completed', '任务完成', '已完成']))
                    else:
                        query_obj = query_obj.filter(ManualDispatchTask.task_id == None)
                
                # 3. 供应商/班组长/大容积供应商：只展示待响应、待确认环节，与账号绑定的派车单位相关的数据（状态中英文兼容）
                elif any(role in user_roles for role in ['供应商', '班组长', '大容积供应商']):
                    unit_id = getattr(current_user, 'dispatch_unit_id', None)
                    if unit_id:
                        # 基础过滤条件：单位和状态
                        base_conditions = (
                            (ManualDispatchTask.organizing_unit_id == unit_id) &
                            (ManualDispatchTask.status.in_(['awaiting_response', 'awaiting_confirmation', '待响应', '待确认']))
                        )
                        
                        # 根据角色添加业务类型过滤
                        if '供应商' in user_roles and '大容积供应商' not in user_roles:
                            # 普通供应商只能看委办派车
                            query_obj = query_obj.filter(
                                base_conditions &
                                (ManualDispatchTask.business_type == '委办派车')
                            )
                        elif '大容积供应商' in user_roles and '供应商' not in user_roles:
                            # 大容积供应商只能看大容积派车
                            query_obj = query_obj.filter(
                                base_conditions &
                                (ManualDispatchTask.business_type == '大容积派车')
                            )
                        elif '班组长' in user_roles:
                            # 班组长可以看所有类型的派车任务
                            query_obj = query_obj.filter(base_conditions)
                        else:
                            # 如果同时拥有供应商和大容积供应商角色，可以看委办派车和大容积派车
                            query_obj = query_obj.filter(
                                base_conditions &
                                (ManualDispatchTask.business_type.in_(['委办派车', '大容积派车']))
                            )
                    else:
                        # 如果没有绑定单位，返回空结果
                        query_obj = query_obj.filter(ManualDispatchTask.task_id == None)
                
                # 4. 其他角色：保持原有逻辑但排除已完成状态（中英文）
                else:
                    unit_id = getattr(current_user, 'dispatch_unit_id', None)
                    unit_name = None
                    if unit_id:
                        try:
                            unit_obj = DispatchUnit.query.get(unit_id)
                            unit_name = unit_obj.name if unit_obj else None
                        except Exception:
                            unit_name = None
                    conditions = []
                    if unit_id:
                        conditions.append(ManualDispatchTask.organizing_unit_id == unit_id)
                    # 允许本人发起的任务可见
                    conditions.append(ManualDispatchTask.initiator_user_id == getattr(current_user, 'id', None))
                    # 允许本单位发起（名称匹配）
                    if unit_name:
                        conditions.append(ManualDispatchTask.initiator_department == unit_name)
                    # 允许当前处理角色匹配用户任一角色
                    if user_roles:
                        conditions.append(ManualDispatchTask.current_handler_role.in_(user_roles))
                    if conditions:
                        query_obj = query_obj.filter(or_(*conditions))
                        # 若未显式按状态筛选，则默认排除已完成（中英文常用写法）
                        if not (filters and filters.get('status')):
                            query_obj = query_obj.filter(ManualDispatchTask.status.notin_(['completed', '任务完成', '已完成']))
                    else:
                        # 如果无任何可用条件，则返回空结果
                        query_obj = query_obj.filter(ManualDispatchTask.task_id == None)
            
            # 全局默认过滤：若未显式按状态筛选，则排除“已完成”任务（中英文）
            if not filters or not filters.get('status'):
                query_obj = query_obj.filter(ManualDispatchTask.status.notin_(['completed', '任务完成', '已完成']))

            # 应用其他过滤条件
            if filters:
                if filters.get('status'):
                    # 兼容中英文状态筛选：当传入中文状态时，映射到英文等价状态；反之亦然
                    status_value = filters['status']
                    status_map = {
                        '待审核': ['pending', '待审核'],
                        '审核通过': ['approved', '审核通过'],
                        '待响应': ['awaiting_response', '待响应'],
                        '已响应': ['responded', '已响应'],
                        '任务完成': ['completed', '任务完成', '已完成'],
                        '已完成': ['completed', '任务完成', '已完成'],
                        '审核拒绝': ['rejected', '审核拒绝']
                    }
                    # 若传入英文状态，则反向查找其中文等价项
                    reverse_map = {
                        'pending': ['pending', '待审核'],
                        'approved': ['approved', '审核通过'],
                        'awaiting_response': ['awaiting_response', '待响应'],
                        'responded': ['responded', '已响应'],
                        'completed': ['completed', '任务完成', '已完成'],
                        'rejected': ['rejected', '审核拒绝']
                    }
                    statuses = status_map.get(status_value) or reverse_map.get(status_value) or [status_value]
                    query_obj = query_obj.filter(ManualDispatchTask.status.in_(statuses))
                if filters.get('business_type'):
                    query_obj = query_obj.filter(ManualDispatchTask.business_type == filters['business_type'])
                if filters.get('mail_route_name'):
                    query_obj = query_obj.filter(ManualDispatchTask.mail_route_name.ilike(f"%{filters['mail_route_name']}%"))
                if filters.get('origin_bureau'):
                    query_obj = query_obj.filter(ManualDispatchTask.origin_bureau.ilike(f"%{filters['origin_bureau']}%"))
                if filters.get('organizing_unit_id'):
                    query_obj = query_obj.filter(ManualDispatchTask.organizing_unit_id == filters['organizing_unit_id'])
                if filters.get('dispatch_track'):
                    query_obj = query_obj.filter(ManualDispatchTask.dispatch_track == filters['dispatch_track'])
            
            pagination = query_obj.order_by(ManualDispatchTask.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            tasks = [task.to_dict() for task in pagination.items]
            return tasks, pagination.total
        except SQLAlchemyError as e:
            logger.error(f"获取派车任务列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[Dict]:
        """
        根据ID获取派车任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict]: 任务信息字典，如果不存在则返回None
        """
        try:
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                return None
            return task.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取派车任务信息失败: {str(e)}")
            raise
    
    @staticmethod
    def create_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建派车任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict: 创建结果
        """
        from app.models.task import ManualDispatchTask
        from datetime import datetime
        import uuid
        
        try:
            # 生成任务ID
            task_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6]}"
            
            # 创建任务对象
            task = ManualDispatchTask(
                task_id=task_data.get('task_id', task_id),
                mail_route_name=task_data.get('mail_route_name', ''),
                required_date=task_data.get('required_date', ''),
                origin_bureau=task_data.get('origin_bureau', ''),
                transport_type=task_data.get('transport_type', ''),
                required_weight=task_data.get('required_weight', ''),
                required_volume=task_data.get('required_volume', 0),
                special_requirements=task_data.get('special_requirements', ''),
                organizing_unit_id=task_data.get('organizing_unit_id'),
                organizing_unit=task_data.get('organizing_unit', ''),
                requirement_type=task_data.get('requirement_type', ''),
                initiator_user_id=task_data.get('initiator_user_id'),
                initiator_department=task_data.get('initiator_department', ''),
                initiator_role=task_data.get('initiator_role', ''),
                status=task_data.get('status', ''),
                current_handler_role=task_data.get('current_handler_role', ''),
                current_handler_user_id=task_data.get('current_handler_user_id'),
                dispatch_track=task_data.get('dispatch_track', ''),
                audit_required=task_data.get('audit_required', False),
                business_type=task_data.get('business_type', '委办派车'),
                created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            db.session.add(task)
            db.session.commit()
            
            return {
                'task_id': task.task_id,
                'status': task.status,
                'current_handler_role': task.current_handler_role,
                'dispatch_track': task.dispatch_track,
                'message': '派车任务创建成功'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_task(task_id: str, update_data: Dict) -> Dict:
        """
        更新派车任务信息
        
        Args:
            task_id: 任务ID
            update_data: 更新数据
            
        Returns:
            Dict: 更新后的任务信息
        """
        try:
            # 获取任务对象
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f"任务ID {task_id} 不存在")
            
            # 更新任务字段
            for key, value in update_data.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # 更新时间
            task.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.session.commit()
            
            return task.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新派车任务失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_task(task_id: str) -> bool:
        """
        删除派车任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 获取任务对象
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                return False
            
            # 删除任务
            db.session.delete(task)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除派车任务失败: {str(e)}")
            raise
    
    @staticmethod
    def create_vehicle(vehicle_data: Dict) -> Dict:
        """
        创建车辆信息
        
        Args:
            vehicle_data: 车辆数据
            
        Returns:
            Dict: 创建的车辆信息
        """
        try:
            # 创建车辆对象
            vehicle = Vehicle(
                task_id=vehicle_data.get('task_id'),
                license_plate=vehicle_data.get('license_plate'),
                carriage_number=vehicle_data.get('carriage_number'),
                vehicle_type=vehicle_data.get('vehicle_type'),
                supplier_id=vehicle_data.get('supplier_id'),
                supplier_type=vehicle_data.get('supplier_type'),
                manifest_number=vehicle_data.get('manifest_number'),
                dispatch_number=vehicle_data.get('dispatch_number'),
                actual_volume=vehicle_data.get('actual_volume'),
                required_volume=vehicle_data.get('required_volume'),
                status='已分配',
                created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # 保存到数据库
            db.session.add(vehicle)
            db.session.commit()
            
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def get_task_status_history(task_id: str) -> List[Dict]:
        """
        获取任务状态历史
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[Dict]: 状态历史列表
        """
        try:
            # 查询状态历史记录
            history_records = DispatchStatusHistory.query.filter_by(task_id=task_id).order_by(DispatchStatusHistory.timestamp).all()
            
            # 转换为字典列表
            history_list = [record.to_dict() for record in history_records]
            
            return history_list
        except SQLAlchemyError as e:
            logger.error(f"获取任务状态历史失败: {str(e)}")
            raise
    
    @staticmethod
    def get_task_operation_logs(task_id: str) -> List[Dict]:
        """
        获取任务操作日志
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[Dict]: 操作日志列表
        """
        try:
            # 查询操作日志记录
            log_records = OperationLog.query.filter_by(task_id=task_id).order_by(OperationLog.operation_time).all()
            
            # 转换为字典列表
            log_list = [record.to_dict() for record in log_records]
            
            return log_list
        except SQLAlchemyError as e:
            logger.error(f"获取任务操作日志失败: {str(e)}")
            raise
    
    @staticmethod
    def merge_vehicles(source_vehicle_id: int, target_vehicle_id: int) -> Dict:
        """
        合并车辆信息
        
        Args:
            source_vehicle_id: 源车辆ID
            target_vehicle_id: 目标车辆ID
            
        Returns:
            Dict: 合并结果
        """
        try:
            # 获取源车辆和目标车辆
            source_vehicle = Vehicle.query.get(source_vehicle_id)
            target_vehicle = Vehicle.query.get(target_vehicle_id)
            
            if not source_vehicle or not target_vehicle:
                raise ValueError("源车辆或目标车辆不存在")
            
            # 创建合并记录
            merge_record = VehicleMergeRecord(
                source_vehicle_id=source_vehicle_id,
                target_vehicle_id=target_vehicle_id,
                merge_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                source_license_plate=source_vehicle.license_plate,
                target_license_plate=target_vehicle.license_plate,
                source_data=source_vehicle.to_dict()
            )
            
            # 保存合并记录
            db.session.add(merge_record)
            
            # 更新目标车辆信息
            if not target_vehicle.actual_volume and source_vehicle.actual_volume:
                target_vehicle.actual_volume = source_vehicle.actual_volume
            
            if not target_vehicle.driver_name and source_vehicle.driver_name:
                target_vehicle.driver_name = source_vehicle.driver_name
                target_vehicle.driver_phone = source_vehicle.driver_phone
                target_vehicle.driver_id_card = source_vehicle.driver_id_card
            
            # 标记源车辆为已合并状态
            source_vehicle.status = '已合并'
            source_vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.session.commit()
            
            return merge_record.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"合并车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def downgrade_vehicle(vehicle_id: int, new_type: str) -> Dict:
        """
        车辆降档
        
        Args:
            vehicle_id: 车辆ID
            new_type: 新车型
            
        Returns:
            Dict: 降档结果
        """
        try:
            # 获取车辆
            vehicle = Vehicle.query.get(vehicle_id)
            
            if not vehicle:
                raise ValueError("车辆不存在")
            
            # 记录原车型
            old_type = vehicle.vehicle_type
            
            # 创建降档记录
            downgrade_record = VehicleDowngradeRecord(
                vehicle_id=vehicle_id,
                original_type=old_type,
                new_type=new_type,
                downgrade_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                license_plate=vehicle.license_plate
            )
            
            # 保存降档记录
            db.session.add(downgrade_record)
            
            # 更新车辆类型
            vehicle.vehicle_type = new_type
            vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.session.commit()
            
            return downgrade_record.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"车辆降档失败: {str(e)}")
            raise
    
    @staticmethod
    def update_task_status(task_id: str, new_status: str, status_history_data: Optional[Dict] = None) -> Dict:
        """
        更新任务状态并记录状态历史
        
        Args:
            task_id: 任务ID
            new_status: 新状态
            status_history_data: 状态历史数据（可选）
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 获取任务
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 更新任务状态
            old_status = task.status
            task.status = new_status
            task.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果提供了状态历史数据，则创建状态历史记录
            if status_history_data:
                # 计算并规范字段映射
                prev_status = status_history_data.get('previous_status')
                new_stat = status_history_data.get('new_status', new_status)
                changed_by = status_history_data.get('changed_by')
                changed_at = status_history_data.get('changed_at')
                comment = status_history_data.get('comment')
                next_handler_role = status_history_data.get('next_handler_role')

                # 若提供了下一阶段处理角色，则同步更新到任务当前处理角色
                if next_handler_role:
                    task.current_handler_role = next_handler_role

                # 构造历史记录字段（与模型字段一致）
                status_change_text = f"{prev_status} -> {new_stat}" if prev_status else str(new_stat)
                # operator 使用可读字符串；若只有ID则使用 ID:<id>
                operator_str = None
                if changed_by is not None:
                    # 尝试从 User 模型获取 full_name
                    user = User.query.get(changed_by)
                    if user and user.full_name:
                        operator_str = user.full_name
                    else:
                        operator_str = f"ID:{changed_by}"
                else:
                    try:
                        # 允许在 Flask 环境下读取 g.current_user 作为补充
                        if has_request_context() and hasattr(g, 'current_user') and g.current_user:
                            operator_str = (
                                getattr(g.current_user, 'full_name', None)
                                or getattr(g.current_user, 'username', None)
                                or f"ID:{getattr(g.current_user, 'id', '系统')}"
                            )
                    except Exception:
                        operator_str = None
                if not operator_str:
                    operator_str = '系统'

                # timestamp 统一为字符串
                try:
                    timestamp_str = changed_at.strftime('%Y-%m-%d %H:%M:%S') if changed_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                status_history = DispatchStatusHistory(
                    task_id=task_id,
                    status_change=status_change_text,
                    operator=operator_str,
                    timestamp=timestamp_str,
                    note=comment,
                    next_handler_role=next_handler_role
                )

                # 保存到数据库
                db.session.add(status_history)
            
            db.session.commit()
            
            return {
                'task_id': task_id,
                'old_status': old_status,
                'new_status': new_status,
                'updated_at': task.updated_at
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新任务状态失败: {str(e)}")
            raise

    # 添加别名方法和缺失方法，用于与控制器及业务层命名对齐
    
    @staticmethod
    def get_dispatch_task_list(page: int = 1, per_page: int = 10, filters: Optional[Dict] = None) -> Tuple[List[Dict], int]:
        """
        获取派车任务列表（控制器调用的别名方法）
        """
        return DispatchService.get_task_list(page, per_page, filters)
    
    @staticmethod
    def get_dispatch_task_by_id(task_id: str) -> Optional[Dict]:
        """
        根据ID获取派车任务信息（控制器调用的别名方法）
        """
        return DispatchService.get_task_by_id(task_id)
    
    @staticmethod
    def update_dispatch_task(task_id: str, update_data: Dict) -> Dict:
        """
        更新派车任务信息（控制器调用的别名方法）
        """
        return DispatchService.update_task(task_id, update_data)
    
    @staticmethod
    def create_dispatch_task(task_data: Dict) -> Dict:
        """
        创建新派车任务（控制器调用的别名方法）
        """
        return DispatchService.create_task(task_data)
    
    @staticmethod
    def assign_vehicle_to_task(task_id: str, vehicle_data: Dict) -> Dict:
        """
        为任务分配车辆
        
        Args:
            task_id: 任务ID
            vehicle_data: 车辆数据（包含车辆ID、司机信息等）
            
        Returns:
            Dict: 分配结果
        """
        try:
            # 检查任务是否存在
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 获取或创建车辆
            vehicle_id = vehicle_data.get('vehicle_id')
            if vehicle_id:
                # 使用已有车辆
                vehicle = Vehicle.query.get(vehicle_id)
                if not vehicle:
                    raise ValueError(f"车辆不存在: {vehicle_id}")
                
                # 更新车辆信息
                vehicle.task_id = task_id
                vehicle.driver_name = vehicle_data.get('driver_name', vehicle.driver_name)
                vehicle.driver_phone = vehicle_data.get('driver_phone', vehicle.driver_phone)
                vehicle.status = '已分配'
                vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                # 创建新车辆
                vehicle_data['task_id'] = task_id
                vehicle = DispatchService.create_vehicle(vehicle_data)
                return vehicle
            
            db.session.commit()
            
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"分配车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Dict]:
        """
        根据ID获取车辆信息
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            Optional[Dict]: 车辆信息字典，如果不存在则返回None
        """
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return None
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def add_operation_log(log_data: Dict) -> Dict:
        """
        添加操作日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            Dict: 创建的日志记录
        """
        try:
            # 创建操作日志对象
            operation_log = OperationLog(
                task_id=log_data.get('task_id'),
                action_type=log_data.get('action_type'),
                action_name=log_data.get('action_name'),
                details=log_data.get('details'),
                user_id=log_data.get('user_id'),
                created_at=log_data.get('created_at', datetime.now())
            )
            
            # 保存到数据库
            db.session.add(operation_log)
            db.session.commit()
            
            return operation_log.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"添加操作日志失败: {str(e)}")
            raise

    @staticmethod
    def add_status_history(history_data: Dict) -> Dict:
        """
        添加状态历史记录
        
        Args:
            history_data: 状态历史数据
            
        Returns:
            Dict: 创建的状态历史记录
        """
        try:
            # 创建状态历史对象
            status_history = DispatchStatusHistory(
                task_id=history_data.get('task_id'),
                status_change=history_data.get('status_change'),
                operator=history_data.get('operator'),
                timestamp=history_data.get('timestamp'),
                note=history_data.get('note'),
                next_handler_role=history_data.get('next_handler_role')
            )
            
            # 保存到数据库
            db.session.add(status_history)
            db.session.commit()
            
            return status_history.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"添加状态历史记录失败: {str(e)}")
            raise