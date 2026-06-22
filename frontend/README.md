# YT Chatbot — Frontend

Next.js 16 frontend for the YT Chatbot project.

## Stack

- Next.js 16 (App Router)
- Tailwind CSS v4
- TypeScript
- `jose` for JWT verification in middleware

## Setup

```bash
npm install
npm run dev
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
SECRET_KEY=your_secret_key
```

`SECRET_KEY` must match the backend `SECRET_KEY` exactly.

## Architecture

- `src/app/(auth)/page.tsx` — login/signup page (Server Component shell, CSR form)
- `src/app/chat/layout.tsx` — sidebar layout, fetches threads server-side on every render
- `src/app/chat/page.tsx` — new thread form (paste YouTube URL)
- `src/app/chat/[threadId]/page.tsx` — chat window, fetches thread server-side then hydrates client
- `src/middleware.ts` — JWT validation on every request, redirects unauthenticated users to `/`
- `src/lib/api.ts` — fetch wrapper, auto-attaches token from cookie, handles 401

## Building

```bash
npm run build
npm start
```
