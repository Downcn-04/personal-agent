"""
核心模块

提供应用的基础设施组件：配置管理、数据库连接、异常体系、常量定义等。
"""

from app.core.config import Settings, get_settings, settings
from app.core.constants import (
    API_V1_PREFIX,
    AUDIT_DIMENSIONS,
    CHAT_PROCESSING_NODES,
    DEFAULT_PAGE_SIZE,
    DEFAULT_THREAD_LIST_LIMIT,
    MAX_MESSAGE_LENGTH,
    MAX_PAGE_SIZE,
    MAX_THREAD_TITLE_LENGTH,
    AuditDimension,
    DevelopmentStage,
    EventType,
    GraphNode,
    MessageRole,
    StageStatus,
)
from app.core.database import (
    Base,
    close_db,
    get_db_session,
    get_engine,
    get_session_factory,
    init_db,
)
from app.core.exceptions import (
    AppException,
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    EmptyMessageError,
    ExternalServiceError,
    LLMServiceError,
    MessageNotFoundError,
    MessageTooLongError,
    ResourceNotFoundError,
    ThreadAlreadyClosedError,
    ThreadNotFoundError,
    ValidationError,
)

__all__ = [
    # 配置
    "Settings",
    "get_settings",
    "settings",
    # 数据库
    "Base",
    "init_db",
    "close_db",
    "get_db_session",
    "get_engine",
    "get_session_factory",
    # 异常
    "AppException",
    "ResourceNotFoundError",
    "ThreadNotFoundError",
    "MessageNotFoundError",
    "ValidationError",
    "EmptyMessageError",
    "MessageTooLongError",
    "BusinessLogicError",
    "ThreadAlreadyClosedError",
    "ExternalServiceError",
    "LLMServiceError",
    "DatabaseError",
    "ConfigurationError",
    # 常量
    "MessageRole",
    "GraphNode",
    "EventType",
    "AuditDimension",
    "DevelopmentStage",
    "StageStatus",
    "MAX_MESSAGE_LENGTH",
    "MAX_THREAD_TITLE_LENGTH",
    "CHAT_PROCESSING_NODES",
    "AUDIT_DIMENSIONS",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "DEFAULT_THREAD_LIST_LIMIT",
    "API_V1_PREFIX",
]
