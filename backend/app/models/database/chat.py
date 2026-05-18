"""
聊天相关数据库模型

包含会话（Thread）和消息（Message）的 ORM 模型。
这些模型直接映射到数据库表，使用 SQLAlchemy 进行 ORM 操作。

术语说明：
- database 模块：存放 SQLAlchemy ORM 模型，映射到数据库表（类似 Java 的 @Entity）
- 与 schemas 模块的区别：schemas 用于 API 数据验证，database 用于数据库持久化
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Thread(Base):
    """会话表（ORM 模型）
    
    存储用户的对话会话信息。
    每个会话包含多条消息，形成完整的对话历史。
    
    数据库表名：threads
    
    Attributes:
        id: 会话唯一标识（UUID 字符串）
        title: 会话标题（自动从第一条用户消息生成，最多 50 字符）
        created_at: 创建时间（数据库自动设置）
        messages: 关联的消息列表（一对多关系）
    
    关系说明：
        - 一个 Thread 包含多个 Message（一对多）
        - 删除 Thread 时自动级联删除所有 Message
    
    索引：
        - 主键索引：id
        - 时间索引：created_at（用于按时间排序查询）
    """
    __tablename__ = "threads"
    
    # ==================== 主键 ====================
    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        comment="会话 ID（UUID 字符串）"
    )
    
    # ==================== 基本字段 ====================
    title: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        comment="会话标题（从第一条消息自动生成）"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    # ==================== 关系映射 ====================
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="thread",
        order_by="Message.created_at",  # 按创建时间排序
        cascade="all, delete-orphan",   # 级联删除：删除 Thread 时自动删除所有 Message
        lazy="selectin",                # 加载策略：自动加载关联数据，避免 N+1 查询
        passive_deletes=True            # 使用数据库级联删除
    )
    
    # ==================== 魔术方法 ====================
    def __repr__(self) -> str:
        """字符串表示（用于调试）"""
        title_preview = self.title[:20] + "..." if len(self.title) > 20 else self.title
        return f"<Thread(id={self.id}, title='{title_preview}')>"


class Message(Base):
    """消息表（ORM 模型）
    
    存储会话中的消息记录。
    每条消息属于一个会话，包含角色和内容。
    
    数据库表名：messages
    
    Attributes:
        id: 消息唯一标识（自增整数）
        thread_id: 所属会话 ID（外键）
        role: 消息角色（user/assistant/system）
        content: 消息内容（文本）
        created_at: 创建时间（数据库自动设置）
        thread: 关联的会话对象（多对一关系）
    
    关系说明：
        - 多个 Message 属于一个 Thread（多对一）
        - 外键约束：thread_id 引用 threads.id
        - 级联删除：Thread 删除时自动删除关联的 Message
    
    索引：
        - 主键索引：id
        - 外键索引：thread_id（用于按会话查询）
        - 复合索引：(thread_id, created_at)（优化按会话和时间查询）
    """
    __tablename__ = "messages"
    
    # ==================== 主键 ====================
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="消息 ID（自增）"
    )
    
    # ==================== 外键 ====================
    thread_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("threads.id", ondelete="CASCADE"),  # 级联删除
        nullable=False,
        index=True,  # 添加索引，优化按会话查询
        comment="所属会话 ID"
    )
    
    # ==================== 基本字段 ====================
    role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息角色（user=用户, assistant=AI助手, system=系统）"
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息内容"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    # ==================== 关系映射 ====================
    thread: Mapped["Thread"] = relationship(
        "Thread",
        back_populates="messages"
    )
    
    # ==================== 表级配置 ====================
    __table_args__ = (
        # 复合索引：优化 "查询某会话的消息并按时间排序" 的场景
        Index("idx_thread_created", "thread_id", "created_at"),
    )
    
    # ==================== 魔术方法 ====================
    def __repr__(self) -> str:
        """字符串表示（用于调试）"""
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"
