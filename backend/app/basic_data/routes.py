#!/usr/bin/env python3
"""
基础数据模块路由文件

包含基础数据管理的API端点
"""

from flask import jsonify, request
from . import basic_data_bp


@basic_data_bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """获取车辆列表接口"""
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [
            {
                'id': 1,
                'plate_number': '京A12345',
                'vehicle_type': '货车',
                'capacity': '10吨',
                'status': '空闲'
            },
            {
                'id': 2,
                'plate_number': '京B67890',
                'vehicle_type': '厢式货车',
                'capacity': '5吨',
                'status': '运输中'
            }
        ]
    })


@basic_data_bp.route('/drivers', methods=['GET'])
def get_drivers():
    """获取司机列表接口"""
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [
            {
                'id': 1,
                'name': '张三',
                'phone': '13800138001',
                'license_type': 'A照',
                'status': '空闲'
            },
            {
                'id': 2,
                'name': '李四',
                'phone': '13800138002',
                'license_type': 'B照',
                'status': '工作中'
            }
        ]
    })


@basic_data_bp.route('/customers', methods=['GET'])
def get_customers():
    """获取客户列表接口"""
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [
            {
                'id': 1,
                'name': '北京科技有限公司',
                'contact': '王经理',
                'phone': '010-12345678',
                'address': '北京市海淀区'
            },
            {
                'id': 2,
                'name': '上海贸易有限公司',
                'contact': '李总监',
                'phone': '021-87654321',
                'address': '上海市浦东新区'
            }
        ]
    })