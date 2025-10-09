"""
超级管理员/区域调度员相关业务逻辑模块

处理派车任务创建、审核、分配等管理操作
"""

from datetime import datetime
from flask_jwt_extended import get_current_user
from app.extensions import db
from app.models.task import ManualDispatchTask
from app.models.dispatch_status_history import DispatchStatusHistory
from app.business.dispatch.base_business import BaseDispatchBusiness
from app.business.dispatch.status_manager import DispatchStatusManager
from app.services.dispatch.dispatch_service import DispatchService  # 添加导入
from typing import Dict, Any, List

class AdminDispatchBusiness(BaseDispatchBusiness):
    """超级管理员/区域调度员派车业务逻辑类"""
    
    @staticmethod
    def create_dispatch_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建派车任务（轨道B流程 - 直接派车，无需审核）
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict: 创建结果
        """
        try:
            current_user = get_current_user()
            
            # 获取用户角色名称
            user_roles = [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
            user_role = '超级管理员/区域调度员' if any(role in ['超级管理员', '区域调度员'] for role in user_roles) else (user_roles[0] if user_roles else '未知角色')
            
            # 生成任务ID
            import uuid
            task_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6]}"
            
            # 准备任务数据
            task_data_prepared = {
                'task_id': task_id,
                'mail_route_name': task_data.get('mail_route_name', ''),
                'required_date': task_data.get('required_date', ''),
                'origin_bureau': task_data.get('origin_bureau', ''),
                'organizing_unit': task_data.get('organizing_unit', ''),
                'organizing_unit_id': task_data.get('organizing_unit_id'),
                'transport_type': task_data.get('transport_type', ''),
                'requirement_type': task_data.get('requirement_type', ''),
                'required_weight': task_data.get('required_weight', ''),
                'required_volume': task_data.get('required_volume', 0),
                'special_requirements': task_data.get('special_requirements', ''),
                'status': '待响应',  # 超级管理员/区域调度员创建的任务直接进入待响应状态
                'dispatch_track': '轨道B',  # 超级管理员/区域调度员创建的任务走轨道B
                'initiator_role': '超级管理员/区域调度员',
                'initiator_user_id': current_user.id,
                'initiator_department': task_data.get('initiator_department') or BaseDispatchBusiness._get_user_department_name(current_user.id),
                'audit_required': False,  # 不需要审核
                'current_handler_role': BaseDispatchBusiness._get_next_handler_role_by_business_type(task_data.get('business_type')),  # 根据业务类型设置当前处理人角色
                'current_handler_user_id': current_user.id,  # 设置当前处理用户ID
                'business_type': task_data.get('business_type', '自办派车')  # 从传入参数读取业务类型
            }
            
            # 调用服务层创建任务
            result = DispatchService.create_dispatch_task(task_data_prepared)
            
            # 记录状态历史（使用服务层方法）
            operator_name = (getattr(current_user, 'full_name', None) or 
                           getattr(current_user, 'username', None) or 
                           f"ID:{getattr(current_user, 'id', '系统')}")
            
            status_history_data = {
                'task_id': task_id,
                'status_change': '创建任务',
                'operator': operator_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': f'超级管理员/区域调度员创建派车任务：{task_data_prepared["mail_route_name"]}（轨道B流程 - 直接派车）',
                'next_handler_role': BaseDispatchBusiness._get_next_handler_role_by_business_type(task_data.get('business_type'))
            }
            
            # 调用服务层记录状态历史
            DispatchService.add_status_history(status_history_data)
            
            # 记录操作日志
            BaseDispatchBusiness._log_task_action(
                task_id=task_id,
                action_type='create',
                details={
                    'route_name': task_data.get('mail_route_name', ''),
                    'initiator_role': '超级管理员/区域调度员',
                    'status': '待响应'
                }
            )
            
            return AdminDispatchBusiness._ok(f'创建派车任务成功，任务ID：{task_id}，已分配给{user_role}处理')
            
        except Exception as e:
            db.session.rollback()
            return AdminDispatchBusiness._error(f'创建派车任务失败：{str(e)}')
    
    @staticmethod
    def review_dispatch_task(task_id: int, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        审核派车任务
        
        Args:
            task_id: 任务ID
            review_data: 审核数据
            
        Returns:
            Dict: 审核结果
        """
        try:
            current_user = get_current_user()
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f'未找到ID为{task_id}的派车任务')
            
            if task.status not in ['待审核', '待确认']:
                raise ValueError(f'当前任务状态为{task.status}，不能进行审核操作')
            
            review_result = review_data.get('review_result')
            remarks = review_data.get('remarks', '')
            
            # 将审核结果规范为受支持的状态并更新
            if review_result == 'approve':
                new_status = '待响应'
            elif review_result in ('reject', 'return'):
                # 退回按审核拒绝处理，需业务方后续重新提交
                new_status = '审核拒绝'
            else:
                raise ValueError(f'不支持的审核结果：{review_result}')
            
            # 使用状态管理器更新任务状态（内部将完成合法性校验与状态历史记录）
            update_result = DispatchStatusManager.update_task_status(
                task_id=str(task_id),
                new_status=new_status,
                comment=f'审核意见：{remarks}'
            )
            
            # 返回成功结果（服务层已提交事务）
            return {
                'valid': True,
                'task_id': task_id,
                'old_status': update_result.get('old_status'),
                'status': update_result.get('new_status'),
                'message': f'派车任务审核{"通过" if review_result == "approve" else "拒绝"}'
            }
            
            
            
                        
        except Exception as e:
            db.session.rollback()
            return AdminDispatchBusiness._error(f'审核派车任务失败：{str(e)}')

    # @staticmethod
    # def assign_dispatch_task(task_id: int, assign_data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     分配派车任务
    #
    #     Args:
    #         task_id: 任务ID
    #         assign_data: 分配数据
    #
    #     Returns:
    #         Dict: 分配结果
    #     """
    #     try:
    #         current_user = get_current_user()
    #         task = ManualDispatchTask.query.get(task_id)
    #         if not task:
    #             raise ValueError(f'未找到ID为{task_id}的派车任务')
    #
    #         if task.status != '待分配':
    #             raise ValueError(f'当前任务状态为{task.status}，不能进行分配操作')
    #
    #         assignee_role = assign_data.get('assignee_role', '车间地调')
    #         assignee_id = assign_data.get('assignee_id')
    #         assignee_name = assign_data.get('assignee_name', '')
    #         remarks = assign_data.get('remarks', '')
    #
    #         # 更新任务状态和处理人
    #         task.status = '待车间核查'
    #         task.current_handler_role = assignee_role
    #         task.current_handler_id = assignee_id
    #         task.updated_at = datetime.now()
    #
    #         # 记录状态历史
    #         status_history = DispatchStatusHistory(
    #             task_id=task_id,
    #             status_change='任务分配',
    #             operator=(getattr(current_user, 'full_name', None) or
    #                      getattr(current_user, 'username', None) or
    #                      f"ID:{getattr(current_user, 'id', '系统')}"),
    #             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #             note=f'分配给{assignee_role}（{assignee_name}）：{remarks}',
    #             next_handler_role=assignee_role
    #         )
    #         db.session.add(status_history)
    #
    #         # 提交事务
    #         db.session.commit()
    #
    #         return {
    #             'task_id': task_id,
    #             'status': task.status,
    #             'current_handler_role': task.current_handler_role,
    #             'current_handler_id': task.current_handler_id,
    #             'message': f'派车任务分配给{assignee_role}（{assignee_name}）成功'
    #         }
    #
    #     except Exception as e:
    #         db.session.rollback()
    #         raise e
    
    @staticmethod
    def cancel_dispatch_task(task_id: int, cancel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        取消派车任务
        
        Args:
            task_id: 任务ID
            cancel_data: 取消数据
            
        Returns:
            Dict: 取消结果
        """
        try:
            current_user = get_current_user()
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f'未找到ID为{task_id}的派车任务')
            
            if task.status in ['已完成', '已取消']:
                raise ValueError(f'当前任务状态为{task.status}，不能进行取消操作')
            
            cancel_reason = cancel_data.get('cancel_reason', '')
            
            # 使用状态管理器更新任务状态
            DispatchStatusManager.update_task_status(
                task_id=str(task_id),
                new_status='已取消',
                comment=f'取消原因：{cancel_reason}'
            )
            
            # 状态历史记录已在DispatchStatusManager.update_task_status中处理
            # 这里不再重复记录
            
            # 提交事务
            db.session.commit()
            
            return {
                'task_id': task_id,
                'status': '已取消',
                'message': '派车任务取消成功'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e