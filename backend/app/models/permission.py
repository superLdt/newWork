# -*- coding: utf-8 -*-
"""
权限模型模块
定义Permission数据模型及相关功能
"""

from datetime import datetime
from ..extensions import db


class Permission(db.Model):
    """
    权限模型类
    对应RBAC权限管理系统中的权限实体
    """
    __tablename__ = 'Permission'
    
    id = db.Column(db.Integer, primary_key=True, comment='权限唯一ID')
    name = db.Column(db.String(100), nullable=False, comment='权限名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='权限代码')
    description = db.Column(db.Text, comment='权限描述')
    resource_type = db.Column(db.String(20), nullable=False, comment='资源类型: menu, api, button')
    resource_id = db.Column(db.String(100), comment='资源标识')
    action = db.Column(db.String(20), nullable=False, comment='操作类型: read, write, delete, execute')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Permission {self.code}>'
    
    def to_dict(self):
        """
        将权限对象转换为字典格式
        Returns:
            dict: 包含权限信息的字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_default_permissions(cls):
        """
        获取系统默认权限列表
        Returns:
            list: 默认权限列表
        """
        return [
            # 用户管理权限
            {'name': '查看用户', 'code': 'user:read', 'description': '查看用户列表和详情', 'resource_type': 'api', 'resource_id': '/users', 'action': 'read'},
            {'name': '创建用户', 'code': 'user:create', 'description': '创建新用户', 'resource_type': 'api', 'resource_id': '/users', 'action': 'write'},
            {'name': '编辑用户', 'code': 'user:update', 'description': '编辑用户信息', 'resource_type': 'api', 'resource_id': '/users', 'action': 'write'},
            {'name': '删除用户', 'code': 'user:delete', 'description': '删除用户', 'resource_type': 'api', 'resource_id': '/users', 'action': 'delete'},
            
            # 角色管理权限
            {'name': '查看角色', 'code': 'role:read', 'description': '查看角色列表和详情', 'resource_type': 'api', 'resource_id': '/roles', 'action': 'read'},
            {'name': '创建角色', 'code': 'role:create', 'description': '创建新角色', 'resource_type': 'api', 'resource_id': '/roles', 'action': 'write'},
            {'name': '编辑角色', 'code': 'role:update', 'description': '编辑角色信息', 'resource_type': 'api', 'resource_id': '/roles', 'action': 'write'},
            {'name': '删除角色', 'code': 'role:delete', 'description': '删除角色', 'resource_type': 'api', 'resource_id': '/roles', 'action': 'delete'},
            
            # 权限管理权限
            {'name': '查看权限', 'code': 'permission:read', 'description': '查看权限列表和详情', 'resource_type': 'api', 'resource_id': '/permissions', 'action': 'read'},
            {'name': '分配权限', 'code': 'permission:assign', 'description': '为角色分配权限', 'resource_type': 'api', 'resource_id': '/permissions', 'action': 'write'},
            
            # 菜单权限
            {'name': '用户管理菜单', 'code': 'menu:user_management', 'description': '访问用户管理菜单', 'resource_type': 'menu', 'resource_id': '/settings/users', 'action': 'read'},
            {'name': '角色管理菜单', 'code': 'menu:role_management', 'description': '访问角色管理菜单', 'resource_type': 'menu', 'resource_id': '/settings/roles', 'action': 'read'},
            {'name': '权限管理菜单', 'code': 'menu:permission_management', 'description': '访问权限管理菜单', 'resource_type': 'menu', 'resource_id': '/settings/permissions', 'action': 'read'},
            {'name': '基础数据菜单', 'code': 'menu:basic_data', 'description': '访问基础数据菜单', 'resource_type': 'menu', 'resource_id': '/basic-data', 'action': 'read'},
            {'name': '调度管理菜单', 'code': 'menu:dispatch', 'description': '访问调度管理菜单', 'resource_type': 'menu', 'resource_id': '/dispatch', 'action': 'read'},
            {'name': '运输订单菜单', 'code': 'menu:transport_orders', 'description': '访问运输订单菜单', 'resource_type': 'menu', 'resource_id': '/dispatch/orders', 'action': 'read'},
            
            # 基础数据权限
            {'name': '查看车辆', 'code': 'vehicle:read', 'description': '查看车辆列表和详情', 'resource_type': 'api', 'resource_id': '/vehicles', 'action': 'read'},
            {'name': '创建车辆', 'code': 'vehicle:create', 'description': '创建车辆', 'resource_type': 'api', 'resource_id': '/vehicles', 'action': 'write'},
            {'name': '管理车辆', 'code': 'vehicle:manage', 'description': '创建、编辑、删除车辆', 'resource_type': 'api', 'resource_id': '/vehicles', 'action': 'write'},
            {'name': '查看司机', 'code': 'driver:read', 'description': '查看司机列表和详情', 'resource_type': 'api', 'resource_id': '/drivers', 'action': 'read'},
            {'name': '管理司机', 'code': 'driver:manage', 'description': '创建、编辑、删除司机', 'resource_type': 'api', 'resource_id': '/drivers', 'action': 'write'},
            {'name': '查看客户', 'code': 'customer:read', 'description': '查看客户列表和详情', 'resource_type': 'api', 'resource_id': '/customers', 'action': 'read'},
            {'name': '管理客户', 'code': 'customer:manage', 'description': '创建、编辑、删除客户', 'resource_type': 'api', 'resource_id': '/customers', 'action': 'write'},
            
            # 吨位容积映射权限
            {'name': '查看吨位容积映射', 'code': 'tonnage_volume:read', 'description': '查看吨位容积映射列表和详情', 'resource_type': 'api', 'resource_id': '/tonnage-volume', 'action': 'read'},
            {'name': '创建吨位容积映射', 'code': 'tonnage_volume:create', 'description': '创建吨位容积映射', 'resource_type': 'api', 'resource_id': '/tonnage-volume', 'action': 'write'},
            {'name': '更新吨位容积映射', 'code': 'tonnage_volume:update', 'description': '更新吨位容积映射', 'resource_type': 'api', 'resource_id': '/tonnage-volume', 'action': 'write'},
            {'name': '删除吨位容积映射', 'code': 'tonnage_volume:delete', 'description': '删除吨位容积映射', 'resource_type': 'api', 'resource_id': '/tonnage-volume', 'action': 'write'},
            
            # 调度管理权限
            {'name': '查看订单', 'code': 'order:read', 'description': '查看运输订单', 'resource_type': 'api', 'resource_id': '/orders', 'action': 'read'},
            {'name': '创建调度', 'code': 'dispatch:create', 'description': '创建调度任务', 'resource_type': 'api', 'resource_id': '/dispatch', 'action': 'write'},
            {'name': '查看调度', 'code': 'dispatch:read', 'description': '查看调度任务列表与详情', 'resource_type': 'api', 'resource_id': '/dispatch', 'action': 'read'},
            {'name': '更新调度', 'code': 'dispatch:update', 'description': '更新调度任务信息', 'resource_type': 'api', 'resource_id': '/dispatch', 'action': 'write'},
            {'name': '审核调度', 'code': 'dispatch:approve', 'description': '审核与批准调度任务', 'resource_type': 'api', 'resource_id': '/dispatch', 'action': 'execute'},
            {'name': '派发调度', 'code': 'dispatch:assign', 'description': '指派车辆与司机', 'resource_type': 'api', 'resource_id': '/dispatch', 'action': 'execute'},
            {'name': '完成调度', 'code': 'dispatch:complete', 'description': '标记调度任务完成', 'resource_type': 'api', 'resource_id': '/dispatch', 'action': 'execute'},
            {'name': '查看跟踪', 'code': 'tracking:read', 'description': '查看运输跟踪信息', 'resource_type': 'api', 'resource_id': '/tracking', 'action': 'read'},
            
            # 供应商响应权限
            {'name': '供应商响应', 'code': 'supplier:respond', 'description': '供应商响应调度任务', 'resource_type': 'api', 'resource_id': '/dispatch/supplier-response', 'action': 'write'},
            {'name': '供应商确认', 'code': 'supplier:confirm', 'description': '供应商确认调度任务', 'resource_type': 'api', 'resource_id': '/dispatch/tasks/*/confirm', 'action': 'write'},
            {'name': '供应商申诉', 'code': 'supplier:appeal', 'description': '供应商提交调度任务申诉', 'resource_type': 'api', 'resource_id': '/dispatch/tasks/*/appeal', 'action': 'write'},
            {'name': '班组派车', 'code': 'team:assign', 'description': '班组长派车响应', 'resource_type': 'api', 'resource_id': '/dispatch/team-response', 'action': 'write'},
            {'name': '大容积供应商派车', 'code': 'large_capacity_supplier:assign', 'description': '大容积供应商派车响应', 'resource_type': 'api', 'resource_id': '/dispatch/large-capacity-supplier-response', 'action': 'write'},
            
            # 文件上传权限
            {'name': '上传图片', 'code': 'upload:image', 'description': '上传图片文件', 'resource_type': 'api', 'resource_id': '/api/v1/upload/image', 'action': 'write'},
            
        # 为了向后兼容，保留原有权限
        {'name': '外包派车', 'code': 'outsourcing:assign', 'description': '外包管理公司派车响应（已废弃）', 'resource_type': 'api', 'resource_id': '/dispatch/outsourcing-response', 'action': 'write'},
        ]
    
    @staticmethod
    def create_permission(name, code, description, resource_type, resource_id, action):
        """
        创建权限的便捷方法
        
        Args:
            name: 权限名称
            code: 权限代码
            description: 权限描述
            resource_type: 资源类型
            resource_id: 资源标识
            action: 操作类型
            
        Returns:
            Permission: 创建的权限对象
        """
        permission = cls(
            name=name,
            code=code,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action
        )
        return permission