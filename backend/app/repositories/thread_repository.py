"""
会话数据访问层

提供会话（Thread）相关的数据库操作。
"""

from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import DEFAULT_THREAD_LIST_LIMIT
from app.models.database import Message, Thread


class ThreadRepository:
    """会话数据访问类
    
    负责会话的 CRUD 操作，不包含业务逻辑。
    
    Attributes:
        db: 数据库会话实例
    """
    
    def __init__(self, db: AsyncSession):
        """初始化 Repository
        
        Args:
            db: 数据库会话实例
        """
        self.db = db
    
    async def create(self, thread_id: str, title: str = "") -> Thread:
        """创建新会话
        
        Args:
            thread_id: 会话 ID（UUID 字符串）
            title: 会话标题（可选）
            
        Returns:
            Thread: 创建的会话实例
        """
        thread = Thread(id=thread_id, title=title)
        self.db.add(thread)
        await self.db.commit()
        await self.db.refresh(thread)
        return thread
    
    async def get_by_id(self, thread_id: str) -> Optional[Thread]:
        """根据 ID 获取会话
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            Optional[Thread]: 会话实例，不存在时返回 None
        """
        result = await self.db.execute(
            select(Thread).where(Thread.id == thread_id)
        )
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        limit: int = DEFAULT_THREAD_LIST_LIMIT,
        offset: int = 0
    ) -> list[Thread]:
        """获取会话列表
        
        按创建时间倒序排列（最新的在前）。
        
        Args:
            limit: 返回数量限制
            offset: 偏移量（用于分页）
            
        Returns:
            list[Thread]: 会话列表
        """
        result = await self.db.execute(
            select(Thread)
            .order_by(Thread.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def update_title(self, thread_id: str, title: str) -> bool:
        """更新会话标题
        
        Args:
            thread_id: 会话 ID
            title: 新标题
            
        Returns:
            bool: 更新成功返回 True，会话不存在返回 False
        """
        thread = await self.get_by_id(thread_id)
        if not thread:
            return False
        
        thread.title = title
        await self.db.commit()
        return True
    
    async def delete(self, thread_id: str) -> bool:
        """删除会话及其所有消息
        
        使用级联删除，会同时删除该会话下的所有消息。
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            bool: 删除成功返回 True，会话不存在返回 False
        """
        # 先删除关联的消息
        await self.db.execute(
            delete(Message).where(Message.thread_id == thread_id)
        )
        
        # 再删除会话
        result = await self.db.execute(
            delete(Thread).where(Thread.id == thread_id)
        )
        
        await self.db.commit()
        return result.rowcount > 0
    
    async def exists(self, thread_id: str) -> bool:
        """检查会话是否存在
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            bool: 存在返回 True，否则返回 False
        """
        result = await self.db.execute(
            select(Thread.id).where(Thread.id == thread_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def count(self) -> int:
        """获取会话总数
        
        Returns:
            int: 会话总数
        """
        result = await self.db.execute(
            select(Thread)
        )
        return len(result.scalars().all())
