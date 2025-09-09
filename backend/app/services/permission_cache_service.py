# -*- coding: utf-8 -*-
"""
权限缓存服务模块
提供权限信息的缓存机制以提升查询性能
"""

import json
import time
from typing import List, Optional, Dict, Any, Set
from functools import wraps
from ..extensions import db
from ..models import User, Role, Permission, Menu


class PermissionCacheService:
    """
    权限缓存服务类
    使用内存缓存来提升权限查询性能
    """
    
    # 缓存存储
    _cache = {}
    
    # 缓存配置
    CACHE_TTL = 300  # 缓存过期时间（秒）
    MAX_CACHE_SIZE = 1000  # 最大缓存条目数
    
    # 缓存键前缀
    USER_PERMISSIONS_PREFIX = 'user_permissions:'
    USER_MENUS_PREFIX = 'user_menus:'
    ROLE_PERMISSIONS_PREFIX = 'role_permissions:'
    MENU_TREE_PREFIX = 'menu_tree:'
    PERMISSION_LIST_PREFIX = 'permission_list:'
    
    @classmethod
    def _generate_cache_key(cls, prefix: str, identifier: str) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 缓存键前缀
            identifier: 标识符
            
        Returns:
            str: 缓存键
        """
        return f"{prefix}{identifier}"
    
    @classmethod
    def _is_cache_valid(cls, cache_entry: Dict[str, Any]) -> bool:
        """
        检查缓存条目是否有效
        
        Args:
            cache_entry: 缓存条目
            
        Returns:
            bool: 是否有效
        """
        if not cache_entry:
            return False
        
        current_time = time.time()
        return current_time - cache_entry.get('timestamp', 0) < cls.CACHE_TTL
    
    @classmethod
    def _set_cache(cls, key: str, data: Any) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            data: 缓存数据
        """
        # 如果缓存已满，清理过期条目
        if len(cls._cache) >= cls.MAX_CACHE_SIZE:
            cls._cleanup_expired_cache()
        
        # 如果仍然满了，清理最旧的条目
        if len(cls._cache) >= cls.MAX_CACHE_SIZE:
            cls._cleanup_oldest_cache()
        
        cls._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    @classmethod
    def _get_cache(cls, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存数据或None
        """
        cache_entry = cls._cache.get(key)
        
        if not cls._is_cache_valid(cache_entry):
            # 缓存无效，删除
            if key in cls._cache:
                del cls._cache[key]
            return None
        
        return cache_entry['data']
    
    @classmethod
    def _delete_cache(cls, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        if key in cls._cache:
            del cls._cache[key]
    
    @classmethod
    def _cleanup_expired_cache(cls) -> None:
        """
        清理过期的缓存条目
        """
        current_time = time.time()
        expired_keys = []
        
        for key, entry in cls._cache.items():
            if current_time - entry.get('timestamp', 0) >= cls.CACHE_TTL:
                expired_keys.append(key)
        
        for key in expired_keys:
            del cls._cache[key]
    
    @classmethod
    def _cleanup_oldest_cache(cls) -> None:
        """
        清理最旧的缓存条目（LRU策略）
        """
        if not cls._cache:
            return
        
        # 找到最旧的条目
        oldest_key = min(cls._cache.keys(), 
                         key=lambda k: cls._cache[k].get('timestamp', 0))
        del cls._cache[oldest_key]
    
    @classmethod
    def get_user_permissions(cls, user_id: int, use_cache: bool = True) -> List[str]:
        """
        获取用户权限代码列表（带缓存）
        
        Args:
            user_id: 用户ID
            use_cache: 是否使用缓存
            
        Returns:
            list: 权限代码列表
        """
        cache_key = cls._generate_cache_key(cls.USER_PERMISSIONS_PREFIX, str(user_id))
        
        # 尝试从缓存获取
        if use_cache:
            cached_data = cls._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # 从数据库查询
        user = User.query.get(user_id)
        if not user or not user.is_active:
            permissions = []
        else:
            permissions = user.get_permission_codes()
        
        # 设置缓存
        if use_cache:
            cls._set_cache(cache_key, permissions)
        
        return permissions
    
    @classmethod
    def get_user_menus(cls, user_id: int, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        获取用户可访问的菜单树（带缓存）
        
        Args:
            user_id: 用户ID
            use_cache: 是否使用缓存
            
        Returns:
            list: 菜单树结构
        """
        from .menu_service import MenuService
        
        cache_key = cls._generate_cache_key(cls.USER_MENUS_PREFIX, str(user_id))
        
        # 尝试从缓存获取
        if use_cache:
            cached_data = cls._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # 从数据库查询
        menus = MenuService.get_user_menus(user_id)
        
        # 设置缓存
        if use_cache:
            cls._set_cache(cache_key, menus)
        
        return menus
    
    @classmethod
    def get_role_permissions(cls, role_id: int, use_cache: bool = True) -> List[str]:
        """
        获取角色权限代码列表（带缓存）
        
        Args:
            role_id: 角色ID
            use_cache: 是否使用缓存
            
        Returns:
            list: 权限代码列表
        """
        cache_key = cls._generate_cache_key(cls.ROLE_PERMISSIONS_PREFIX, str(role_id))
        
        # 尝试从缓存获取
        if use_cache:
            cached_data = cls._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # 从数据库查询
        role = Role.query.get(role_id)
        if not role:
            permissions = []
        else:
            permissions = role.get_permission_codes()
        
        # 设置缓存
        if use_cache:
            cls._set_cache(cache_key, permissions)
        
        return permissions
    
    @classmethod
    def get_menu_tree(cls, include_inactive: bool = False, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        获取菜单树结构（带缓存）
        
        Args:
            include_inactive: 是否包含未启用的菜单
            use_cache: 是否使用缓存
            
        Returns:
            list: 菜单树结构
        """
        from .menu_service import MenuService
        
        cache_key = cls._generate_cache_key(cls.MENU_TREE_PREFIX, str(include_inactive))
        
        # 尝试从缓存获取
        if use_cache:
            cached_data = cls._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # 从数据库查询
        menu_tree = MenuService.get_menu_tree(include_inactive)
        
        # 设置缓存
        if use_cache:
            cls._set_cache(cache_key, menu_tree)
        
        return menu_tree
    
    @classmethod
    def check_user_permission(cls, user_id: int, permission_code: str, use_cache: bool = True) -> bool:
        """
        检查用户是否具有指定权限（带缓存）
        
        Args:
            user_id: 用户ID
            permission_code: 权限代码
            use_cache: 是否使用缓存
            
        Returns:
            bool: 是否具有权限
        """
        user_permissions = cls.get_user_permissions(user_id, use_cache)
        return permission_code in user_permissions
    
    @classmethod
    def check_user_menu_access(cls, user_id: int, menu_code: str, use_cache: bool = True) -> bool:
        """
        检查用户是否可以访问指定菜单（带缓存）
        
        Args:
            user_id: 用户ID
            menu_code: 菜单代码
            use_cache: 是否使用缓存
            
        Returns:
            bool: 是否可以访问
        """
        user_menus = cls.get_user_menus(user_id, use_cache)
        
        # 递归检查菜单树
        def check_menu_in_tree(menus, target_code):
            for menu in menus:
                if menu.get('code') == target_code:
                    return True
                if 'children' in menu and check_menu_in_tree(menu['children'], target_code):
                    return True
            return False
        
        return check_menu_in_tree(user_menus, menu_code)
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> None:
        """
        使用户相关缓存失效
        
        Args:
            user_id: 用户ID
        """
        # 删除用户权限缓存
        permissions_key = cls._generate_cache_key(cls.USER_PERMISSIONS_PREFIX, str(user_id))
        cls._delete_cache(permissions_key)
        
        # 删除用户菜单缓存
        menus_key = cls._generate_cache_key(cls.USER_MENUS_PREFIX, str(user_id))
        cls._delete_cache(menus_key)
    
    @classmethod
    def invalidate_role_cache(cls, role_id: int) -> None:
        """
        使角色相关缓存失效
        
        Args:
            role_id: 角色ID
        """
        # 删除角色权限缓存
        permissions_key = cls._generate_cache_key(cls.ROLE_PERMISSIONS_PREFIX, str(role_id))
        cls._delete_cache(permissions_key)
        
        # 删除拥有此角色的用户的缓存
        role = Role.query.get(role_id)
        if role:
            for user in role.users:
                cls.invalidate_user_cache(user.id)
    
    @classmethod
    def invalidate_menu_cache(cls) -> None:
        """
        使菜单相关缓存失效
        """
        # 删除菜单树缓存
        keys_to_delete = []
        for key in cls._cache.keys():
            if key.startswith(cls.MENU_TREE_PREFIX) or key.startswith(cls.USER_MENUS_PREFIX):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            cls._delete_cache(key)
    
    @classmethod
    def invalidate_all_cache(cls) -> None:
        """
        清空所有缓存
        """
        cls._cache.clear()
    
    @classmethod
    def get_cache_statistics(cls) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            dict: 缓存统计信息
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        cache_types = {
            'user_permissions': 0,
            'user_menus': 0,
            'role_permissions': 0,
            'menu_tree': 0,
            'other': 0
        }
        
        for key, entry in cls._cache.items():
            if cls._is_cache_valid(entry):
                valid_entries += 1
            else:
                expired_entries += 1
            
            # 统计缓存类型
            if key.startswith(cls.USER_PERMISSIONS_PREFIX):
                cache_types['user_permissions'] += 1
            elif key.startswith(cls.USER_MENUS_PREFIX):
                cache_types['user_menus'] += 1
            elif key.startswith(cls.ROLE_PERMISSIONS_PREFIX):
                cache_types['role_permissions'] += 1
            elif key.startswith(cls.MENU_TREE_PREFIX):
                cache_types['menu_tree'] += 1
            else:
                cache_types['other'] += 1
        
        return {
            'total_entries': len(cls._cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_types': cache_types,
            'max_cache_size': cls.MAX_CACHE_SIZE,
            'cache_ttl': cls.CACHE_TTL
        }
    
    @classmethod
    def preload_user_cache(cls, user_id: int) -> None:
        """
        预加载用户缓存
        
        Args:
            user_id: 用户ID
        """
        # 预加载用户权限
        cls.get_user_permissions(user_id, use_cache=True)
        
        # 预加载用户菜单
        cls.get_user_menus(user_id, use_cache=True)
    
    @classmethod
    def preload_role_cache(cls, role_id: int) -> None:
        """
        预加载角色缓存
        
        Args:
            role_id: 角色ID
        """
        # 预加载角色权限
        cls.get_role_permissions(role_id, use_cache=True)
    
    @classmethod
    def warmup_cache(cls) -> Dict[str, int]:
        """
        预热缓存（加载常用数据）
        
        Returns:
            dict: 预热统计信息
        """
        stats = {
            'users_loaded': 0,
            'roles_loaded': 0,
            'menu_tree_loaded': 0
        }
        
        # 预加载活跃用户的权限和菜单
        active_users = User.query.filter_by(is_active=True).limit(50).all()
        for user in active_users:
            cls.preload_user_cache(user.id)
            stats['users_loaded'] += 1
        
        # 预加载所有角色的权限
        roles = Role.query.all()
        for role in roles:
            cls.preload_role_cache(role.id)
            stats['roles_loaded'] += 1
        
        # 预加载菜单树
        cls.get_menu_tree(include_inactive=False, use_cache=True)
        cls.get_menu_tree(include_inactive=True, use_cache=True)
        stats['menu_tree_loaded'] = 2
        
        return stats


def cache_permission_result(cache_key_func=None, ttl=None):
    """
    权限结果缓存装饰器
    
    Args:
        cache_key_func: 缓存键生成函数
        ttl: 缓存过期时间
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = PermissionCacheService._get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 设置缓存
            PermissionCacheService._set_cache(cache_key, result)
            
            return result
        
        return wrapper
    return decorator