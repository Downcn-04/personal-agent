"""
聊天业务逻辑服务

处理聊天相关的业务逻辑，包括消息发送、流式响应、LLM 交互等。
"""

from typing import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core import CHAT_PROCESSING_NODES, EventType, MessageRole, ThreadNotFoundError
from app.repositories import MessageRepository
from app.services.thread_service import ThreadService


class ChatService:
    """聊天业务逻辑服务
    
    负责聊天相关的业务逻辑处理，协调消息存储、LLM 调用、流式响应等。
    
    职责：
    - 处理用户消息
    - 调用 LLM 生成响应
    - 流式返回 AI 响应
    - 保存消息到数据库
    - 自动生成会话标题
    
    Attributes:
        message_repo: 消息数据访问对象
        thread_service: 会话业务逻辑服务
        chat_graph: LangGraph 工作流（延迟注入）
    """
    
    def __init__(
        self,
        message_repo: MessageRepository,
        thread_service: ThreadService
    ):
        """初始化服务
        
        Args:
            message_repo: 消息 Repository 实例
            thread_service: 会话 Service 实例
        """
        self.message_repo = message_repo
        self.thread_service = thread_service
        self.chat_graph = None  # 延迟注入（避免循环依赖）
    
    def set_chat_graph(self, chat_graph):
        """设置 LangGraph 工作流（延迟注入）
        
        Args:
            chat_graph: LangGraph 编译后的工作流实例
        """
        self.chat_graph = chat_graph
    
    async def process_message(
        self,
        thread_id: str,
        content: str
    ) -> AsyncGenerator[dict, None]:
        """处理用户消息并流式返回 AI 响应
        
        完整流程：
        1. 验证会话存在
        2. 保存用户消息
        3. 自动生成会话标题（如果是第一条消息）
        4. 获取历史消息
        5. 转换为 LangChain 格式
        6. 调用 LLM 生成响应（流式）
        7. 保存 AI 响应
        
        Args:
            thread_id: 会话 ID
            content: 用户消息内容
            
        Yields:
            dict: 流式事件（内容、阶段变更等）
            
        Raises:
            ThreadNotFoundError: 会话不存在时抛出
            
        Example:
            ```python
            async for event in service.process_message("thread-id", "你好"):
                if event["type"] == "content":
                    print(event["data"], end="", flush=True)
            ```
        """
        # 1. 验证会话存在
        exists = await self.thread_service.check_thread_exists(thread_id)
        if not exists:
            raise ThreadNotFoundError(thread_id)
        
        # 2. 保存用户消息
        await self.message_repo.create(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=content
        )
        
        # 3. 自动生成会话标题
        await self.thread_service.auto_generate_title(thread_id, content)
        
        # 4. 获取历史消息
        history = await self.message_repo.get_by_thread(thread_id)
        
        # 5. 转换为 LangChain 格式
        lc_messages = self._convert_to_langchain_messages(history)
        
        # 6. 调用 LLM 并流式返回
        collected_content = []
        
        # 导入 chat_graph（延迟导入，避免循环依赖）
        if self.chat_graph is None:
            from app.integrations.llm.graph import chat_graph
            self.chat_graph = chat_graph
        
        async for event in self.chat_graph.astream_events(
            {"messages": lc_messages},
            version="v2"
        ):
            # 处理事件
            processed_event = self._process_event(event)
            
            if processed_event:
                # 收集内容（用于保存）
                if processed_event.get("type") == EventType.CONTENT:
                    collected_content.append(processed_event["data"])
                
                # 返回给前端
                yield processed_event
        
        # 7. 保存 AI 响应
        if collected_content:
            full_response = "".join(collected_content)
            await self.message_repo.create(
                thread_id=thread_id,
                role=MessageRole.ASSISTANT,
                content=full_response
            )
    
    def _convert_to_langchain_messages(self, messages) -> list:
        """转换消息格式为 LangChain 格式
        
        将数据库中的消息转换为 LangChain 的消息对象。
        
        Args:
            messages: 数据库消息列表
            
        Returns:
            list: LangChain 消息对象列表
            
        Example:
            ```python
            db_messages = [Message(role="user", content="你好")]
            lc_messages = self._convert_to_langchain_messages(db_messages)
            # [HumanMessage(content="你好")]
            ```
        """
        lc_messages = []
        
        for m in messages:
            if m.role == MessageRole.SYSTEM:
                lc_messages.append(SystemMessage(content=m.content))
            elif m.role == MessageRole.ASSISTANT:
                lc_messages.append(AIMessage(content=m.content))
            else:  # user
                lc_messages.append(HumanMessage(content=m.content))
        
        return lc_messages
    
    def _process_event(self, event: dict) -> dict | None:
        """处理 LangGraph 事件
        
        过滤和转换 LangGraph 的原始事件为前端需要的格式。
        
        Args:
            event: LangGraph 原始事件
            
        Returns:
            dict | None: 处理后的事件，如果不需要返回则为 None
            
        事件类型：
        - on_custom_event: 自定义事件（阶段变更、阶段数据等）
        - on_chat_model_stream: LLM 流式输出
        - 其他事件: 忽略
        """
        # 只处理特定节点的事件
        node_name = event.get("metadata", {}).get("langgraph_node")
        if node_name not in CHAT_PROCESSING_NODES:
            if event["event"] != "on_custom_event":
                return None
        
        event_kind = event["event"]
        
        # 自定义事件（阶段变更、阶段数据等）
        if event_kind == "on_custom_event":
            return {
                "type": "custom",
                "data": event["data"]
            }
        
        # LLM 流式输出
        elif event_kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                return {
                    "type": EventType.CONTENT,
                    "data": chunk.content
                }
        
        return None
