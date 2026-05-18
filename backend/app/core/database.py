"""
数据库连接和会话管理模块

提供数据库引擎初始化、会话工厂和依赖注入函数。
使用 SQLAlchemy 2.0 的异步 API。
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.core.exceptions import DatabaseError


# ==================== 数据库基类 ====================

class Base(DeclarativeBase):
    """ORM 模型基类
    
    所有数据库模型都应继承此类。
    """
    pass


# ==================== 全局变量 ====================

# 数据库引擎（延迟初始化）
_engine: AsyncEngine | None = None

# 会话工厂（延迟初始化）
_session_factory: async_sessionmaker[AsyncSession] | None = None


# ==================== 引擎和会话工厂 ====================

def get_engine() -> AsyncEngine:
    """获取数据库引擎
    
    使用单例模式，确保整个应用只有一个引擎实例。
    
    Returns:
        AsyncEngine: 数据库引擎实例
        
    Raises:
        DatabaseError: 引擎未初始化时抛出
    """
    global _engine
    if _engine is None:
        raise DatabaseError("Database engine not initialized. Call init_db() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂
    
    Returns:
        async_sessionmaker: 会话工厂实例
        
    Raises:
        DatabaseError: 会话工厂未初始化时抛出
    """
    global _session_factory
    if _session_factory is None:
        raise DatabaseError("Session factory not initialized. Call init_db() first.")
    return _session_factory


# ==================== 初始化函数 ====================

async def init_db() -> None:
    """初始化数据库
    
    创建数据库引擎、会话工厂，并自动创建所有表。
    应在应用启动时调用一次。
    
    Raises:
        DatabaseError: 数据库初始化失败时抛出
    """
    global _engine, _session_factory
    
    try:
        settings = get_settings()
        
        # 创建异步引擎
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            pool_recycle=settings.database_pool_recycle,
            pool_pre_ping=True,  # 连接前检查连接是否有效
        )
        
        # 创建会话工厂
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后不过期对象
            autoflush=False,  # 禁用自动刷新
        )
        
        # 创建所有表（仅用于开发环境，生产环境应使用 Alembic 迁移）
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
    except Exception as e:
        raise DatabaseError(f"Failed to initialize database: {str(e)}")


async def close_db() -> None:
    """关闭数据库连接
    
    释放数据库引擎资源。
    应在应用关闭时调用。
    """
    global _engine, _session_factory
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


# ==================== 依赖注入 ====================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（用于 FastAPI 依赖注入）
    
    使用上下文管理器自动管理会话生命周期。
    会话在请求结束时自动关闭。
    
    Yields:
        AsyncSession: 数据库会话实例
        
    Example:
        ```python
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(Item))
            return result.scalars().all()
        ```
    """
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            # 发生异常时回滚事务
            await session.rollback()
            raise
        finally:
            # 确保会话关闭
            await session.close()
