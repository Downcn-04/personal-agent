"""
数据访问层（Repository）

提供数据库操作的抽象接口，遵循 Repository 模式。
Repository 层只负责数据访问，不包含业务逻辑。
"""

from app.repositories.message_repository import MessageRepository
from app.repositories.thread_repository import ThreadRepository

__all__ = [
    "ThreadRepository",
    "MessageRepository",
]
