import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 font-sans text-white overflow-hidden relative">
      {/* Background gradients and glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/30 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px] pointer-events-none" />

      {/* Navigation (Simple placeholder for Hero context) */}
      <nav className="w-full py-6 px-8 flex justify-between items-center z-10 border-b border-white/5 bg-slate-950/50 backdrop-blur-md">
        <div className="text-xl font-bold tracking-tighter flex items-center gap-2">
          <span className="text-blue-500">⚡</span> Suparator
        </div>
        <div className="hidden md:flex gap-8 text-sm font-medium text-slate-300">
          <Link href="#" className="hover:text-white transition-colors">Proteínas</Link>
          <Link href="#" className="hover:text-white transition-colors">Creatinas</Link>
          <Link href="#" className="hover:text-white transition-colors">Marcas</Link>
        </div>
      </nav>

      {/* Main Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-blue-400 mb-8 backdrop-blur-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          Lanzamiento V2 Próximamente
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-[1.1] mb-6">
          El mayor comparador de <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            suplementos de España
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. Analizamos y comparamos en tiempo real para que tú ahorres.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center max-w-md">
          <button className="px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)] active:scale-95">
            Ver Catálogo
          </button>
          <button className="px-8 py-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold transition-all backdrop-blur-sm active:scale-95">
            Las mejores marcas
          </button>
        </div>
      </main>

      {/* Hero bottom decorative fade */}
      <div className="h-32 bg-gradient-to-t from-slate-950 to-transparent w-full absolute bottom-0 z-0" />
    </div>
  );
}
