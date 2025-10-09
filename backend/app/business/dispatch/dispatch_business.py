"""
派车流程业务逻辑模块

处理派车流程相关的业务规则和验证逻辑，位于应用层
"""

from datetime import datetime
from typing import Dict, Any
import logging

from flask_jwt_extended import get_current_user

from app.services.dispatch.dispatch_service import DispatchService
from app.business.dispatch.admin_business import AdminDispatchBusiness
from app.business.dispatch.base_business import BaseDispatchBusiness
from app.business.dispatch.large_supplier_business import LargeSupplierDispatchBusiness
from app.business.dispatch.supplier_business import SupplierDispatchBusiness
from app.business.dispatch.team_business import TeamDispatchBusiness
from app.business.dispatch.workshop_business import WorkshopDispatchBusiness

logger = logging.getLogger(__name__)

class DispatchBusiness(BaseDispatchBusiness):
    """
    派车业务逻辑类
    
    负责协调各个角色的业务逻辑，提供统一的业务接口
    继承自BaseDispatchBusiness，实现通用的派车流程管理
    """

    # ==================== 任务验证方法 ====================
    
    @staticmethod
    def validate_task_creation(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证任务创建数据
        
        Args:
            data: 任务创建数据
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 检查必需字段
            required_fields = ['mail_route_name', 'required_date', 'origin_bureau']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'valid': False,
                        'message': f'缺少必需字段: {field}'
                    }
            
            # 验证日期格式
            try:
                datetime.strptime(data['required_date'], '%Y-%m-%d')
            except ValueError:
                return {
                    'valid': False,
                    'message': '需求日期格式不正确，应为 YYYY-MM-DD'
                }
            
            return {
                'valid': True,
                'message': '验证通过'
            }
        except Exception as e:
            logger.error(f'验证任务创建数据失败: {str(e)}')
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }

    @staticmethod
    def validate_task_update(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证任务更新数据
        
        Args:
            task_id: 任务ID
            data: 任务更新数据
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'valid': False,
                    'message': '任务不存在'
                }
            
            # 如果有日期字段，验证日期格式
            if 'required_date' in data:
                try:
                    datetime.strptime(data['required_date'], '%Y-%m-%d')
                except ValueError:
                    return {
                        'valid': False,
                        'message': '需求日期格式不正确，应为 YYYY-MM-DD'
                    }
            
            return {
                'valid': True,
                'message': '验证通过'
            }
        except Exception as e:
            logger.error(f'验证任务更新数据失败: {str(e)}')
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }

    @staticmethod
    def validate_task_approval(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证任务审批数据
        
        Args:
            task_id: 任务ID
            data: 审批数据
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'valid': False,
                    'message': '任务不存在'
                }
            
            # 检查审批状态（兼容多种字段：approved / review_result / approval_status）
            has_approved_flag = 'approved' in data
            has_review_result = 'review_result' in data
            has_approval_status = 'approval_status' in data
            if not (has_approved_flag or has_review_result or has_approval_status):
                return {
                    'valid': False,
                    'message': '缺少审批状态（支持字段：approved/review_result/approval_status）'
                }
            
            return {
                'valid': True,
                'message': '验证通过'
            }
        except Exception as e:
            logger.error(f'验证任务审批数据失败: {str(e)}')
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }

    @staticmethod
    def validate_vehicle_assignment(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证车辆分配数据
        
        Args:
            task_id: 任务ID
            data: 车辆分配数据
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'valid': False,
                    'message': '任务不存在'
                }
            
            # 检查车辆ID
            if 'vehicle_id' not in data:
                return {
                    'valid': False,
                    'message': '缺少车辆ID'
                }
            
            return {
                'valid': True,
                'message': '验证通过'
            }
        except Exception as e:
            logger.error(f'验证车辆分配数据失败: {str(e)}')
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }

    @staticmethod
    def validate_task_completion(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证任务完成数据
        
        Args:
            task_id: 任务ID
            data: 任务完成数据
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 检查任务是否存在
            task = DispatchService.get_dispatch_task_by_id(task_id)
            if not task:
                return {
                    'valid': False,
                    'message': '任务不存在'
                }
            
            return {
                'valid': True,
                'message': '验证通过'
            }
        except Exception as e:
            logger.error(f'验证任务完成数据失败: {str(e)}')
            return {
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }

    # ==================== 角色响应验证方法 ====================
    
    @staticmethod
    def validate_supplier_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证供应商响应数据"""
        return SupplierDispatchBusiness.validate_supplier_response_data(data)

    @staticmethod
    def process_supplier_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """处理供应商响应"""
        return SupplierDispatchBusiness.process_supplier_response(data)

    @staticmethod
    def validate_team_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证班组响应数据"""
        return TeamDispatchBusiness.validate_team_response_data(data)

    @staticmethod
    def process_team_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """处理班组响应"""
        return TeamDispatchBusiness.process_team_response(data)

    @staticmethod
    def validate_large_capacity_supplier_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证大容积供应商响应数据"""
        return LargeSupplierDispatchBusiness.validate_large_capacity_supplier_response_data(data)

    @staticmethod
    def validate_outsourcing_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证外包响应数据"""
        return LargeSupplierDispatchBusiness.validate_outsourcing_response_data(data)

    @staticmethod
    def process_large_capacity_supplier_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """处理大容积供应商响应"""
        return LargeSupplierDispatchBusiness.process_large_capacity_supplier_response(data)

    @staticmethod
    def process_workshop_verification(task_id: int, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理车间核实"""
        return WorkshopDispatchBusiness.process_workshop_verification(task_id, verification_data)

    # ==================== 任务流程管理方法 ====================
    
    @staticmethod
    def create_dispatch_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建派车任务（根据当前用户角色选择轨道A或轨道B）"""
        try:
            current_user = get_current_user()
            user_roles = [role.name for role in getattr(current_user, 'roles', [])] if current_user else []

            # 车间地调走轨道A（需审核）
            if '车间地调' in user_roles:
                return WorkshopDispatchBusiness.create_dispatch_task(task_data)

            # 超级管理员/区域调度员走轨道B（直接派车）
            if any(role in ['超级管理员', '区域调度员'] for role in user_roles):
                return AdminDispatchBusiness.create_dispatch_task(task_data)

            # 其他角色默认按管理侧创建（若无权限由装饰器拦截）
            return AdminDispatchBusiness.create_dispatch_task(task_data)
        except Exception as e:
            return AdminDispatchBusiness._error(f'创建派车任务失败：{str(e)}')

    @staticmethod
    def review_dispatch_task(task_id: int, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """审核派车任务"""
        return AdminDispatchBusiness.review_dispatch_task(task_id, review_data)

    @staticmethod
    def process_task_approval(task_id: int, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务审批（统一参数并调用审核方法）"""
        try:
            # 归一化审批结果
            comment = approval_data.get('comment') or approval_data.get('remarks', '')
            review_result: str = ''
            
            if 'approved' in approval_data:
                review_result = 'approve' if bool(approval_data.get('approved')) else 'reject'
            elif 'review_result' in approval_data:
                review_result = str(approval_data.get('review_result'))
            elif 'approval_status' in approval_data:
                status = str(approval_data.get('approval_status')).lower()
                if status in ('approved', 'approve', 'pass', '通过'):
                    review_result = 'approve'
                elif status in ('rejected', 'reject', 'fail', '拒绝'):
                    review_result = 'reject'
                elif status in ('returned', 'return', '退回'):
                    review_result = 'return'
                else:
                    return BaseDispatchBusiness._error(f'不支持的审批状态：{approval_data.get("approval_status")}')
            else:
                return BaseDispatchBusiness._error('缺少审批状态（approved/review_result/approval_status）')

            # 调用统一的审核方法
            return AdminDispatchBusiness.review_dispatch_task(task_id, {
                'review_result': review_result,
                'remarks': comment or ''
            })
        except Exception as e:
            return BaseDispatchBusiness._error(f'处理任务审批失败：{str(e)}')

    @staticmethod
    def assign_dispatch_task(task_id: int, assign_data: Dict[str, Any]) -> Dict[str, Any]:
        """分配派车任务"""
        return AdminDispatchBusiness.assign_dispatch_task(task_id, assign_data)

    @staticmethod
    def cancel_dispatch_task(task_id: int, cancel_data: Dict[str, Any]) -> Dict[str, Any]:
        """取消派车任务"""
        return AdminDispatchBusiness.cancel_dispatch_task(task_id, cancel_data)