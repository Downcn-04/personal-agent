"""
自定义异常体系

定义应用级异常，用于统一错误处理和错误码管理。
所有业务异常都应继承自 AppException。
"""

from typing import Any, Optional


class AppException(Exception):
    """应用基础异常类
    
    所有自定义异常的基类，提供统一的错误信息和错误码。
    
    Attributes:
        message: 错误消息（面向用户）
        code: 错误码（用于前端判断）
        details: 额外的错误详情（可选）
    """
    
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式（用于 API 响应）"""
        result = {
            "error": self.message,
            "code": self.code
        }
        if self.details:
            result["details"] = self.details
        return result


# ==================== 资源相关异常 ====================

class ResourceNotFoundError(AppException):
    """资源不存在异常"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            code="RESOURCE_NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class ThreadNotFoundError(ResourceNotFoundError):
    """会话不存在异常"""
    
    def __init__(self, thread_id: str):
        super().__init__(resource_type="Thread", resource_id=thread_id)


class MessageNotFoundError(ResourceNotFoundError):
    """消息不存在异常"""
    
    def __init__(self, message_id: str):
        super().__init__(resource_type="Message", resource_id=message_id)


# ==================== 验证相关异常 ====================

class ValidationError(AppException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )


class EmptyMessageError(ValidationError):
    """空消息异常"""
    
    def __init__(self):
        super().__init__(
            message="Message content cannot be empty",
            field="content"
        )


class MessageTooLongError(ValidationError):
    """消息过长异常"""
    
    def __init__(self, max_length: int, actual_length: int):
        super().__init__(
            message=f"Message exceeds maximum length of {max_length} characters",
            field="content"
        )
        self.details["max_length"] = max_length
        self.details["actual_length"] = actual_length


# ==================== 业务逻辑异常 ====================

class BusinessLogicError(AppException):
    """业务逻辑异常"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="BUSINESS_LOGIC_ERROR"
        )


class ThreadAlreadyClosedError(BusinessLogicError):
    """会话已关闭异常"""
    
    def __init__(self, thread_id: str):
        super().__init__(
            message=f"Thread '{thread_id}' is already closed"
        )


# ==================== 外部服务异常 ====================

class ExternalServiceError(AppException):
    """外部服务异常"""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(
            message=f"{service_name} error: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name}
        )


class LLMServiceError(ExternalServiceError):
    """LLM 服务异常"""
    
    def __init__(self, message: str, provider: str = "LLM"):
        super().__init__(service_name=provider, message=message)


class DatabaseError(ExternalServiceError):
    """数据库异常"""
    
    def __init__(self, message: str):
        super().__init__(service_name="Database", message=message)


# ==================== 配置相关异常 ====================

class ConfigurationError(AppException):
    """配置错误异常"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details=details
        )
