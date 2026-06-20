from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import Video
from app.schema import VideoStatusOut

router = APIRouter()


@router.get("/{video_id}/status", response_model=VideoStatusOut)
def get_video_status(
    video_id: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoStatusOut(status=video.status)