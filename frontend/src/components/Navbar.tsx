import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="w-full py-6 px-8 flex justify-between items-center z-50 border-b border-white/5 bg-slate-950/50 backdrop-blur-md sticky top-0">
      <div className="text-xl font-bold tracking-tighter flex items-center gap-2">
        <Link href="/">
          <span className="text-blue-500">⚡</span> Suparator
        </Link>
      </div>
      <div className="hidden md:flex gap-8 text-sm font-medium text-slate-300">
        <Link href="/#catalogo" className="hover:text-white transition-colors">Catálogo</Link>
        <Link href="#" className="hover:text-white transition-colors">Proteínas</Link>
        <Link href="#" className="hover:text-white transition-colors">Creatinas</Link>
      </div>
    </nav>
  );
}
