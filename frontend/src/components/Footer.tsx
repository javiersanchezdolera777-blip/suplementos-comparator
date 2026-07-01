import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-slate-950/80 backdrop-blur-md py-12 mt-20 relative z-10">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex flex-col items-center md:items-start gap-2">
          <div className="text-xl font-bold tracking-tighter flex items-center gap-2">
            <span className="text-blue-500">⚡</span> Suparator
          </div>
          <p className="text-sm text-slate-500">
            © 2026 Suparator. Todos los derechos reservados.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-8 text-sm font-medium text-slate-400">
          <Link href="/about" className="hover:text-blue-400 transition-colors">Quiénes Somos</Link>
          <Link href="/legal" className="hover:text-blue-400 transition-colors">Aviso Legal</Link>
          <Link href="/privacy" className="hover:text-blue-400 transition-colors">Política de Privacidad</Link>
        </div>
      </div>
    </footer>
  );
}
