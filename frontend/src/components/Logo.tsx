import Link from 'next/link';

interface LogoProps {
  className?: string;
  lightMode?: boolean;
}

export default function Logo({ className = "", lightMode = false }: LogoProps = {}) {
  return (
    <Link className={`flex items-center gap-2.5 group focus:outline-none ${className}`} href="/">
      {/* Isotipo TS */}
      <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200 flex-shrink-0">
        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          className="w-5 h-5 text-white stroke-current stroke-[2.5]" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          {/* Trazos vectoriales limpios TS / Energía */}
          <path d="M4 6h10" />
          <path d="M9 6v12" />
          <path d="M14 13c1.5-1 3.5-1 4.5.5s.5 3.5-1 4.5-3.5 1-4.5-.5" />
        </svg>
      </div>

      {/* Tipografía de Marca */}
      <div className="flex items-baseline text-xl tracking-tight select-none">
        <span className={`font-semibold ${lightMode ? "text-slate-300" : "text-slate-700 dark:text-slate-200"}`}>
          Tus
        </span>
        <span className={`font-extrabold ml-1 ${lightMode ? "text-white" : "text-slate-900 dark:text-white"}`}>
          Suplementos
        </span>
        <span className="text-blue-600 font-extrabold text-xl leading-none ml-0.5">
          .
        </span>
      </div>
    </Link>
  );
}
