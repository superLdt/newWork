"""
自定义异常类
统一异常处理规范
"""


class SmartTransportException(Exception):
    """基础异常类"""
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or 500
        self.payload = payload


class AuthenticationError(SmartTransportException):
    """认证异常"""
    def __init__(self, message="认证失败", payload=None):
        super().__init__(message, 401, payload)


class ValidationError(SmartTransportException):
    """数据验证异常"""
    def __init__(self, message="数据验证失败", payload=None):
        super().__init__(message, 400, payload)


class ResourceNotFoundError(SmartTransportException):
    """资源不存在异常"""
    def __init__(self, message="资源不存在", payload=None):
        super().__init__(message, 404, payload)


class PermissionDeniedError(SmartTransportException):
    """权限不足异常"""
    def __init__(self, message="权限不足", payload=None):
        super().__init__(message, 403, payload)