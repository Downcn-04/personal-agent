"""
数据库 ORM 模型模块（Database Models）

术语说明：
- database 模块：存放 SQLAlchemy ORM 模型，直接映射到数据库表
- 作用：数据持久化层，负责与数据库交互
- 类比：Java 中的 @Entity 类，Go 中的 struct + gorm tag

与 schemas 模块的区别：
- database：数据库层面的模型（ORM），包含数据库字段、关系、索引等
- schemas：API 层面的模型（Pydantic），用于请求验证和响应序列化

组织方式：
- 按业务领域拆分文件（chat.py, user.py, project.py 等）
- 每个文件包含相关的模型类
- base.py 提供公共基类和 Mixin

示例：
    ```python
    # 在 Repository 中使用 database 模型
    from app.models.database import Thread, Message
    
    thread = Thread(id="uuid", title="My Thread")
    db.add(thread)
    await db.commit()
    ```
"""

# 公共基类和 Mixin
from app.models.database.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

# 聊天相关模型
from app.models.database.chat import Message, Thread

__all__ = [
    # 公共基类和 Mixin
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    # 聊天模型
    "Thread",
    "Message",
]
