#!/usr/bin/env python3
"""
蓝图自动发现和注册工具模块

提供蓝图自动发现、模块扫描和配置化注册功能，避免硬编码导入。
符合四层架构规范，将表现层组件注册逻辑集中管理。
"""

import importlib
import inspect
import os
import pkgutil
from typing import List, Dict, Any, Optional
from flask import Blueprint


def auto_register_blueprints(app, package_path: str = 'app') -> None:
    """
    自动发现并注册所有蓝图
    
    参数:
        app: Flask应用实例
        package_path: 包路径，默认为'app'
    
    返回:
        None
    """
    blueprints = discover_module_blueprints(package_path)
    
    for bp_info in blueprints:
        register_blueprint_with_config(app, bp_info)


def discover_module_blueprints(package_path: str) -> List[Dict[str, Any]]:
    """
    发现指定包路径下的所有蓝图模块
    
    参数:
        package_path: 包路径，如'app.api'
    
    返回:
        蓝图信息列表，每个元素包含模块路径和配置信息
    """
    blueprints = []
    
    try:
        package = importlib.import_module(package_path)
    except ImportError:
        return blueprints
    
    # 获取包所在的目录路径
    package_dir = os.path.dirname(package.__file__)
    
    # 遍历包下的所有模块
    for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
        if is_pkg:
            # 递归处理子包
            subpackage_path = f"{package_path}.{module_name}"
            blueprints.extend(discover_module_blueprints(subpackage_path))
        else:
            # 检查模块是否包含蓝图
            module_path = f"{package_path}.{module_name}"
            bp_info = _discover_blueprint_in_module(module_path)
            if bp_info:
                blueprints.append(bp_info)
    
    return blueprints


def _discover_blueprint_in_module(module_path: str) -> Optional[Dict[str, Any]]:
    """
    在指定模块中发现蓝图对象
    
    参数:
        module_path: 模块完整路径
    
    返回:
        蓝图配置信息字典，包含蓝图对象和注册配置
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        return None
    
    # 查找模块中的蓝图对象
    blueprint = None
    url_prefix = None
    
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, Blueprint):
            blueprint = obj
            # 根据模块路径推断URL前缀
            if module_path.startswith('app.api.'):
                # API模块使用/api/前缀
                submodule_path = module_path.replace('app.api.', '')
                url_prefix = f'/api/{submodule_path.replace(".", "/")}'
            elif module_path.startswith('app.auth'):
                url_prefix = '/auth'
            elif module_path.startswith('app.basic_data'):
                url_prefix = '/basic-data'
            elif module_path.startswith('app.dispatch'):
                url_prefix = '/dispatch'
            break
    
    if blueprint:
        return {
            'blueprint': blueprint,
            'url_prefix': url_prefix,
            'module_path': module_path
        }
    
    return None


def register_blueprint_with_config(app, bp_info: Dict[str, Any]) -> None:
    """
    使用配置信息注册蓝图
    
    参数:
        app: Flask应用实例
        bp_info: 蓝图信息字典
    
    返回:
        None
    """
    blueprint = bp_info['blueprint']
    url_prefix = bp_info.get('url_prefix')
    module_path = bp_info['module_path']
    
    # 注册蓝图
    if url_prefix:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        print(f"已注册蓝图: {blueprint.name} (模块: {module_path}, 前缀: {url_prefix})")
    else:
        app.register_blueprint(blueprint)
        print(f"已注册蓝图: {blueprint.name} (模块: {module_path})")


def get_blueprint_config(blueprint_name: str) -> Dict[str, Any]:
    """
    获取指定蓝图的配置信息
    
    参数:
        blueprint_name: 蓝图名称
    
    返回:
        蓝图配置字典
    """
    # 默认配置
    config = {
        'url_prefix': None,
        'subdomain': None,
        'url_defaults': None,
        'root_path': None,
        'cli_commands': []
    }
    
    # 根据蓝图名称设置特定配置
    if blueprint_name == 'auth_bp':
        config['url_prefix'] = '/auth'
    elif blueprint_name == 'basic_data_bp':
        config['url_prefix'] = '/basic-data'
    elif blueprint_name == 'dispatch_bp':
        config['url_prefix'] = '/dispatch'
    elif blueprint_name.startswith('api_'):
        # API蓝图使用统一前缀
        api_version = blueprint_name.replace('api_', '')
        config['url_prefix'] = f'/api/{api_version}'
    
    return config