import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Thread, Message


async def create_thread(db: AsyncSession, title: str = "") -> Thread:
    thread = Thread(id=str(uuid.uuid4()), title=title)
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return thread


async def get_thread(db: AsyncSession, thread_id: str) -> Thread | None:
    result = await db.execute(select(Thread).where(Thread.id == thread_id))
    return result.scalar_one_or_none()


async def list_threads(db: AsyncSession) -> list[Thread]:
    result = await db.execute(select(Thread).order_by(Thread.created_at.desc()))
    return result.scalars().all()


async def delete_thread(db: AsyncSession, thread_id: str) -> bool:
    await db.execute(delete(Message).where(Message.thread_id == thread_id))
    result = await db.execute(delete(Thread).where(Thread.id == thread_id))
    await db.commit()
    return result.rowcount > 0


async def add_message(db: AsyncSession, thread_id: str, role: str, content: str) -> Message:
    msg = Message(thread_id=thread_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    thread = await get_thread(db, thread_id)
    if thread and not thread.title and role == "user":
        thread.title = content[:50]
        await db.commit()

    return msg


async def get_messages(db: AsyncSession, thread_id: str) -> list[Message]:
    result = await db.execute(
        select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at)
    )
    return result.scalars().all()
