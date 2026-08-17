"use client";

import { useState } from "react";

export default function NewsletterForm() {
    const [email, setEmail] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("loading");

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/newsletter/subscribe`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || "Ha ocurrido un error al suscribirse.");
            }

            setStatus("success");
            setMessage("¡Suscripción completada!");
            setEmail("");
        } catch (error: any) {
            setStatus("error");
            setMessage(error.message);
        }
    };

    return (
        <div className="w-full flex flex-col gap-4">
            <div>
                <h4 className="text-white font-bold tracking-wide uppercase text-sm mb-2">Newsletter</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                    Recibe alertas de bajadas de precio.
                </p>
            </div>

            {status === "success" ? (
                <div className="text-xs text-emerald-400 border border-emerald-500/20 bg-emerald-500/10 p-2.5 rounded-lg font-medium inline-block">
                    {message}
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="flex flex-col gap-2.5 w-full">
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Tu correo electrónico..."
                        className="w-full bg-[#0a0f1d] text-slate-200 placeholder-slate-500 px-3 py-2 rounded-lg border border-slate-800 focus:border-slate-600 focus:ring-1 focus:ring-slate-600 outline-none transition-all text-xs"
                        disabled={status === "loading"}
                    />
                    <button
                        type="submit"
                        disabled={status === "loading"}
                        className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-slate-700"
                    >
                        {status === "loading" ? "Procesando..." : "Suscribirme"}
                    </button>
                </form>
            )}

            {status === "error" && (
                <p className="text-red-400 text-xs font-medium">{message}</p>
            )}
        </div>
    );
}