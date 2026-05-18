"""
公共 API Schemas

提供跨业务模块使用的通用响应模型。
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field


# ==================== 错误响应 ====================

class ErrorResponse(BaseModel):
    """错误响应模型
    
    统一的错误响应格式，用于所有 API 错误。
    
    Attributes:
        error: 错误消息（面向用户）
        code: 错误码（用于前端判断错误类型）
        details: 错误详情（可选，提供额外的调试信息）
    
    Example:
        ```json
        {
            "error": "Thread with ID 'xxx' not found",
            "code": "RESOURCE_NOT_FOUND",
            "details": {
                "resource_type": "Thread",
                "resource_id": "xxx"
            }
        }
        ```
    """
    error: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误码")
    details: Optional[dict[str, Any]] = Field(None, description="错误详情")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Thread with ID 'xxx' not found",
                    "code": "RESOURCE_NOT_FOUND",
                    "details": {
                        "resource_type": "Thread",
                        "resource_id": "xxx"
                    }
                }
            ]
        }
    }


# ==================== 成功响应 ====================

class DeleteResponse(BaseModel):
    """删除操作响应模型
    
    用于删除操作的统一响应格式。
    
    Attributes:
        ok: 是否成功
        message: 操作消息（可选）
    
    Example:
        ```json
        {
            "ok": true,
            "message": "Thread deleted successfully"
        }
        ```
    """
    ok: bool = Field(True, description="是否成功")
    message: Optional[str] = Field(None, description="操作消息")


# ==================== 分页相关 ====================

class PaginationMeta(BaseModel):
    """分页元数据
    
    提供分页信息，用于列表查询响应。
    
    Attributes:
        total: 总记录数
        page: 当前页码（从 1 开始）
        page_size: 每页记录数
        total_pages: 总页数
    
    Example:
        ```json
        {
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
        ```
    """
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码（从 1 开始）")
    page_size: int = Field(..., ge=1, le=100, description="每页记录数")
    total_pages: int = Field(..., ge=0, description="总页数")


# 泛型类型变量（用于分页响应）
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型（泛型）
    
    用于返回分页数据的统一格式。
    
    Attributes:
        data: 数据列表（泛型）
        meta: 分页元数据
    
    Example:
        ```python
        # 定义具体的分页响应
        class ThreadListResponse(PaginatedResponse[ThreadOut]):
            pass
        
        # 使用
        response = ThreadListResponse(
            data=[thread1, thread2],
            meta=PaginationMeta(total=100, page=1, page_size=20, total_pages=5)
        )
        ```
    """
    data: list[T] = Field(..., description="数据列表")
    meta: PaginationMeta = Field(..., description="分页元数据")


# ==================== 健康检查 ====================

class HealthCheckResponse(BaseModel):
    """健康检查响应
    
    用于服务健康检查接口。
    
    Attributes:
        status: 服务状态（healthy/unhealthy）
        version: 应用版本
        timestamp: 检查时间戳
    
    Example:
        ```json
        {
            "status": "healthy",
            "version": "0.1.0",
            "timestamp": "2026-05-19T10:30:00Z"
        }
        ```
    """
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="应用版本")
    timestamp: str = Field(..., description="检查时间戳（ISO 格式）")
