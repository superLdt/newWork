#!/usr/bin/env python3
"""
统一错误处理中间件
提供全局的错误处理机制，符合四层架构规范
"""

from flask import jsonify
import logging

# 配置日志
logger = logging.getLogger(__name__)

def error_handler(error):
    """
    全局错误处理中间件
    
    Args:
        error: 捕获的异常对象
        
    Returns:
        JSON格式的错误响应和相应的HTTP状态码
    """
    
    # 记录错误日志
    logger.error(f"全局错误处理: {type(error).__name__}: {str(error)}", exc_info=True)
    
    # 根据异常类型返回相应的错误响应
    error_type = type(error).__name__
    
    # 已知异常类型的处理
    if error_type == 'ValidationError':
        return jsonify({
            'success': False,
            'error': '数据验证失败',
            'message': str(error)
        }), 400
    
    elif error_type == 'ValueError':
        return jsonify({
            'success': False,
            'error': '参数错误',
            'message': str(error)
        }), 400
    
    elif error_type == 'PermissionError':
        return jsonify({
            'success': False,
            'error': '权限不足',
            'message': '您没有执行此操作的权限'
        }), 403
    
    elif error_type == 'NotFound':
        return jsonify({
            'success': False,
            'error': '资源未找到',
            'message': str(error) or '请求的资源不存在'
        }), 404
    
    elif error_type == 'IntegrityError':
        return jsonify({
            'success': False,
            'error': '数据完整性错误',
            'message': '数据操作违反完整性约束'
        }), 409
    
    # 未知异常的处理
    else:
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': '系统繁忙，请稍后再试'
        }), 500

def register_error_handlers(app):
    """
    注册错误处理器到Flask应用
    
    Args:
        app: Flask应用实例
    """
    # 注册全局错误处理器
    app.register_error_handler(Exception, error_handler)
    
    # 注册特定的HTTP错误处理器
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': '错误的请求',
            'message': '请求格式或参数不正确'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': '未授权',
            'message': '请先登录系统'
        }), 401
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '资源未找到',
            'message': '请求的资源不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': '系统繁忙，请稍后再试'
        }), 500