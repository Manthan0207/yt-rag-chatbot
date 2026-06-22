"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { ChatMessage, ThreadDetail, VideoStatusResponse } from "@/lib/types";

interface Props {
  initial: ThreadDetail;
}

export default function ChatWindow({ initial }: Props) {
  const [thread, setThread] = useState<ThreadDetail>(initial);
  const [status, setStatus] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    async function checkStatus() {
      const res = await api.get<VideoStatusResponse>(`/videos/${thread.video_id}/status`);
      setStatus(res.status);
      if (res.status !== "processing") clearInterval(interval);
    }

    checkStatus();
    interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, [thread.video_id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thread.messages]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || sending || status !== "ready") return;

    const content = input;
    setInput("");
    setSending(true);

    const userMsg: ChatMessage = { role: "user", content, created_at: new Date().toISOString() };
    setThread((prev) => ({ ...prev, messages: [...prev.messages, userMsg] }));

    try {
      const reply = await api.post<ChatMessage>(`/threads/${thread.id}/messages`, { content });
      setThread((prev) => ({ ...prev, messages: [...prev.messages, reply] }));
    } catch {
      setThread((prev) => ({ ...prev, messages: prev.messages.slice(0, -1) }));
    } finally {
      setSending(false);
    }
  }


  const isProcessing = status === "processing" || status === null;
  const isFailed = status === "failed";

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <p className="text-gray-900 font-medium truncate">{thread.title ?? "New Chat"}</p>
        <div className="flex items-center gap-2">
          {isProcessing && (
            <span className="text-xs text-yellow-700 bg-yellow-50 px-3 py-1 rounded-full border border-yellow-200">
              Processing video…
            </span>
          )}
          {isFailed && (
            <span className="text-xs text-red-700 bg-red-50 px-3 py-1 rounded-full border border-red-200">
              Failed to process video
            </span>
          )}
          {status === "ready" && (
            <span className="text-xs text-green-700 bg-green-50 px-3 py-1 rounded-full border border-green-200">
              Ready
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-3xl mx-auto flex flex-col gap-6">
          {thread.messages.length === 0 && (
            <p className="text-gray-400 text-sm text-center mt-8">
              {isProcessing
                ? "Wait for the video to finish processing…"
                : "Ask anything about this video"}
            </p>
          )}
          {thread.messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-lg text-sm leading-relaxed ${msg.role === "user"
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-900"
                  }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-400 px-4 py-3 rounded-lg text-sm">
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isProcessing ? "Waiting for video to process…" : "Ask something…"}
            disabled={isProcessing || isFailed}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900 transition-all disabled:bg-gray-50 disabled:text-gray-400"
          />
          <button
            type="submit"
            disabled={sending || isProcessing || isFailed || !input.trim()}
            className="px-5 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}