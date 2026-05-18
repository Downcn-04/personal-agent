"""
数据库 ORM 模型

定义数据库表结构和关系映射。
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Thread(Base):
    """会话表
    
    存储用户的对话会话信息。
    
    Attributes:
        id: 会话唯一标识（UUID 字符串）
        title: 会话标题（自动从第一条消息生成）
        created_at: 创建时间
        messages: 关联的消息列表
    """
    __tablename__ = "threads"
    
    # 主键
    id: Mapped[str] = mapped_column(Text, primary_key=True, comment="会话 ID（UUID）")
    
    # 基本字段
    title: Mapped[str] = mapped_column(
        Text,
        default="",
        comment="会话标题"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        comment="创建时间"
    )
    
    # 关系
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="thread",
        order_by="Message.created_at",
        cascade="all, delete-orphan",  # 级联删除
        lazy="selectin"  # 自动加载关联数据
    )
    
    def __repr__(self) -> str:
        return f"<Thread(id={self.id}, title={self.title[:20]})>"


class Message(Base):
    """消息表
    
    存储会话中的消息记录。
    
    Attributes:
        id: 消息唯一标识（自增 ID）
        thread_id: 所属会话 ID
        role: 消息角色（user/assistant/system）
        content: 消息内容
        created_at: 创建时间
        thread: 关联的会话对象
    """
    __tablename__ = "messages"
    
    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="消息 ID"
    )
    
    # 外键
    thread_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属会话 ID"
    )
    
    # 基本字段
    role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息角色（user/assistant/system）"
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息内容"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        comment="创建时间"
    )
    
    # 关系
    thread: Mapped["Thread"] = relationship(
        "Thread",
        back_populates="messages"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_thread_created", "thread_id", "created_at"),  # 复合索引，优化查询
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, content={self.content[:30]})>"
