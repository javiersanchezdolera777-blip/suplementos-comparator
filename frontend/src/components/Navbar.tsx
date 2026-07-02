import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="w-full py-5 px-6 md:px-12 flex justify-between items-center z-50 border-b border-white/5 bg-[#030712]/70 backdrop-blur-xl sticky top-0 supports-[backdrop-filter]:bg-[#030712]/40">
      <div className="text-2xl font-black tracking-tighter flex items-center gap-2">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-blue-500 drop-shadow-[0_0_10px_rgba(59,130,246,0.8)] group-hover:scale-110 transition-transform">⚡</span> 
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Suparator</span>
        </Link>
      </div>
      <div className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-400">
        <Link href="/#catalogo" className="hover:text-white transition-colors">Catálogo</Link>
        <Link href="#" className="hover:text-white transition-colors">Proteínas</Link>
        <Link href="#" className="hover:text-white transition-colors">Creatinas</Link>
        <div className="w-px h-4 bg-white/10"></div>
        <Link href="#" className="px-5 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white transition-all hover:scale-105 active:scale-95">
          Únete gratis
        </Link>
      </div>
    </nav>
  );
}
