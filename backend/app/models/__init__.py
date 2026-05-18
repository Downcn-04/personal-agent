"""
数据模型模块

包含两类模型：
1. database 模块：SQLAlchemy ORM 模型（数据库层）
2. schemas 模块：Pydantic 模型（API 层）

模块说明：
- database：数据库 ORM 模型，映射到数据库表，用于数据持久化
- schemas：API 数据模型，用于请求验证和响应序列化

命名来源：
- database：表示"数据库模型"，强调这是数据库层面的定义
- schemas：Pydantic 和 FastAPI 的标准术语，表示"数据结构定义"

使用示例：
    ```python
    # 导入 ORM 模型（用于 Repository 层）
    from app.models import Thread, Message
    
    # 导入 API Schemas（用于 API 路由）
    from app.models import ChatRequest, ThreadOut
    ```
"""

# ==================== Database Models（ORM 模型）====================
from app.models.database import Message, Thread

# ==================== API Schemas（Pydantic 模型）====================
from app.models.schemas import (
    ChatRequest,
    DeleteResponse,
    ErrorResponse,
    FeatureAssessment,
    MessageOut,
    PaginationMeta,
    RequirementAuditReport,
    ThreadCreateResponse,
    ThreadDetailOut,
    ThreadOut,
)

__all__ = [
    # ORM 模型（database）
    "Thread",
    "Message",
    # API Schemas（schemas）
    "ChatRequest",
    "ThreadOut",
    "ThreadDetailOut",
    "ThreadCreateResponse",
    "MessageOut",
    "ErrorResponse",
    "DeleteResponse",
    "PaginationMeta",
    "FeatureAssessment",
    "RequirementAuditReport",
]
