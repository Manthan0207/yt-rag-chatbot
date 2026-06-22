import re
from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi
from sqlalchemy.orm import Session
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.documents import Document
from app.core.config import settings
from app.database import SessionLocal
from app.models import Video
from app.services.pinecone_service import get_index

embedding_model = HuggingFaceEndpointEmbeddings(
    model="BAAI/bge-large-en-v1.5",
    huggingfacehub_api_token=settings.hf_token,
)


def extract_video_id(youtube_url: str) -> str:
    normalized_url = youtube_url.strip()
    parsed_url = urlparse(normalized_url if "://" in normalized_url else f"https://{normalized_url}")

    if parsed_url.hostname in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
        query_video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        if query_video_id:
            return query_video_id

        path_match = re.search(r"/shorts/([a-zA-Z0-9_-]{11})", parsed_url.path)
        if path_match:
            return path_match.group(1)

        embed_match = re.search(r"/embed/([a-zA-Z0-9_-]{11})", parsed_url.path)
        if embed_match:
            return embed_match.group(1)

    if parsed_url.hostname == "youtu.be":
        path_match = re.search(r"^/([a-zA-Z0-9_-]{11})", parsed_url.path)
        if path_match:
            return path_match.group(1)

    raw_match = re.search(r"([a-zA-Z0-9_-]{11})", normalized_url)
    if raw_match:
        return raw_match.group(1)

    raise ValueError(f"Could not extract video id from URL: {youtube_url}")


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
            transcript = YouTubeTranscriptApi().fetch(video_id, languages=["en", "hi"]).snippets
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
