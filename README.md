# YT Chatbot

A full-stack AI chatbot that lets you chat with any YouTube video using its transcript. Paste a YouTube link, wait for the video to be processed, then ask anything about the video content.

## How It Works

1. User pastes a YouTube URL
2. Backend fetches the transcript using `youtube-transcript-api`
3. Transcript is chunked and embedded using `BAAI/bge-large-en-v1.5` (HuggingFace)
4. Embeddings are stored in Pinecone vector database
5. User asks questions — relevant transcript chunks are retrieved and passed to the LLM
6. `Qwen2.5-7B-Instruct` (via HuggingFace Inference API) answers based only on the transcript context
7. Conversation memory is managed by LangGraph with a SQLite checkpointer

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

## Project Structure

```
YT_TRANSCRIPT/
├── backend/
│   ├── app/
│   │   ├── core/         # config, settings
│   │   ├── routers/      # auth, threads, videos
│   │   ├── services/     # chat (LangGraph), ingestion, pinecone
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schema.py
│   │   ├── deps.py
│   │   └── security.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages and layouts
│       ├── components/   # auth, chat components
│       ├── lib/          # api client, types
│       └── middleware.ts # JWT auth guard
└── youtube_transcript.ipynb  # original prototype notebook
```

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

## Streaming

Streaming is currently not supported. HuggingFace third-party inference providers (novita, featherless-ai, etc.) do not support token streaming for the conversational task. To enable streaming, switch to a self-hosted model or OpenAI (`gpt-4o-mini` works out of the box with LangGraph streaming).

## Deploying

Both services have Dockerfiles. Deploy to any container platform (Render, Railway, Fly.io etc.).

- Backend — set root dir to `backend`, add all env vars from `backend/.env`
- Frontend — set root dir to `frontend`, set `NEXT_PUBLIC_API_URL` to your deployed backend URL

> SQLite is used for simplicity. On platforms with ephemeral storage (Render free tier), data will reset on redeploy. For production persistence switch to PostgreSQL.
