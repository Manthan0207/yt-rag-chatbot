from datetime import datetime
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    token: str


class AuthPayload(BaseModel):
    email: EmailStr
    password: str


class ThreadCreateRequest(BaseModel):
    youtube_url: str


class ThreadListItem(BaseModel):
    id: str
    title: str | None
    video_id: str
    created_at: datetime


class MessageCreateRequest(BaseModel):
    content: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ThreadDetailOut(BaseModel):
    id: str
    title: str | None
    video_id: str
    messages: list[MessageOut]


class ThreadCreateResponse(BaseModel):
    thread_id: str
    video_id: str
    status: str


class VideoStatusOut(BaseModel):
    status: str