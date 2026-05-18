"""
消息数据访问层

提供消息（Message）相关的数据库操作。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Message


class MessageRepository:
    """消息数据访问类
    
    负责消息的 CRUD 操作，不包含业务逻辑。
    
    Attributes:
        db: 数据库会话实例
    """
    
    def __init__(self, db: AsyncSession):
        """初始化 Repository
        
        Args:
            db: 数据库会话实例
        """
        self.db = db
    
    async def create(
        self,
        thread_id: str,
        role: str,
        content: str
    ) -> Message:
        """创建新消息
        
        Args:
            thread_id: 所属会话 ID
            role: 消息角色（user/assistant/system）
            content: 消息内容
            
        Returns:
            Message: 创建的消息实例
        """
        message = Message(
            thread_id=thread_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_by_id(self, message_id: int) -> Optional[Message]:
        """根据 ID 获取消息
        
        Args:
            message_id: 消息 ID
            
        Returns:
            Optional[Message]: 消息实例，不存在时返回 None
        """
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_thread(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[Message]:
        """获取指定会话的消息列表
        
        按创建时间正序排列（最早的在前）。
        
        Args:
            thread_id: 会话 ID
            limit: 返回数量限制（None 表示不限制）
            offset: 偏移量（用于分页）
            
        Returns:
            list[Message]: 消息列表
        """
        query = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
        )
        
        if limit is not None:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_by_thread(
        self,
        thread_id: str,
        limit: int = 10
    ) -> list[Message]:
        """获取指定会话的最新消息
        
        按创建时间倒序排列（最新的在前）。
        
        Args:
            thread_id: 会话 ID
            limit: 返回数量限制
            
        Returns:
            list[Message]: 消息列表
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        # 反转列表，使最早的消息在前
        return list(reversed(result.scalars().all()))
    
    async def count_by_thread(self, thread_id: str) -> int:
        """获取指定会话的消息数量
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            int: 消息数量
        """
        result = await self.db.execute(
            select(Message).where(Message.thread_id == thread_id)
        )
        return len(result.scalars().all())
    
    async def get_first_user_message(
        self,
        thread_id: str
    ) -> Optional[Message]:
        """获取指定会话的第一条用户消息
        
        用于自动生成会话标题。
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            Optional[Message]: 第一条用户消息，不存在时返回 None
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.thread_id == thread_id)
            .where(Message.role == "user")
            .order_by(Message.created_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def delete_by_thread(self, thread_id: str) -> int:
        """删除指定会话的所有消息
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            int: 删除的消息数量
        """
        from sqlalchemy import delete
        
        result = await self.db.execute(
            delete(Message).where(Message.thread_id == thread_id)
        )
        await self.db.commit()
        return result.rowcount
