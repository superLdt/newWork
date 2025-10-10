from flask import jsonify

def success_response(data=None, message="操作成功", code=200):
    """
    标准成功响应格式
    """
    response = {
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(response)

def error_response(message="操作失败", code=400, errors=None):
    """
    标准错误响应格式
    """
    response = {
        "code": code,
        "message": message,
        "errors": errors
    }
    return jsonify(response)