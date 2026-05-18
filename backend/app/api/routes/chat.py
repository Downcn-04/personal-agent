"""
聊天相关 API 路由

提供会话管理和聊天功能的 HTTP 接口。

路由列表：
- POST   /threads          - 创建新会话
- GET    /threads          - 获取会话列表
- GET    /threads/{id}     - 获取会话详情
- DELETE /threads/{id}     - 删除会话
- POST   /chat             - 发送消息（流式响应）
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service, get_thread_service
from app.core import EventType, ThreadNotFoundError
from app.models import (
    ChatRequest,
    DeleteResponse,
    ThreadCreateResponse,
    ThreadDetailOut,
    ThreadOut,
)
from app.services import ChatService, ThreadService

# 创建路由器
router = APIRouter(tags=["chat"])


# ==================== 会话管理接口 ====================

@router.post(
    "/threads",
    response_model=ThreadCreateResponse,
    status_code=201,
    summary="创建新会话",
    description="创建一个新的聊天会话，返回会话 ID"
)
async def create_thread(
    service: Annotated[ThreadService, Depends(get_thread_service)]
) -> ThreadCreateResponse:
    """创建新会话
    
    Args:
        service: 会话服务（自动注入）
        
    Returns:
        ThreadCreateResponse: 包含新会话 ID
        
    Example:
        ```bash
        curl -X POST http://localhost:8000/threads
        ```
        
        Response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000"
        }
        ```
    """
    return await service.create_thread()


@router.get(
    "/threads",
    response_model=list[ThreadOut],
    summary="获取会话列表",
    description="获取所有会话列表，按创建时间倒序排列"
)
async def list_threads(
    service: Annotated[ThreadService, Depends(get_thread_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="返回数量限制")] = 100,
    offset: Annotated[int, Query(ge=0, description="偏移量（用于分页）")] = 0
) -> list[ThreadOut]:
    """获取会话列表
    
    Args:
        service: 会话服务（自动注入）
        limit: 返回数量限制（1-100）
        offset: 偏移量（用于分页）
        
    Returns:
        list[ThreadOut]: 会话列表
        
    Example:
        ```bash
        curl http://localhost:8000/threads?limit=20&offset=0
        ```
    """
    return await service.get_thread_list(limit=limit, offset=offset)


@router.get(
    "/threads/{thread_id}",
    response_model=ThreadDetailOut,
    summary="获取会话详情",
    description="获取指定会话的详细信息，包含所有消息"
)
async def get_thread(
    thread_id: Annotated[str, Path(description="会话 ID")],
    service: Annotated[ThreadService, Depends(get_thread_service)]
) -> ThreadDetailOut:
    """获取会话详情
    
    Args:
        thread_id: 会话 ID
        service: 会话服务（自动注入）
        
    Returns:
        ThreadDetailOut: 会话详情（包含消息列表）
        
    Raises:
        HTTPException: 会话不存在时返回 404
        
    Example:
        ```bash
        curl http://localhost:8000/threads/550e8400-e29b-41d4-a716-446655440000
        ```
    """
    try:
        return await service.get_thread_detail(thread_id)
    except ThreadNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.delete(
    "/threads/{thread_id}",
    response_model=DeleteResponse,
    summary="删除会话",
    description="删除指定会话及其所有消息"
)
async def delete_thread(
    thread_id: Annotated[str, Path(description="会话 ID")],
    service: Annotated[ThreadService, Depends(get_thread_service)]
) -> DeleteResponse:
    """删除会话
    
    Args:
        thread_id: 会话 ID
        service: 会话服务（自动注入）
        
    Returns:
        DeleteResponse: 删除结果
        
    Raises:
        HTTPException: 会话不存在时返回 404
        
    Example:
        ```bash
        curl -X DELETE http://localhost:8000/threads/550e8400-e29b-41d4-a716-446655440000
        ```
    """
    deleted = await service.delete_thread(thread_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return DeleteResponse(ok=True, message="Thread deleted successfully")


# ==================== 聊天接口 ====================

@router.post(
    "/chat",
    summary="发送消息",
    description="发送消息到指定会话，返回 AI 响应（流式）",
    responses={
        200: {
            "description": "流式响应（Server-Sent Events）",
            "content": {
                "text/event-stream": {
                    "example": "data: {\"content\": \"你好\"}\n\ndata: [DONE]\n\n"
                }
            }
        },
        404: {"description": "会话不存在"}
    }
)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)]
) -> StreamingResponse:
    """发送消息并获取 AI 响应（流式）
    
    使用 Server-Sent Events (SSE) 协议进行流式响应。
    
    Args:
        request: 聊天请求（包含消息内容和会话 ID）
        service: 聊天服务（自动注入）
        
    Returns:
        StreamingResponse: SSE 流式响应
        
    Raises:
        HTTPException: 会话不存在时返回 404
        
    事件格式：
        - data: {"content": "文本内容"}  # 流式输出的文本
        - data: {"type": "stage", ...}   # 阶段变更事件
        - data: [DONE]                   # 完成标记
        
    Example:
        ```bash
        curl -X POST http://localhost:8000/chat \
          -H "Content-Type: application/json" \
          -d '{"content": "你好", "thread_id": "550e8400-e29b-41d4-a716-446655440000"}'
        ```
    """
    async def event_generator():
        """SSE 事件生成器"""
        try:
            # 处理消息并流式返回
            async for event in service.process_message(
                request.thread_id,
                request.content
            ):
                # 格式化事件
                if event["type"] == EventType.CONTENT:
                    # 内容事件
                    yield f"data: {json.dumps({'content': event['data']})}\n\n"
                elif event["type"] == "custom":
                    # 自定义事件（阶段变更等）
                    yield f"data: {json.dumps(event['data'])}\n\n"
            
            # 发送完成标记
            yield f"data: {EventType.DONE}\n\n"
            
        except ThreadNotFoundError as e:
            # 会话不存在错误
            yield f"data: {json.dumps({'error': e.message, 'code': e.code})}\n\n"
        except Exception as e:
            # 其他错误
            yield f"data: {json.dumps({'error': str(e), 'code': 'INTERNAL_ERROR'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )
