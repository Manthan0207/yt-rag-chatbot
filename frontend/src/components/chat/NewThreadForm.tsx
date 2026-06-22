"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { ThreadCreateResponse } from "@/lib/types";

export default function NewThreadForm() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;
    setError(null);
    setLoading(true);
    try {
      const data = await api.post<ThreadCreateResponse>("/threads", { youtube_url: url });
      router.push(`/chat/${data.thread_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex items-center justify-center p-8 bg-white">
      <div className="w-full max-w-lg">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">New Chat</h1>
        <p className="text-gray-500 text-sm mb-6">Paste a YouTube link to start chatting with the video</p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900 transition-all"
          />
          {error && (
            <p className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded-lg border border-red-200">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="py-3 rounded-lg bg-gray-900 text-white font-medium text-sm hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Creating…" : "Start Chat"}
          </button>
        </form>
      </div>
    </div>
  );
}