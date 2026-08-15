import React from 'react';

export default function TelegramBanner() {
  return (
    <div className="bg-slate-900 text-slate-100 text-xs sm:text-sm py-2 px-4 flex flex-col sm:flex-row justify-center items-center gap-1 sm:gap-3 w-full border-b border-slate-800 z-50">
      <span className="flex items-center gap-2 font-medium">
        <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.04.01.12 0 .18z" />
        </svg>
        ¿Quieres enterarte de chollos flash antes que nadie?
      </span>
      <a
        href="https://t.me/TusSuplementosChollos"
        target="_blank"
        rel="noopener noreferrer"
        className="font-bold text-blue-400 hover:text-blue-300 underline decoration-blue-400/30 underline-offset-4 transition-colors"
      >
        Únete gratis al canal →
      </a>
    </div>
  );
}
