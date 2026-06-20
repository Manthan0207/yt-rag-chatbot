from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import Message, Thread, User, Video
from app.schema import MessageCreateRequest, MessageOut, ThreadCreateRequest, ThreadCreateResponse, ThreadDetailOut, ThreadListItem
from app.services.ingestion import ingest_video_for_url, extract_video_id
from app.services.chat import run_chat_turn, generate_thread_title

router = APIRouter()


@router.post("", response_model=ThreadCreateResponse)
def create_thread(
    payload: ThreadCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video_id = extract_video_id(payload.youtube_url)
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        video = Video(id=video_id, youtube_url=payload.youtube_url, status="processing")
        db.add(video)
        db.commit()
        db.refresh(video)
        background_tasks.add_task(ingest_video_for_url, payload.youtube_url)
    elif video.status != "ready":
        background_tasks.add_task(ingest_video_for_url, payload.youtube_url)

    thread = Thread(user_id=current_user.id, video_id=video_id)
    db.add(thread)
    db.commit()
    db.refresh(thread)

    return ThreadCreateResponse(thread_id=thread.id, video_id=video_id, status=video.status)


@router.get("", response_model=list[ThreadListItem])
def list_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    threads = (
        db.query(Thread)
        .filter(Thread.user_id == current_user.id)
        .order_by(Thread.created_at.desc())
        .all()
    )
    return [
        ThreadListItem(
            id=thread.id,
            title=thread.title,
            video_id=thread.video_id,
            created_at=thread.created_at,
        )
        for thread in threads
    ]


@router.get("/{thread_id}", response_model=ThreadDetailOut)
def get_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    if thread.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    messages = (
        db.query(Message)
        .filter(Message.thread_id == thread.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return ThreadDetailOut(
        id=thread.id,
        title=thread.title,
        video_id=thread.video_id,
        messages=[
            MessageOut(role=message.role, content=message.content, created_at=message.created_at)
            for message in messages
        ],
    )


@router.post("/{thread_id}/messages", response_model=MessageOut)
def send_message(
    thread_id: str,
    payload: MessageCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    if thread.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    user_message = Message(thread_id=thread.id, role="user", content=payload.content)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    assistant_content = run_chat_turn(
        db=db,
        thread=thread,
        user_message_content=payload.content,
    )

    assistant_message = Message(thread_id=thread.id, role="assistant", content=assistant_content)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    if thread.title is None:
        background_tasks.add_task(generate_thread_title, thread.id)

    return MessageOut(
        role=assistant_message.role,
        content=assistant_message.content,
        created_at=assistant_message.created_at,
    )