import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import ChatWindow from "@/components/chat/ChatWindow";
import type { ThreadDetail } from "@/lib/types";

async function getThread(threadId: string): Promise<ThreadDetail | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/threads/${threadId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function ThreadPage({ params }: { params: Promise<{ threadId: string }> }) {
  const { threadId } = await params;
  const thread = await getThread(threadId);
  if (!thread) notFound();
  return <ChatWindow initial={thread} />;
}
