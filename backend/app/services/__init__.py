"""
服务层模块初始化
统一暴露所有业务服务接口
"""

from .auth_service import AuthService
from .user_service import UserService
from .dispatch_unit_service import DispatchUnitService
from .role_service import RoleService
from .permission_cache_service import PermissionCacheService
# 权限相关服务
from .permission_service import PermissionService
from .menu_service import MenuService
from .role_permission_service import RolePermissionService
from .vehicle.vehicle_service import VehicleService
from .user_management_service import UserManagementService

__all__ = [
    'AuthService',
    'UserService', 
    'DispatchUnitService',
    'RoleService',
    'VehicleService',
    'PermissionCacheService',
    'UserManagementService',
    # 权限相关服务
    'PermissionService',
    'MenuService',
    'RolePermissionService'
]