from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


def uuid_str() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=uuid_str)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    threads = relationship("Thread", back_populates="user", cascade="all, delete-orphan")
    
    
class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)  # youtube video_id
    youtube_url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="processing")  # processing | ready | failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    threads = relationship("Thread", back_populates="video")

class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True, default=uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False, index=True)
    title = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="threads")
    video = relationship("Video", back_populates="threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")
    
class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=uuid_str)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    thread = relationship("Thread", back_populates="messages")