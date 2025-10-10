#!/usr/bin/env python3
"""
调度管理模块路由文件

包含运输调度相关的API端点
"""

from flask import jsonify, request
from . import dispatch_bp


@dispatch_bp.route('/orders', methods=['GET'])
def get_orders():
    """获取运输订单列表接口"""
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [
            {
                'id': 1,
                'order_number': 'ORD20240101001',
                'customer': '北京科技有限公司',
                'start_location': '北京市海淀区',
                'end_location': '上海市浦东新区',
                'goods_type': '电子产品',
                'weight': '5吨',
                'status': '待调度'
            },
            {
                'id': 2,
                'order_number': 'ORD20240101002',
                'customer': '上海贸易有限公司',
                'start_location': '上海市浦东新区',
                'end_location': '广州市天河区',
                'goods_type': '服装',
                'weight': '3吨',
                'status': '运输中'
            }
        ]
    })


@dispatch_bp.route('/dispatch', methods=['POST'])
def create_dispatch():
    """创建调度任务接口"""
    return jsonify({
        'code': 200,
        'message': '调度任务创建成功',
        'data': {
            'dispatch_id': 1001,
            'order_number': 'ORD20240101001',
            'vehicle': '京A12345',
            'driver': '张三',
            'estimated_arrival_time': '2024-01-02 10:00:00',
            'status': '已调度'
        }
    })


@dispatch_bp.route('/tracking/<int:dispatch_id>', methods=['GET'])
def get_tracking_info(dispatch_id):
    """获取运输跟踪信息接口"""
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'dispatch_id': dispatch_id,
            'current_location': '北京市朝阳区',
            'next_stop': '天津市',
            'estimated_arrival': '2024-01-02 12:00:00',
            'status': '运输中',
            'progress': '30%'
        }
    })