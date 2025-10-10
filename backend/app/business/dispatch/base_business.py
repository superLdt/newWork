"""
派车流程基础业务逻辑模块

包含所有角色共用的基础业务逻辑和通用方法
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class BaseDispatchBusiness:
    """
    派车流程基础业务逻辑类
    提供所有角色共用的基础方法
    """

    @staticmethod
    def _get_user_department_name(user_id):
        """
        根据用户ID获取用户所属派车单位名称
        
        Args:
            user_id: 用户ID
            
        Returns:
            str: 派车单位名称，如果未找到则返回空字符串
        """
        try:
            from app.models.user import User
            from app.models.company import DispatchUnit
            
            user = User.query.get(user_id)
            if user and user.dispatch_unit_id:
                dispatch_unit = DispatchUnit.query.get(user.dispatch_unit_id)
                if dispatch_unit:
                    return dispatch_unit.name
            return ''
        except Exception:
            return ''

    @staticmethod
    def _log_task_action(task_id: str, action_type: str, details: Dict[str, Any]):
        """
        记录任务操作日志
        
        Args:
            task_id: 任务ID
            action_type: 操作类型
            details: 操作详情
        """
        try:
            from app.business.dispatch.log_manager import DispatchLogManager
            DispatchLogManager.log_action(
                task_id=task_id,
                action_type=action_type,
                details=details
            )
        except Exception:
            pass  # 日志记录失败不应影响主流程

    @staticmethod
    def _get_next_handler_role_by_business_type(business_type: str) -> str:
        """
        根据业务类型确定下一处理人角色
        
        Args:
            business_type: 业务类型（自办派车/委办派车/大容积派车）
            
        Returns:
            str: 下一处理人角色
        """
        bt = (business_type or '').strip()
        if bt == '自办派车':
            return '班组长'
        elif bt == '大容积派车':
            return '大容积供应商'
        elif bt == '委办派车':
            return '供应商'
        else:
            # 默认回退规则
            return '供应商'

    # == 统一的校验结果包装 ==
    @staticmethod
    def _ok(msg: str = 'OK') -> Dict[str, Any]:
        """返回成功的校验结果"""
        return {'valid': True, 'message': msg}
    
    @staticmethod
    def _error(msg: str) -> Dict[str, Any]:
        """返回失败的校验结果"""
        return {'valid': False, 'message': msg}
    
    @staticmethod
    def validate_vehicle_data(vehicles: List[Dict[str, Any]], carriages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证车辆和车厢数据
        
        Args:
            vehicles: 车辆数据列表
            carriages: 车厢数据列表
            
        Returns:
            Dict: 验证结果
        """
        # 计算总的车辆和车厢数量
        total_vehicles = len(vehicles) if vehicles else 0
        total_carriages = len(carriages) if carriages else 0
        total_count = total_vehicles + total_carriages
        
        # 唯一性验证：一个任务只能派遣一辆车或一个车厢
        if total_count == 0:
            return BaseDispatchBusiness._error('至少需要提供一辆车辆或一个车厢信息')
        elif total_count > 1:
            return BaseDispatchBusiness._error('一个任务只能派遣一辆车或一个车厢，不能同时派遣多个')
        
        # 验证车辆信息
        if vehicles:
            for i, vehicle in enumerate(vehicles):
                # 车牌号必填
                if not vehicle.get('license_plate'):
                    return BaseDispatchBusiness._error(f'第{i+1}辆车的车牌号不能为空')
                
                # 车辆类型必填
                if not vehicle.get('vehicle_type'):
                    return BaseDispatchBusiness._error(f'第{i+1}辆车的车辆类型不能为空')
        
        # 验证车厢信息
        if carriages:
            for i, carriage in enumerate(carriages):
                # 车厢号必填
                if not carriage.get('carriage_number'):
                    return BaseDispatchBusiness._error(f'第{i+1}个车厢的车厢号不能为空')
                
                # 车辆类型必填
                if not carriage.get('vehicle_type'):
                    return BaseDispatchBusiness._error(f'第{i+1}个车厢的车辆类型不能为空')
        
        return BaseDispatchBusiness._ok('数据验证通过')