import type { AuthPayload } from "@/lib/types";

interface Props {
    payload: AuthPayload;
    error: string | null;
    submitting: boolean;
    submitLabel: string;
    onChange: (payload: AuthPayload) => void;
    onSubmit: () => void;
}

export default function AuthForm({ payload, error, submitting, submitLabel, onChange, onSubmit }: Props) {
    return (
        <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Email</label>
                <input
                    type="email"
                    required
                    autoComplete="email"
                    value={payload.email}
                    onChange={(e) => onChange({ ...payload, email: e.target.value })}
                    placeholder="you@example.com"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900 transition-all"
                />
            </div>
            <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700">Password</label>
                <input
                    type="password"
                    required
                    autoComplete="current-password"
                    value={payload.password}
                    onChange={(e) => onChange({ ...payload, password: e.target.value })}
                    placeholder="••••••••"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-1 focus:ring-gray-900 transition-all"
                />
            </div>
            {error && (
                <p className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded-lg border border-red-200">
                    {error}
                </p>
            )}
            <button
                type="submit"
                disabled={submitting}
                className="mt-1 py-2.5 rounded-lg bg-gray-900 text-white font-medium text-sm hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
                {submitting ? "Please wait…" : submitLabel}
            </button>
        </form>
    );
}