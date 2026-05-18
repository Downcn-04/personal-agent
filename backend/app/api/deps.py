"""
API 依赖注入模块

提供 FastAPI 路由所需的依赖项，包括数据库会话、Repository、Service 等。
使用 FastAPI 的依赖注入系统，实现松耦合和可测试性。

依赖层次：
1. 数据库会话（get_db_session）
2. Repository 层（依赖数据库会话）
3. Service 层（依赖 Repository）
4. API 路由（依赖 Service）

示例：
    ```python
    # 在路由中使用依赖注入
    @router.post("/threads")
    async def create_thread(
        service: ThreadService = Depends(get_thread_service)
    ):
        return await service.create_thread()
    ```
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories import MessageRepository, ThreadRepository
from app.services import AuditService, ChatService, ThreadService


# ==================== Repository 依赖 ====================

def get_thread_repository(
    db: AsyncSession = Depends(get_db_session)
) -> ThreadRepository:
    """获取会话 Repository 实例
    
    Args:
        db: 数据库会话（自动注入）
        
    Returns:
        ThreadRepository: 会话 Repository 实例
    """
    return ThreadRepository(db)


def get_message_repository(
    db: AsyncSession = Depends(get_db_session)
) -> MessageRepository:
    """获取消息 Repository 实例
    
    Args:
        db: 数据库会话（自动注入）
        
    Returns:
        MessageRepository: 消息 Repository 实例
    """
    return MessageRepository(db)


# ==================== Service 依赖 ====================

def get_thread_service(
    thread_repo: ThreadRepository = Depends(get_thread_repository),
    message_repo: MessageRepository = Depends(get_message_repository)
) -> ThreadService:
    """获取会话 Service 实例
    
    Args:
        thread_repo: 会话 Repository（自动注入）
        message_repo: 消息 Repository（自动注入）
        
    Returns:
        ThreadService: 会话 Service 实例
    """
    return ThreadService(thread_repo, message_repo)


def get_chat_service(
    message_repo: MessageRepository = Depends(get_message_repository),
    thread_service: ThreadService = Depends(get_thread_service)
) -> ChatService:
    """获取聊天 Service 实例
    
    Args:
        message_repo: 消息 Repository（自动注入）
        thread_service: 会话 Service（自动注入）
        
    Returns:
        ChatService: 聊天 Service 实例
    """
    return ChatService(message_repo, thread_service)


def get_audit_service() -> AuditService:
    """获取审计 Service 实例
    
    Returns:
        AuditService: 审计 Service 实例
    """
    return AuditService()
