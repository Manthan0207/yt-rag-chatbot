export type AuthMode = "login" | "signup";

export interface AuthPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  token: string;
}

export interface ThreadSummary {
  id: string;
  title: string | null;
  video_id: string;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ThreadDetail {
  id: string;
  title: string | null;
  video_id: string;
  messages: ChatMessage[];
}

export interface ThreadCreateResponse {
  thread_id: string;
  video_id: string;
  status: string;
}

export interface VideoStatusResponse {
  status: string;
}
