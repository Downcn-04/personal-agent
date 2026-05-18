"""
全局异常处理器

统一处理应用中的异常，返回标准化的错误响应。
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    ExternalServiceError,
    ResourceNotFoundError,
    ValidationError,
)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理应用自定义异常
    
    将自定义异常转换为标准的 JSON 响应。
    
    Args:
        request: FastAPI 请求对象
        exc: 应用异常实例
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    # 根据异常类型确定 HTTP 状态码
    status_code = _get_status_code_for_exception(exc)
    
    return JSONResponse(
        status_code=status_code,
        content=exc.to_dict()
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """处理验证错误
    
    Args:
        request: FastAPI 请求对象
        exc: 验证异常实例
        
    Returns:
        JSONResponse: 验证错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=exc.to_dict()
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """处理资源不存在错误
    
    Args:
        request: FastAPI 请求对象
        exc: 资源不存在异常实例
        
    Returns:
        JSONResponse: 404 错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exc.to_dict()
    )


async def business_logic_error_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """处理业务逻辑错误
    
    Args:
        request: FastAPI 请求对象
        exc: 业务逻辑异常实例
        
    Returns:
        JSONResponse: 400 错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.to_dict()
    )


async def external_service_error_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    """处理外部服务错误
    
    Args:
        request: FastAPI 请求对象
        exc: 外部服务异常实例
        
    Returns:
        JSONResponse: 502 错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=exc.to_dict()
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """处理数据库错误
    
    Args:
        request: FastAPI 请求对象
        exc: 数据库异常实例
        
    Returns:
        JSONResponse: 500 错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=exc.to_dict()
    )


async def configuration_error_handler(request: Request, exc: ConfigurationError) -> JSONResponse:
    """处理配置错误
    
    Args:
        request: FastAPI 请求对象
        exc: 配置异常实例
        
    Returns:
        JSONResponse: 500 错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=exc.to_dict()
    )


def _get_status_code_for_exception(exc: AppException) -> int:
    """根据异常类型确定 HTTP 状态码
    
    Args:
        exc: 应用异常实例
        
    Returns:
        int: HTTP 状态码
    """
    # 异常类型到状态码的映射
    exception_status_map = {
        ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        BusinessLogicError: status.HTTP_400_BAD_REQUEST,
        ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    # 查找匹配的异常类型
    for exc_type, status_code in exception_status_map.items():
        if isinstance(exc, exc_type):
            return status_code
    
    # 默认返回 500
    return status.HTTP_500_INTERNAL_SERVER_ERROR
