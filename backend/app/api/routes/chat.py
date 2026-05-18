from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models import ChatRequest, ThreadOut, MessageOut
from app.services.chat_service import stream_chat
from app.db import crud

router = APIRouter()


@router.post("/threads")
async def create_thread(db: AsyncSession = Depends(get_db)):
    thread = await crud.create_thread(db)
    return {"id": thread.id}


@router.get("/threads")
async def list_threads(db: AsyncSession = Depends(get_db)):
    threads = await crud.list_threads(db)
    return [
        ThreadOut(id=t.id, title=t.title, created_at=str(t.created_at))
        for t in threads
    ]


@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    thread = await crud.get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = await crud.get_messages(db, thread_id)
    return {
        "id": thread.id,
        "title": thread.title,
        "created_at": str(thread.created_at),
        "messages": [
            MessageOut(id=m.id, thread_id=m.thread_id, role=m.role, content=m.content, created_at=str(m.created_at))
            for m in messages
        ],
    }


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_thread(db, thread_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"ok": True}


@router.post("/chat")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    thread = await crud.get_thread(db, req.thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    return await stream_chat(db, req)
