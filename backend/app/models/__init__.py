"""
模型包初始化文件
导出所有数据模型类
"""

from .user import User
from .company import Company
from .role import Role
from .user_role import user_role
from .task import ManualDispatchTask
from .vehicle import Vehicle
from .dispatch_status_history import DispatchStatusHistory
from .vehicle_capacity_reference import VehicleCapacityReference

__all__ = [
    'User',
    'Company', 
    'Role',
    'ManualDispatchTask',
    'Vehicle',
    'DispatchStatusHistory',
    'VehicleCapacityReference'
]