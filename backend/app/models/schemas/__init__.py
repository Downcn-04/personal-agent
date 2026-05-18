"""
API Schemas 模块（Pydantic Schemas）

术语说明：
- schemas 模块：存放 Pydantic 模型，用于 API 数据验证和序列化
- 作用：API 层面的数据结构定义，负责请求验证和响应格式化
- 类比：Java 中的 DTO 类，Go 中的 struct + json tag

与 database 模块的区别：
- schemas：API 层面的模型（Pydantic），用于数据验证、序列化、文档生成
- database：数据库层面的模型（SQLAlchemy ORM），用于数据持久化

为什么叫 schemas？
- Pydantic 的官方术语，表示"数据结构定义"（Schema = 结构）
- FastAPI 官方文档统一使用这个命名
- 强调这是"数据的形状"而非"数据本身"

组织方式：
- 按业务领域拆分文件（chat.py, user.py, project.py, audit.py 等）
- 每个文件包含相关的请求/响应模型
- common.py 提供公共响应模型（错误、分页等）

示例：
    ```python
    # 在 API 路由中使用 schemas
    from app.models.schemas import ChatRequest, ThreadOut
    
    @router.post("/chat")
    async def chat(request: ChatRequest) -> ThreadOut:
        # FastAPI 自动验证 request 数据
        # 自动序列化 ThreadOut 为 JSON
        ...
    ```
"""

# 公共 Schemas
from app.models.schemas.common import (
    DeleteResponse,
    ErrorResponse,
    HealthCheckResponse,
    PaginationMeta,
)

# 聊天相关 Schemas
from app.models.schemas.chat import (
    ChatRequest,
    MessageOut,
    ThreadCreateResponse,
    ThreadDetailOut,
    ThreadOut,
)

# 审计相关 Schemas
from app.models.schemas.audit import FeatureAssessment, RequirementAuditReport

__all__ = [
    # 公共 Schemas
    "ErrorResponse",
    "DeleteResponse",
    "PaginationMeta",
    "HealthCheckResponse",
    # 聊天 Schemas
    "ChatRequest",
    "ThreadOut",
    "ThreadDetailOut",
    "ThreadCreateResponse",
    "MessageOut",
    # 审计 Schemas
    "FeatureAssessment",
    "RequirementAuditReport",
]
