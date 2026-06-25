# YT Chatbot

A full-stack AI chatbot that lets you have a conversation with any YouTube video. Paste a link, and the system turns the video's transcript into a searchable knowledge base, then answers questions grounded strictly in that content, with full conversation memory across follow-up questions.

---

## What it does

1. User pastes a YouTube URL
2. Backend fetches the transcript and processes it in the background (status is polled, not blocking)
3. Transcript is chunked and embedded (`BAAI/bge-large-en-v1.5`), then stored in Pinecone
4. User asks a question — the system retrieves only the relevant transcript chunks for that specific video
5. An LLM (`Qwen2.5-7B-Instruct`) answers using only that retrieved context — never general knowledge
6. Conversation history persists per thread, so follow-up questions work naturally
7. A user can run multiple chat threads, each tied to a different video, all saved across sessions

## Architecture

The system is built around one core split: **video knowledge is separate from conversation state.**

```
┌──────────────────────────┐        ┌───────────────────────────┐
│   VIDEO KNOWLEDGE BASE   │        │       CHAT THREAD         │
│   (processed once)       │ ◄──────│     (created per chat)    │
│                          │video_id│                           │
│  transcript → chunks     │        │  thread_id, user_id       │
│  → embeddings → Pinecone │        │  message history (SQLite) │
│  shared across ALL users │        │  owned by one user        │
└──────────────────────────┘        └───────────────────────────┘
```

A video is ingested **once**, regardless of how many users or threads reference it — re-pasting a link that's already been processed skips straight to chat. Retrieval is scoped per-video via Pinecone metadata filtering on a single shared index, so one user's video never leaks into another user's answers.

## Design decisions

A few choices made deliberately, not by default:

- **One shared Pinecone index, filtered by `video_id` metadata** — rather than a separate index per video. Vector DB plans typically cap index count, so this scales to many videos without hitting that ceiling, while still keeping each video's search space isolated at query time.
- **Knowledge base is shared across users, conversations are not** — if two users paste the same link, the transcript is embedded once and reused. Avoids redundant embedding cost and re-processing time for popular videos.
- **`video_id` and `thread_id` are routing/identity, not conversation state** — they're passed through LangGraph's `config`, not its `state`. State stays minimal (just message history), which keeps the graph itself simple and avoids stale-flag bugs from carrying setup parameters through every turn.
- **Conversation summarization after 20 messages** — keeps long-running threads from silently overflowing the LLM's context window as a conversation grows.

## Stack

**Backend**
- FastAPI — REST API
- LangGraph — conversation graph with memory and summarization
- LangChain + HuggingFace — LLM and embeddings
- Pinecone — vector store for transcript embeddings
- SQLite — user data, threads, messages (`app.db`) and LangGraph checkpoints (`checkpoints.db`)
- JWT — authentication

**Frontend**
- Next.js 16 — App Router with Server and Client Components
- Tailwind CSS v4
- TypeScript

## Features

- JWT auth (signup / login) with cookie-based token storage
- Auth guard via Next.js middleware — validates JWT on every page render
- YouTube transcript ingestion with background processing
- RAG-based chat — answers grounded in transcript context
- Conversation summarization after 20 messages to manage context window
- Thread history persisted in DB and accessible across sessions
- Video processing status polling


## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 --env-file .env
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

**`backend/.env`**
```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=youtube-ai-chatbot
PINECONE_NAMESPACE=shared
ACCESS_TOKEN_EXPIRE_MINUTES=10080
HF_TOKEN=your_huggingface_token
```

**`frontend/.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
SECRET_KEY=your_secret_key
```
> `SECRET_KEY` must be the same in both frontend and backend — used for JWT signing and verification.

## Deploying

Both services have Dockerfiles. Deploy to any container platform (Render, Railway, Fly.io etc.).

- Backend — set root dir to `backend`, add all env vars from `backend/.env`
- Frontend — set root dir to `frontend`, set `NEXT_PUBLIC_API_URL` to your deployed backend URL
