"""
会话业务逻辑服务

处理会话相关的业务逻辑，包括创建、查询、更新、删除等操作。
"""

import uuid
from typing import Optional

from app.core import MAX_THREAD_TITLE_LENGTH, ThreadNotFoundError
from app.models import ThreadCreateResponse, ThreadDetailOut, ThreadOut
from app.repositories import MessageRepository, ThreadRepository


class ThreadService:
    """会话业务逻辑服务
    
    负责会话相关的业务逻辑处理，协调 ThreadRepository 和 MessageRepository。
    
    职责：
    - 创建新会话
    - 查询会话列表和详情
    - 自动生成会话标题（业务规则）
    - 删除会话
    
    Attributes:
        thread_repo: 会话数据访问对象
        message_repo: 消息数据访问对象
    """
    
    def __init__(
        self,
        thread_repo: ThreadRepository,
        message_repo: MessageRepository
    ):
        """初始化服务
        
        Args:
            thread_repo: 会话 Repository 实例
            message_repo: 消息 Repository 实例
        """
        self.thread_repo = thread_repo
        self.message_repo = message_repo
    
    async def create_thread(self, title: str = "") -> ThreadCreateResponse:
        """创建新会话
        
        生成 UUID 作为会话 ID，创建空会话。
        
        Args:
            title: 会话标题（可选，默认为空）
            
        Returns:
            ThreadCreateResponse: 包含新会话 ID 的响应
            
        Example:
            ```python
            response = await service.create_thread()
            print(response.id)  # "550e8400-e29b-41d4-a716-446655440000"
            ```
        """
        # 生成 UUID
        thread_id = str(uuid.uuid4())
        
        # 创建会话
        await self.thread_repo.create(thread_id, title)
        
        return ThreadCreateResponse(id=thread_id)
    
    async def get_thread_list(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[ThreadOut]:
        """获取会话列表
        
        返回会话列表，按创建时间倒序排列（最新的在前）。
        
        Args:
            limit: 返回数量限制
            offset: 偏移量（用于分页）
            
        Returns:
            list[ThreadOut]: 会话列表
            
        Example:
            ```python
            threads = await service.get_thread_list(limit=20, offset=0)
            for thread in threads:
                print(thread.title)
            ```
        """
        # 查询会话列表
        threads = await self.thread_repo.list_all(limit, offset)
        
        # 转换为 DTO
        return [
            ThreadOut(
                id=t.id,
                title=t.title,
                created_at=str(t.created_at)
            )
            for t in threads
        ]
    
    async def get_thread_detail(self, thread_id: str) -> ThreadDetailOut:
        """获取会话详情（包含消息列表）
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            ThreadDetailOut: 会话详情（包含消息列表）
            
        Raises:
            ThreadNotFoundError: 会话不存在时抛出
            
        Example:
            ```python
            detail = await service.get_thread_detail("thread-id")
            print(f"标题: {detail.title}")
            print(f"消息数: {len(detail.messages)}")
            ```
        """
        # 查询会话
        thread = await self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise ThreadNotFoundError(thread_id)
        
        # 查询消息列表
        messages = await self.message_repo.get_by_thread(thread_id)
        
        # 转换为 DTO
        from app.models import MessageOut
        
        return ThreadDetailOut(
            id=thread.id,
            title=thread.title,
            created_at=str(thread.created_at),
            messages=[
                MessageOut(
                    id=m.id,
                    thread_id=m.thread_id,
                    role=m.role,
                    content=m.content,
                    created_at=str(m.created_at)
                )
                for m in messages
            ]
        )
    
    async def auto_generate_title(
        self,
        thread_id: str,
        first_message_content: str
    ) -> None:
        """自动生成会话标题（业务逻辑）
        
        根据第一条用户消息自动生成会话标题。
        只在会话标题为空时生成。
        
        业务规则：
        - 取消息内容的前 50 个字符作为标题
        - 如果会话已有标题，则不更新
        
        Args:
            thread_id: 会话 ID
            first_message_content: 第一条消息的内容
            
        Example:
            ```python
            await service.auto_generate_title(
                "thread-id",
                "你好，我想开发一个任务管理系统"
            )
            # 会话标题将被设置为 "你好，我想开发一个任务管理系统"（最多 50 字符）
            ```
        """
        # 查询会话
        thread = await self.thread_repo.get_by_id(thread_id)
        
        # 只在标题为空时生成
        if thread and not thread.title:
            # 业务规则：取前 50 个字符
            title = first_message_content[:MAX_THREAD_TITLE_LENGTH]
            await self.thread_repo.update_title(thread_id, title)
    
    async def delete_thread(self, thread_id: str) -> bool:
        """删除会话
        
        删除会话及其所有消息（级联删除）。
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            bool: 删除成功返回 True，会话不存在返回 False
            
        Example:
            ```python
            success = await service.delete_thread("thread-id")
            if success:
                print("删除成功")
            else:
                print("会话不存在")
            ```
        """
        return await self.thread_repo.delete(thread_id)
    
    async def check_thread_exists(self, thread_id: str) -> bool:
        """检查会话是否存在
        
        Args:
            thread_id: 会话 ID
            
        Returns:
            bool: 存在返回 True，否则返回 False
            
        Example:
            ```python
            exists = await service.check_thread_exists("thread-id")
            if not exists:
                raise ThreadNotFoundError("thread-id")
            ```
        """
        return await self.thread_repo.exists(thread_id)
