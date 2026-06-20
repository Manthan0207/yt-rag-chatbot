from sqlalchemy.orm import Session
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.database import SessionLocal
from app.models import Message, Thread
from app.services.pinecone_service import get_index

llm = ChatOpenAI(model="gpt-4o-mini")
title_llm = ChatOpenAI(model="gpt-4o-mini")


def run_chat_turn(db: Session, thread: Thread, user_message_content: str) -> str:
    index = get_index()
    retriever = index.as_retriever(
        search_kwargs={
            "k": 3,
            "filter": {"video_id": {"$eq": thread.video_id}},
            "namespace": settings.pinecone_namespace,
        }
    )

    context_docs = retriever.invoke(user_message_content)
    context_text = "\n\n".join(
        doc.page_content if hasattr(doc, "page_content") else str(doc)
        for doc in context_docs
    )

    messages = (
        db.query(Message)
        .filter(Message.thread_id == thread.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    chat_messages = [
        SystemMessage(
            content=(
                "You answer only from the provided transcript context. "
                "Do not use general knowledge. If the answer is not in context, say you could not find it in the video."
            )
        )
    ]

    for message in messages:
        if message.role == "user":
            chat_messages.append(HumanMessage(content=message.content))
        else:
            chat_messages.append(AIMessage(content=message.content))

    chat_messages.append(
        HumanMessage(
            content=(
                f"Transcript context:\n{context_text}\n\n"
                f"User question:\n{user_message_content}"
            )
        )
    )

    response = llm.invoke(chat_messages)
    return response.content


def generate_thread_title(thread_id: str):
    db: Session = SessionLocal()
    try:
        thread = db.query(Thread).filter(Thread.id == thread_id).first()
        if not thread or thread.title is not None:
            return

        messages = (
            db.query(Message)
            .filter(Message.thread_id == thread.id)
            .order_by(Message.created_at.asc())
            .limit(2)
            .all()
        )
        if len(messages) < 2:
            return

        title_prompt = [
            SystemMessage(content="Create a short 4 to 6 word title for this conversation."),
            HumanMessage(
                content=f"User: {messages[0].content}\nAssistant: {messages[1].content}"
            ),
        ]
        title = title_llm.invoke(title_prompt).content.strip().strip('"')
        thread.title = title[:80]
        db.commit()
    finally:
        db.close()
