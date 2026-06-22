import { cookies } from "next/headers";
import Sidebar from "@/components/chat/Sidebar";
import type { ThreadSummary } from "@/lib/types";

async function getThreads(): Promise<ThreadSummary[]> {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/threads`, {
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function ChatLayout({ children }: { children: React.ReactNode }) {
  const threads = await getThreads();
  return (
    <div className="flex h-screen bg-white">
      <Sidebar threads={threads} />
      {children}
    </div>
  );
}