"""
模型包初始化文件
导出所有数据模型类
"""

from .user import User
from .company import Company
from .role import Role
from .user_role import user_role
from .task import ManualDispatchTask
from .vehicle.vehicle import Vehicle
from .dispatch_status_history import DispatchStatusHistory
from .vehicle.vehicle_capacity_reference import VehicleCapacityReference
# 权限相关模型
from .permission import Permission
from .menu import Menu
from .role_permission import RolePermission
from .menu_permission import MenuPermission
# 调度相关模型
from .dispatch.operation_log import OperationLog

__all__ = [
    'User',
    'Company', 
    'Role',
    'ManualDispatchTask',
    'Vehicle',
    'user_role',
    'DispatchStatusHistory',
    'VehicleCapacityReference',
    # 权限相关模型
    'Permission',
    'Menu',
    'RolePermission',
    'MenuPermission',
    # 调度相关模型
    'OperationLog'
]