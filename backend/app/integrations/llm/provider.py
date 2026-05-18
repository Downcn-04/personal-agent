"""
LLM 提供商抽象

提供 LLM 服务的统一接口，支持依赖注入和可测试性。
"""

from langchain_openai import ChatOpenAI

from app.core import get_settings


class LLMProvider:
    """LLM 提供商类
    
    封装 LLM 客户端的创建和管理，支持延迟初始化。
    
    职责：
    - 管理 LLM 客户端实例
    - 提供不同温度的 LLM 实例（聊天、审计等）
    - 支持依赖注入和测试 Mock
    
    Attributes:
        settings: 应用配置
        _chat_client: 聊天 LLM 客户端（延迟初始化）
        _audit_client: 审计 LLM 客户端（延迟初始化）
    """
    
    def __init__(self, settings=None):
        """初始化 LLM 提供商
        
        Args:
            settings: 应用配置（可选，默认使用全局配置）
        """
        self.settings = settings or get_settings()
        self._chat_client = None
        self._audit_client = None
    
    @property
    def chat_client(self) -> ChatOpenAI:
        """获取聊天 LLM 客户端
        
        用于普通对话，温度较高（0.7），生成更有创造性的回复。
        
        Returns:
            ChatOpenAI: 聊天 LLM 客户端实例
        """
        if self._chat_client is None:
            self._chat_client = ChatOpenAI(
                api_key=self.settings.llm_api_key,
                base_url=self.settings.llm_base_url,
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                timeout=self.settings.llm_timeout,
            )
        return self._chat_client
    
    @property
    def audit_client(self) -> ChatOpenAI:
        """获取审计 LLM 客户端
        
        用于需求审计，温度较低（0.1），生成更准确、一致的结果。
        
        Returns:
            ChatOpenAI: 审计 LLM 客户端实例
        """
        if self._audit_client is None:
            self._audit_client = ChatOpenAI(
                api_key=self.settings.llm_api_key,
                base_url=self.settings.llm_base_url,
                model=self.settings.llm_model,
                temperature=0.1,  # 低温度，更准确
                max_tokens=self.settings.llm_max_tokens,
                timeout=self.settings.llm_timeout,
            )
        return self._audit_client
    
    def close(self):
        """关闭 LLM 客户端
        
        释放资源（如果需要）。
        """
        # ChatOpenAI 不需要显式关闭
        self._chat_client = None
        self._audit_client = None


# 全局 LLM 提供商实例（用于非依赖注入场景）
_llm_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """获取全局 LLM 提供商实例
    
    使用单例模式，确保整个应用只有一个实例。
    
    Returns:
        LLMProvider: LLM 提供商实例
    """
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider
