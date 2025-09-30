from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from datetime import datetime
import uuid
from database import Base, engine, get_db

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user")


class ChatSession(Base):
    __tablename__ = "session"

    session_id = Column(String, primary_key=True, index=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)  # يمكن أن يكون فارغ (session مؤقت)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    history = relationship("ChatHistory", back_populates="session")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("session.session_id"), nullable=False, index=True)
    is_system_prompt = Column(Boolean, default=False)
    system_prompt = Column(String, nullable=True)
    message_user = Column(String, nullable=True)
    response_bot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="history")
