"""
数据库模型公共基类和 Mixin

提供可复用的字段和行为，遵循 DRY 原则。
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Text, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """时间戳 Mixin
    
    为模型自动添加创建时间和更新时间字段。
    使用数据库函数自动设置时间，确保时区一致性。
    
    Attributes:
        created_at: 记录创建时间（由数据库自动设置）
        updated_at: 记录最后更新时间（由数据库自动更新）
    
    Usage:
        ```python
        class MyModel(Base, TimestampMixin):
            __tablename__ = "my_table"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
        ```
    """
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="最后更新时间"
    )


class UUIDMixin:
    """UUID 主键 Mixin
    
    为模型提供 UUID 字符串作为主键。
    UUID 由应用层生成，避免数据库依赖。
    
    Attributes:
        id: UUID 字符串主键
    
    Usage:
        ```python
        class MyModel(Base, UUIDMixin):
            __tablename__ = "my_table"
            # id 字段已由 UUIDMixin 提供
        ```
    """
    
    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键（UUID 字符串）"
    )


class SoftDeleteMixin:
    """软删除 Mixin
    
    为模型添加软删除功能，删除时只标记而不真正删除数据。
    
    Attributes:
        deleted_at: 删除时间（NULL 表示未删除）
        is_deleted: 是否已删除（冗余字段，便于查询）
    
    Usage:
        ```python
        class MyModel(Base, SoftDeleteMixin):
            __tablename__ = "my_table"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
        
        # 查询时过滤已删除记录
        query = select(MyModel).where(MyModel.is_deleted == False)
        ```
    """
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        default=None,
        comment="删除时间（NULL 表示未删除）"
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,  # 添加索引，优化查询
        comment="是否已删除"
    )
