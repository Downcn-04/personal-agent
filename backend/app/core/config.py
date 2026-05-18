"""
应用配置管理模块

使用 Pydantic Settings 进行类型安全的配置管理，支持从环境变量和 .env 文件加载配置。
所有配置项都有明确的类型和验证规则。
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类
    
    配置优先级：环境变量 > .env 文件 > 默认值
    """
    
    # ==================== 应用配置 ====================
    app_name: str = Field(
        default="Personal Agent Backend",
        description="应用名称"
    )
    
    app_version: str = Field(
        default="0.1.0",
        description="应用版本"
    )
    
    environment: Literal["development", "testing", "production"] = Field(
        default="development",
        description="运行环境"
    )
    
    debug: bool = Field(
        default=False,
        description="是否开启调试模式"
    )
    
    # ==================== 数据库配置 ====================
    database_url: str = Field(
        ...,  # 必填项
        description="数据库连接字符串，格式: postgresql+asyncpg://user:pass@host:port/dbname"
    )
    
    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="数据库连接池大小"
    )
    
    database_pool_recycle: int = Field(
        default=3600,
        ge=300,
        description="连接池回收时间（秒）"
    )
    
    database_echo: bool = Field(
        default=False,
        description="是否打印 SQL 语句（仅用于调试）"
    )
    
    # ==================== LLM 配置 ====================
    llm_provider: Literal["deepseek", "openai"] = Field(
        default="deepseek",
        description="LLM 提供商"
    )
    
    llm_api_key: str = Field(
        ...,  # 必填项
        description="LLM API 密钥"
    )
    
    llm_base_url: str = Field(
        default="https://api.deepseek.com",
        description="LLM API 基础 URL"
    )
    
    llm_model: str = Field(
        default="deepseek-chat",
        description="LLM 模型名称"
    )
    
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM 生成温度（0-2）"
    )
    
    llm_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=32768,
        description="LLM 最大生成 token 数"
    )
    
    llm_timeout: int = Field(
        default=60,
        ge=10,
        le=300,
        description="LLM 请求超时时间（秒）"
    )
    
    # ==================== CORS 配置 ====================
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="允许的跨域来源列表"
    )
    
    cors_allow_credentials: bool = Field(
        default=True,
        description="是否允许携带凭证"
    )
    
    # ==================== 日志配置 ====================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="日志级别"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # ==================== 验证器 ====================
    @field_validator("llm_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """验证 API Key 格式"""
        if not v or len(v) < 10:
            raise ValueError("LLM API Key 格式无效，长度至少为 10 个字符")
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """验证数据库 URL 格式"""
        if not v.startswith("postgresql"):
            raise ValueError("仅支持 PostgreSQL 数据库")
        return v
    
    # ==================== Pydantic 配置 ====================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 忽略未定义的环境变量
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例
    
    使用 lru_cache 确保配置只加载一次，提高性能。
    
    Returns:
        Settings: 应用配置实例
    """
    return Settings()


# 导出配置实例（用于非依赖注入场景）
settings = get_settings()
