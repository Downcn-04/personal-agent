"""
应用入口文件

FastAPI 应用的主入口，负责应用初始化、中间件配置、路由注册等。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import (
    app_exception_handler,
    business_logic_error_handler,
    configuration_error_handler,
    database_error_handler,
    external_service_error_handler,
    resource_not_found_handler,
    validation_error_handler,
)
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core import (
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    ExternalServiceError,
    ResourceNotFoundError,
    ValidationError,
    close_db,
    get_settings,
    init_db,
)
from app.core.exceptions import AppException


# ==================== 生命周期管理 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理
    
    在应用启动时初始化资源，在应用关闭时清理资源。
    
    Args:
        app: FastAPI 应用实例
        
    Yields:
        None
    """
    # 启动时：初始化数据库
    await init_db()
    
    yield
    
    # 关闭时：清理资源
    await close_db()


# ==================== 创建应用实例 ====================

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Personal Agent Backend API",
    lifespan=lifespan,
)


# ==================== 中间件配置 ====================

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 异常处理器注册 ====================

# 注册自定义异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
app.add_exception_handler(BusinessLogicError, business_logic_error_handler)
app.add_exception_handler(ExternalServiceError, external_service_error_handler)
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(ConfigurationError, configuration_error_handler)


# ==================== 路由注册 ====================

# 注册 API 路由（与前端约定：/threads、/chat、/health 等根路径）
app.include_router(chat_router)
app.include_router(health_router)


# ==================== 根路径 ====================

@app.get("/", tags=["root"])
async def root():
    """根路径
    
    返回 API 基本信息。
    
    Returns:
        dict: API 信息
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
