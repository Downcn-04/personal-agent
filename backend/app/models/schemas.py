"""
API 数据传输对象（DTO）

定义 API 请求和响应的数据结构。
使用 Pydantic 进行数据验证和序列化。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core import MAX_MESSAGE_LENGTH


# ==================== 请求模型 ====================

class ChatRequest(BaseModel):
    """聊天请求
    
    Attributes:
        content: 消息内容
        thread_id: 会话 ID
    """
    content: str = Field(
        ...,
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH,
        description="消息内容",
        examples=["你好，我想开发一个任务管理系统"]
    )
    
    thread_id: str = Field(
        ...,
        min_length=1,
        description="会话 ID（UUID 格式）",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证消息内容"""
        v = v.strip()
        if not v:
            raise ValueError("消息内容不能为空")
        return v


# ==================== 响应模型 ====================

class ThreadOut(BaseModel):
    """会话响应
    
    Attributes:
        id: 会话 ID
        title: 会话标题
        created_at: 创建时间
    """
    id: str = Field(..., description="会话 ID")
    title: str = Field(..., description="会话标题")
    created_at: str = Field(..., description="创建时间（ISO 格式）")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "任务管理系统需求讨论",
                    "created_at": "2026-05-19T10:30:00"
                }
            ]
        }
    }


class MessageOut(BaseModel):
    """消息响应
    
    Attributes:
        id: 消息 ID
        thread_id: 所属会话 ID
        role: 消息角色
        content: 消息内容
        created_at: 创建时间
    """
    id: int = Field(..., description="消息 ID")
    thread_id: str = Field(..., description="所属会话 ID")
    role: str = Field(..., description="消息角色（user/assistant/system）")
    content: str = Field(..., description="消息内容")
    created_at: str = Field(..., description="创建时间（ISO 格式）")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "user",
                    "content": "你好，我想开发一个任务管理系统",
                    "created_at": "2026-05-19T10:30:00"
                }
            ]
        }
    }


class ThreadDetailOut(BaseModel):
    """会话详情响应（包含消息列表）
    
    Attributes:
        id: 会话 ID
        title: 会话标题
        created_at: 创建时间
        messages: 消息列表
    """
    id: str = Field(..., description="会话 ID")
    title: str = Field(..., description="会话标题")
    created_at: str = Field(..., description="创建时间（ISO 格式）")
    messages: list[MessageOut] = Field(default_factory=list, description="消息列表")


class ThreadCreateResponse(BaseModel):
    """创建会话响应
    
    Attributes:
        id: 新创建的会话 ID
    """
    id: str = Field(..., description="会话 ID")


class DeleteResponse(BaseModel):
    """删除操作响应
    
    Attributes:
        ok: 是否成功
    """
    ok: bool = Field(True, description="是否成功")


# ==================== 错误响应模型 ====================

class ErrorResponse(BaseModel):
    """错误响应
    
    Attributes:
        error: 错误消息
        code: 错误码
        details: 错误详情（可选）
    """
    error: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误码")
    details: Optional[dict] = Field(None, description="错误详情")
    
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
