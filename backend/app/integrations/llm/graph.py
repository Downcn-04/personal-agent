"""
LangGraph 工作流定义

定义需求审计和聊天的工作流编排。
"""

import json

from langchain_core.messages import SystemMessage
from langgraph.config import get_stream_writer
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from app.integrations.llm.prompts import GUIDED_QUESTION_PROMPT, PM_AUDIT_PROMPT, PRD_GENERATION_PROMPT
from app.models.schemas.audit import RequirementAuditReport
from app.core import DevelopmentStage, StageStatus
from app.integrations.llm.provider import get_llm_provider


# ==================== 状态定义 ====================

class ProjectState(BaseModel):
    """项目状态
    
    在工作流节点之间传递的状态对象。
    
    Attributes:
        messages: 消息列表（LangChain 格式）
        audit_report: 审计报告（字典格式）
        is_ready_for_dev: 是否准备好开发
    """
    messages: list = []
    audit_report: dict = {}
    is_ready_for_dev: bool = False


# ==================== 工作流节点 ====================

async def pm_audit_node(state: ProjectState) -> dict:
    """产品经理审计节点
    
    审计用户需求的完整性，检查是否满足开发条件。
    
    Args:
        state: 项目状态
        
    Returns:
        dict: 更新的状态（audit_report, is_ready_for_dev）
    """
    # 获取流式写入器
    writer = get_stream_writer()
    
    # 发送阶段变更事件
    writer({
        "type": "stage",
        "stage": DevelopmentStage.REQUIREMENTS,
        "status": StageStatus.ACTIVE
    })
    
    # 构建审计提示词
    schema_json = json.dumps(
        RequirementAuditReport.model_json_schema(),
        ensure_ascii=False
    )
    prompt = (
        f"{PM_AUDIT_PROMPT}\n\n"
        f"请严格按照以下JSON Schema输出审计结果：\n"
        f"```json\n{schema_json}\n```"
    )
    
    # 构建消息列表
    audit_messages = [SystemMessage(content=prompt)] + list(state.messages)
    
    # 调用 LLM 进行审计
    llm_provider = get_llm_provider()
    json_llm = llm_provider.audit_client.bind(
        response_format={"type": "json_object"}
    )
    response = await json_llm.ainvoke(audit_messages)
    
    # 解析审计报告
    report = RequirementAuditReport.model_validate_json(response.content)
    
    # 发送阶段数据事件
    writer({
        "type": "stage_data",
        "stage": DevelopmentStage.REQUIREMENTS,
        "data": report.model_dump()
    })
    
    # 如果审计通过，发送完成事件
    if report.all_satisfied:
        writer({
            "type": "stage",
            "stage": DevelopmentStage.REQUIREMENTS,
            "status": StageStatus.COMPLETED
        })
    
    return {
        "audit_report": report.model_dump(),
        "is_ready_for_dev": report.all_satisfied,
    }


async def chat_node(state: ProjectState) -> dict:
    """聊天节点
    
    根据审计结果生成引导式追问，或进行普通对话。
    
    Args:
        state: 项目状态
        
    Returns:
        dict: 更新的状态（messages）
    """
    llm_provider = get_llm_provider()
    
    # 如果需求未完善,生成引导式追问
    if not state.is_ready_for_dev and state.audit_report:
        report = RequirementAuditReport(**state.audit_report)
        suggestions = report.get_unsatisfied_suggestions()
        
        if suggestions:
            # 构建引导提示词
            guide = (
                f"{GUIDED_QUESTION_PROMPT}\n\n"
                "需要追问的问题：\n" +
                "\n".join(f"- {s}" for s in suggestions)
            )
            
            # 调用 LLM 生成追问
            response = await llm_provider.chat_client.ainvoke(
                [SystemMessage(content=guide)] + list(state.messages)
            )
            return {"messages": [response]}
    
    # 普通对话
    response = await llm_provider.chat_client.ainvoke(state.messages)
    return {"messages": [response]}


async def dev_ready_node(state: ProjectState) -> dict:
    """开发就绪节点
    
    需求审计通过后，生成 PRD 文档。
    
    Args:
        state: 项目状态
        
    Returns:
        dict: 更新的状态（messages）
    """
    # 获取流式写入器
    writer = get_stream_writer()
    
    # 发送阶段变更事件
    writer({
        "type": "stage",
        "stage": DevelopmentStage.DEVELOPMENT,
        "status": StageStatus.ACTIVE
    })
    
    # 提取 PRD 数据
    report = state.audit_report
    prd = {
        "data_entities": report.get("data_entities", {}).get("extracted_data"),
        "roles_permissions": report.get("roles_permissions", {}).get("extracted_data"),
        "business_workflow": report.get("business_workflow", {}).get("extracted_data"),
        "ui_components": report.get("ui_components", {}).get("extracted_data"),
    }
    prd_json = json.dumps(prd, ensure_ascii=False, indent=2)
    
    # 构建 PRD 生成提示词
    prompt = (
        f"{PRD_GENERATION_PROMPT}\n\n"
        f"结构化数据：\n```json\n{prd_json}\n```"
    )
    
    # 调用 LLM 生成 PRD
    llm_provider = get_llm_provider()
    response = await llm_provider.chat_client.ainvoke(
        [SystemMessage(content=prompt)] + list(state.messages)
    )
    
    return {"messages": [response]}


# ==================== 路由函数 ====================

def route_after_audit(state: ProjectState) -> str:
    """审计后的路由决策
    
    根据审计结果决定下一步流程。
    
    Args:
        state: 项目状态
        
    Returns:
        str: 下一个节点名称（"dev_ready" 或 "chat"）
    """
    return "dev_ready" if state.is_ready_for_dev else "chat"


# ==================== 工作流构建 ====================

# 创建状态图
builder = StateGraph(ProjectState)

# 添加节点
builder.add_node("pm_audit", pm_audit_node)
builder.add_node("chat", chat_node)
builder.add_node("dev_ready", dev_ready_node)

# 设置入口点
builder.set_entry_point("pm_audit")

# 添加条件边
builder.add_conditional_edges(
    "pm_audit",
    route_after_audit,
    {
        "chat": "chat",
        "dev_ready": "dev_ready",
    }
)

# 添加结束边
builder.add_edge("chat", END)
builder.add_edge("dev_ready", END)

# 编译工作流
chat_graph = builder.compile()
