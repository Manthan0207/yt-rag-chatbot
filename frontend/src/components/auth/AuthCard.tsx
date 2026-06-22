"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { AuthMode, AuthPayload, TokenResponse } from "@/lib/types";
import AuthToggle from "./AuthToggle";
import AuthForm from "./AuthForm";

const empty: AuthPayload = { email: "", password: "" };

export default function AuthCard() {
    const router = useRouter();
    const [mode, setMode] = useState<AuthMode>("login");
    const [payload, setPayload] = useState<AuthPayload>(empty);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    async function handleSubmit() {
        setError(null);
        setSubmitting(true);
        try {
            const endpoint = mode === "login" ? "/auth/login" : "/auth/signup";
            const data = await api.post<TokenResponse>(endpoint, payload);
            document.cookie = `token=${data.token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
            router.push("/chat");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <div className="w-full max-w-md bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <div className="mb-8">
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">YT Chatbot</h1>
                <p className="text-gray-500 text-sm">Chat with any YouTube video</p>
            </div>
            <AuthToggle mode={mode} onChange={(m) => { setMode(m); setError(null); }} />
            <AuthForm
                payload={payload}
                error={error}
                submitting={submitting}
                submitLabel={mode === "login" ? "Sign in" : "Create account"}
                onChange={setPayload}
                onSubmit={handleSubmit}
            />
        </div>
    );
}