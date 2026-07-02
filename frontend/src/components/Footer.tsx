import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/5 bg-[#030712] py-12 mt-auto relative z-10">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex flex-col items-center md:items-start gap-2">
          <div className="text-xl font-black tracking-tighter flex items-center gap-2">
            <span className="text-blue-500 drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]">⚡</span> 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Suparator</span>
          </div>
          <p className="text-sm text-slate-500 font-medium">
            © 2026 Suparator. Todos los derechos reservados.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-8 text-sm font-semibold text-slate-400">
          <Link href="/about" className="hover:text-white transition-colors">Quiénes Somos</Link>
          <Link href="/legal" className="hover:text-white transition-colors">Aviso Legal</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Política de Privacidad</Link>
        </div>
      </div>
    </footer>
  );
}
