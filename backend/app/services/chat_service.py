import json
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.models import ChatRequest
from app.core.graph import chat_graph
from app.db import crud


async def stream_chat(db: AsyncSession, req: ChatRequest):
    history = await crud.get_messages(db, req.thread_id)
    lc_messages = []
    for m in history:
        if m.role == "system":
            lc_messages.append(SystemMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))
        else:
            lc_messages.append(HumanMessage(content=m.content))

    await crud.add_message(db, req.thread_id, "user", req.content)
    lc_messages.append(HumanMessage(content=req.content))

    async def event_generator():
        collected = []
        try:
            async for event in chat_graph.astream_events({"messages": lc_messages}, version="v2"):
                if event["metadata"].get("langgraph_node") not in ("chat", "dev_ready"):
                    if event["event"] != "on_custom_event":
                        continue
                kind = event["event"]
                if kind == "on_custom_event":
                    yield f"data: {json.dumps(event['data'])}\n\n"
                elif kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        collected.append(chunk.content)
                        yield f"data: {json.dumps({'content': chunk.content})}\n\n"
                elif kind == "on_chat_model_end":
                    full = "".join(collected)
                    if full:
                        await crud.add_message(db, req.thread_id, "assistant", full)
                    yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
