"""
业务逻辑层（Service Layer）

Service 层负责编排业务逻辑，协调多个 Repository 和外部服务。
遵循单一职责原则，每个 Service 处理一个业务领域。

职责说明：
- 编排多个 Repository 的操作
- 实现业务规则和验证
- 处理事务边界
- 调用外部服务（LLM、缓存等）
- 数据转换（ORM 模型 <-> DTO）

与其他层的关系：
- 依赖 Repository 层（数据访问）
- 被 API 层调用（通过依赖注入）
- 不直接操作数据库（通过 Repository）

示例：
    ```python
    # 在 API 路由中使用 Service
    from app.services import ThreadService
    
    @router.post("/threads")
    async def create_thread(service: ThreadService = Depends(get_thread_service)):
        thread_id = await service.create_thread()
        return {"id": thread_id}
    ```
"""

from app.services.audit_service import AuditService
from app.services.chat_service import ChatService
from app.services.thread_service import ThreadService

__all__ = [
    "ThreadService",
    "ChatService",
    "AuditService",
]
