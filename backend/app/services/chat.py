import sqlite3
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, RemoveMessage,AIMessageChunk 
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import SessionLocal
from app.models import Message, Thread
from app.services.pinecone_service import get_index
from langchain_core.runnables import RunnableConfig
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEndpointEmbeddings, ChatHuggingFace

_llm_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    huggingfacehub_api_token=settings.hf_token,
    max_new_tokens=500,
    temperature=0.3,
)
_title_llm_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    huggingfacehub_api_token=settings.hf_token,
    max_new_tokens=20,
    temperature=0.3,
)
llm = ChatHuggingFace(llm=_llm_endpoint)
title_llm = ChatHuggingFace(llm=_title_llm_endpoint)
embedding_model = HuggingFaceEndpointEmbeddings(
    model="BAAI/bge-large-en-v1.5",
    huggingfacehub_api_token=settings.hf_token,
)

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    summary : str 


def chat_node(state: ChatState, config: RunnableConfig) -> dict:
    video_id = config["configurable"]["video_id"]
    query = state["messages"][-1].content
    
    summary = state.get("summary" , "")

    query_vector = embedding_model.embed_query(query)
    index = get_index()
    results = index.query(
        vector=query_vector,
        top_k=8,
        filter={"video_id": {"$eq": video_id}},
        namespace=settings.pinecone_namespace,
        include_metadata=True,
    )
    context = "\n\n".join(
        match.metadata.get("text", "") for match in results.matches
    )

    prompt = PromptTemplate(
        template=(
            "You are a helpful assistant answering questions about a YouTube video.\n"
            "Use the transcript context below to answer the user's question.\n"
            "Use the conversation history to answer conversational questions.\n"
            "For greetings or small talk, respond naturally.\n"
            "Only say you could not find it in the video if the context truly has no relevant information.\n\n"
            "Chat Summary :\n {summary}\n\n"
            "Last Few Queries and ans : \n {history}"
            "Context:\n{context}\n\n"
            "User question: {query}"
        ),
        input_variables=["query", "context","summary","history"],
    )
    chain = prompt | llm | StrOutputParser()
    output = chain.invoke({"query": query, "context": context,"summary" : summary, "history" : state["messages"]})

    return {"messages": [AIMessage(content=output)]}


def do_summarize(state) :
    return len(state["messages"]) >= 20

def summary_node(state):
    existing_summary = state.get("summary", "")

    messages = state["messages"]

    messages_to_summarize = messages[:-4]

    chat_text = []

    for msg in messages_to_summarize:
        role = "User" if isinstance(msg, HumanMessage) else "AI"
        chat_text.append(f"{role}: {msg.content}")

    chat_text = "\n".join(chat_text)

    prompt = PromptTemplate.from_template(
        """
You are a conversation summarizer.

You are given:

1. Existing summary
2. New conversation messages

Update the summary by:
- Keeping important facts
- Keeping user preferences
- Keeping important questions and answers
- Removing redundancy
- Writing a concise summary

Existing Summary:
{existing_summary}

New Messages:
{new_messages}

Updated Summary:
"""
    )

    chain = prompt | llm | StrOutputParser()

    updated_summary = chain.invoke({
        "existing_summary": existing_summary,
        "new_messages": chat_text,
    })

    return {
        "summary": updated_summary,
        "messages": [
            RemoveMessage(id=msg.id)
            for msg in messages_to_summarize
        ]
    }
    
    

graph_builder = StateGraph(ChatState)
graph_builder.add_node("chat", chat_node)
graph_builder.add_node("summarize" , summary_node)
graph_builder.add_edge(START, "chat")
graph_builder.add_conditional_edges(
    "chat" , do_summarize , {
        True : "summarize" , 
        False : END
    }
)
graph_builder.add_edge("summarize", END)
graph = graph_builder.compile(checkpointer=checkpointer)


def run_chat_turn(db: Session, thread: Thread, user_message_content: str) -> str:
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_message_content)]},
        config={
            "configurable": {
                "thread_id": thread.id,
                "video_id": thread.video_id,
            }
        },
    )
    return result["messages"][-1].content


# NOTE: stream_chat_turn is commented out because HuggingFace third-party inference
# providers (novita, featherless-ai, etc.) do not support streaming for the
# conversational task. To enable streaming, switch to a self-hosted model or OpenAI.

# def stream_chat_turn(thread: Thread, user_message_content: str):
#     for chunk, metadata in graph.stream(
#         {"messages": [HumanMessage(content=user_message_content)]},
#         config={
#             "configurable": {
#                 "thread_id": thread.id,
#                 "video_id": thread.video_id,
#             }
#         },
#         stream_mode="messages",
#     ):
#         if isinstance(chunk, AIMessageChunk):
#             yield chunk.content

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
            HumanMessage(
                content=f"Create a short 4 to 6 word title for this conversation.\n\nUser: {messages[0].content}\nAssistant: {messages[1].content}"
            )
        ]
        title = title_llm.invoke(title_prompt).content.strip().strip('"')
        thread.title = title[:80]
        db.commit()
    finally:
        db.close()
