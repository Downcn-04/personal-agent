import json
from langgraph.graph import StateGraph, END
from langgraph.config import get_stream_writer
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from app.core.llm import chat_llm, audit_llm
from app.agents.pm_agents import PM_AUDIT_PROMPT, RequirementAuditReport


class ProjectState(BaseModel):
    messages: list = []
    audit_report: dict = {}
    is_ready_for_dev: bool = False


async def pm_audit_node(state: ProjectState) -> dict:
    writer = get_stream_writer()
    writer({"type": "stage", "stage": "requirements", "status": "active"})

    schema_json = json.dumps(RequirementAuditReport.model_json_schema(), ensure_ascii=False)
    prompt = PM_AUDIT_PROMPT + f"\n\n请严格按照以下JSON Schema输出审计结果：\n```json\n{schema_json}\n```"
    audit_messages = [SystemMessage(content=prompt)] + list(state.messages)

    json_llm = audit_llm.bind(response_format={"type": "json_object"})
    response = await json_llm.ainvoke(audit_messages)
    report = RequirementAuditReport.model_validate_json(response.content)

    writer({"type": "stage_data", "stage": "requirements", "data": report.model_dump()})

    if report.all_satisfied:
        writer({"type": "stage", "stage": "requirements", "status": "completed"})
    print('all',report.all_satisfied)
    return {
        "audit_report": report.model_dump(),
        "is_ready_for_dev": report.all_satisfied,
    }


async def chat_node(state: ProjectState) -> dict:
    if not state.is_ready_for_dev and state.audit_report:
        report = RequirementAuditReport(**state.audit_report)
        suggestions = report.get_unsatisfied_suggestions()
        if suggestions:
            guide = (
                "你是资深PM。根据对用户需求的审计，请以专业且引导式的口吻，"
                "向用户提出以下追问，帮助完善需求：\n" + "\n".join(f"- {s}" for s in suggestions)
            )
            response = await chat_llm.ainvoke([SystemMessage(content=guide)] + list(state.messages))
            return {"messages": [response]}

    response = await chat_llm.ainvoke(state.messages)
    return {"messages": [response]}


async def dev_ready_node(state: ProjectState) -> dict:
    writer = get_stream_writer()
    writer({"type": "stage", "stage": "development", "status": "active"})

    report = state.audit_report
    prd = {
        "data_entities": report.get("data_entities", {}).get("extracted_data"),
        "roles_permissions": report.get("roles_permissions", {}).get("extracted_data"),
        "business_workflow": report.get("business_workflow", {}).get("extracted_data"),
        "ui_components": report.get("ui_components", {}).get("extracted_data"),
    }
    prd_json = json.dumps(prd, ensure_ascii=False, indent=2)
    prompt = f"需求审计已全部通过。以下是提取的PRD结构化数据，请将其整理为一份专业的PRD文档输出给用户：\n\n```json\n{prd_json}\n```"
    response = await chat_llm.ainvoke([SystemMessage(content=prompt)] + list(state.messages))
    return {"messages": [response]}


def route_after_audit(state: ProjectState) -> str:
    return "dev_ready" if state.is_ready_for_dev else "chat"


builder = StateGraph(ProjectState)
builder.add_node("pm_audit", pm_audit_node)
builder.add_node("chat", chat_node)
builder.add_node("dev_ready", dev_ready_node)

builder.set_entry_point("pm_audit")
builder.add_conditional_edges("pm_audit", route_after_audit, {
    "chat": "chat",
    "dev_ready": "dev_ready",
})
builder.add_edge("chat", END)
builder.add_edge("dev_ready", END)

chat_graph = builder.compile()
