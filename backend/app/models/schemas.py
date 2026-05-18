from pydantic import BaseModel


class ChatRequest(BaseModel):
    content: str
    thread_id: str


class ThreadOut(BaseModel):
    id: str
    title: str
    created_at: str


class MessageOut(BaseModel):
    id: int
    thread_id: str
    role: str
    content: str
    created_at: str
