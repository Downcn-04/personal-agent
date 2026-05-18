"""
聊天相关 API Schemas

包含聊天功能的请求和响应模型。
这些模型用于 API 数据验证和序列化，不直接映射到数据库。

术语说明：
- schemas：Pydantic 模型，用于 API 层的数据验证和序列化
- 与 database 模块的区别：database 用于数据库持久化，schemas 用于 API 交互
"""

from pydantic import BaseModel, Field, field_validator

from app.core import MAX_MESSAGE_LENGTH


# ==================== 请求模型（Request Schemas）====================

class ChatRequest(BaseModel):
    """聊天请求模型
    
    用于接收用户发送的聊天消息。
    FastAPI 会自动验证请求数据是否符合此模型。
    
    Attributes:
        content: 消息内容（1-10000 字符）
        thread_id: 所属会话 ID（UUID 格式）
    
    验证规则：
        - content 不能为空或纯空格
        - content 长度不超过 MAX_MESSAGE_LENGTH
        - thread_id 不能为空
    
    Example:
        ```json
        {
            "content": "你好，我想开发一个任务管理系统",
            "thread_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        ```
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
        """验证消息内容
        
        去除首尾空格，并检查是否为空。
        
        Args:
            v: 原始消息内容
            
        Returns:
            str: 处理后的消息内容
            
        Raises:
            ValueError: 消息内容为空时抛出
        """
        v = v.strip()
        if not v:
            raise ValueError("消息内容不能为空或纯空格")
        return v


# ==================== 响应模型（Response Schemas）====================

class MessageOut(BaseModel):
    """消息响应模型
    
    用于返回单条消息的数据。
    
    Attributes:
        id: 消息 ID
        thread_id: 所属会话 ID
        role: 消息角色（user/assistant/system）
        content: 消息内容
        created_at: 创建时间（ISO 格式字符串）
    
    Example:
        ```json
        {
            "id": 1,
            "thread_id": "550e8400-e29b-41d4-a716-446655440000",
            "role": "user",
            "content": "你好，我想开发一个任务管理系统",
            "created_at": "2026-05-19T10:30:00"
        }
        ```
    """
    id: int = Field(..., description="消息 ID")
    thread_id: str = Field(..., description="所属会话 ID")
    role: str = Field(..., description="消息角色（user=用户, assistant=AI助手, system=系统）")
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


class ThreadOut(BaseModel):
    """会话响应模型（简化版）
    
    用于返回会话列表时的数据。
    不包含消息列表，减少数据传输量。
    
    Attributes:
        id: 会话 ID
        title: 会话标题
        created_at: 创建时间（ISO 格式字符串）
    
    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "任务管理系统需求讨论",
            "created_at": "2026-05-19T10:30:00"
        }
        ```
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


class ThreadDetailOut(BaseModel):
    """会话详情响应模型（完整版）
    
    用于返回单个会话的完整数据，包含消息列表。
    
    Attributes:
        id: 会话 ID
        title: 会话标题
        created_at: 创建时间（ISO 格式字符串）
        messages: 消息列表
    
    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "任务管理系统需求讨论",
            "created_at": "2026-05-19T10:30:00",
            "messages": [
                {
                    "id": 1,
                    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "user",
                    "content": "你好",
                    "created_at": "2026-05-19T10:30:00"
                }
            ]
        }
        ```
    """
    id: str = Field(..., description="会话 ID")
    title: str = Field(..., description="会话标题")
    created_at: str = Field(..., description="创建时间（ISO 格式）")
    messages: list[MessageOut] = Field(default_factory=list, description="消息列表")


class ThreadCreateResponse(BaseModel):
    """创建会话响应模型
    
    用于返回新创建的会话 ID。
    
    Attributes:
        id: 新创建的会话 ID
    
    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000"
        }
        ```
    """
    id: str = Field(..., description="会话 ID")
