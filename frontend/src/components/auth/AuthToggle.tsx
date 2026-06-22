import type { AuthMode } from "@/lib/types";

interface Props {
    mode: AuthMode;
    onChange: (mode: AuthMode) => void;
}

export default function AuthToggle({ mode, onChange }: Props) {
    return (
        <div className="flex rounded-lg bg-gray-100 p-1 mb-6">
            {(["login", "signup"] as AuthMode[]).map((m) => (
                <button
                    key={m}
                    type="button"
                    onClick={() => onChange(m)}
                    className={`flex-1 py-2 rounded-md text-sm font-medium capitalize transition-all ${mode === m
                            ? "bg-white text-gray-900 shadow-sm"
                            : "text-gray-500 hover:text-gray-700"
                        }`}
                >
                    {m}
                </button>
            ))}
        </div>
    );
}