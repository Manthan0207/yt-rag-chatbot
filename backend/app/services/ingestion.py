import re
from youtube_transcript_api import YouTubeTranscriptApi
from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.core.config import settings
from app.database import SessionLocal
from app.models import Video
from app.services.pinecone_service import get_index

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")


def extract_video_id(youtube_url: str) -> str:
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    raise ValueError("Could not extract video id from URL")


def chunk_transcript(snippets, max_chunk_duration: int = 45):
    chunks = []
    current_text = []
    chunk_start = snippets[0].start

    for snip in snippets:
        current_text.append(snip.text)
        if (snip.start + snip.duration) - chunk_start >= max_chunk_duration:
            chunks.append(
                {
                    "text": " ".join(current_text),
                    "start": chunk_start,
                }
            )
            current_text = []
            chunk_start = snip.start + snip.duration

    if current_text:
        chunks.append({"text": " ".join(current_text), "start": chunk_start})

    return chunks


def ingest_video_for_url(youtube_url: str):
    db: Session = SessionLocal()
    try:
        video_id = extract_video_id(youtube_url)
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            video = Video(id=video_id, youtube_url=youtube_url, status="processing")
            db.add(video)
            db.commit()
            db.refresh(video)

        if video.status == "ready":
            return

        try:
            transcript = YouTubeTranscriptApi().fetch(video_id).snippets
            chunks = chunk_transcript(transcript, 45)

            docs = [
                Document(
                    page_content=chunk["text"],
                    metadata={
                        "video_id": video_id,
                        "start": chunk["start"],
                        "text": chunk["text"],
                    },
                )
                for chunk in chunks
            ]

            index = get_index()
            vectors = embedding_model.embed_documents([doc.page_content for doc in docs])

            upsert_payload = []
            for i, doc in enumerate(docs):
                upsert_payload.append(
                    {
                        "id": f"{video_id}-{i}",
                        "values": vectors[i],
                        "metadata": doc.metadata,
                    }
                )

            index.upsert(vectors=upsert_payload, namespace=settings.pinecone_namespace)

            video.status = "ready"
            db.commit()
        except Exception:
            video.status = "failed"
            db.commit()
            raise
    finally:
        db.close()