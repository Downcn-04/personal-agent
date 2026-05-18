from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Thread(Base):
    __tablename__ = "threads"

    id = Column(Text, primary_key=True)
    title = Column(Text, default="")
    created_at = Column(TIMESTAMP, server_default=func.now())

    messages = relationship("Message", back_populates="thread", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Text, ForeignKey("threads.id"), nullable=False, index=True)
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    thread = relationship("Thread", back_populates="messages")
