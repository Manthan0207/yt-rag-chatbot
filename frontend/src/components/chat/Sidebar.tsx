"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ThreadSummary } from "@/lib/types";

interface Props {
  threads: ThreadSummary[];
}

export default function Sidebar({ threads }: Props) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    document.cookie = "token=; max-age=0; path=/";
    router.push("/");
  }

  return (
    <aside className="w-64 h-screen flex flex-col border-r border-gray-200 bg-gray-50">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <span className="font-semibold text-gray-900">YT Chatbot</span>
          <button
            onClick={logout}
            className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Logout
          </button>
        </div>
        <Link
          href="/chat"
          className="flex items-center justify-center w-full py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-100 text-gray-700 text-sm font-medium transition-colors"
        >
          + New Chat
        </Link>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 flex flex-col gap-0.5">
        {threads.length === 0 && (
          <p className="text-gray-400 text-xs px-3 py-4 text-center">No chats yet</p>
        )}
        {threads.map((t) => {
          const active = pathname === `/chat/${t.id}`;
          return (
            <Link
              key={t.id}
              href={`/chat/${t.id}`}
              className={`px-3 py-2 rounded-lg text-sm truncate transition-colors ${active
                ? "bg-gray-200 text-gray-900 font-medium"
                : "text-gray-600 hover:bg-gray-200/50 hover:text-gray-900"
                }`}
            >
              {t.title ?? `Video: ${t.video_id}`}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}