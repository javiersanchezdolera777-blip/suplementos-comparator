import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import Catalog from "@/components/Catalog";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#f8fafc] font-sans text-slate-900 relative selection:bg-blue-100 selection:text-blue-900">

      {/* Navigation */}
      <Navbar />

      {/* Main Hero Section */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-2 pb-6">
        <section className="w-full flex flex-col items-center justify-center text-center mt-4 md:mt-6 mb-6 md:mb-8 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">

          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-700 mb-6 backdrop-blur-md shadow-sm transition-transform hover:scale-105 cursor-default">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Comparando precios en tiempo real</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tighter max-w-4xl leading-[1.1] mb-4 text-slate-900 drop-shadow-sm">
            El mayor comparador de <br className="hidden md:block" />
            <span className="text-blue-600">
              suplementos de España
            </span>
          </h1>

          <p className="text-sm md:text-base text-slate-600 max-w-2xl mb-8 leading-relaxed font-medium">
            Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. <span className="text-slate-900 font-bold">Analizamos y comparamos en tiempo real</span> para que tú ahorres.
          </p>

          {/* Partner Grid */}
          <div className="w-full max-w-5xl mx-auto mb-8 pt-6 border-t border-slate-200">
            <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase mb-6">Comparamos en tiempo real el catálogo de</p>
            <div className="flex flex-wrap justify-center items-center gap-10 md:gap-16 opacity-60 grayscale hover:grayscale-0 transition-all duration-700">
              <span className="text-2xl font-black tracking-tighter text-slate-800">MYPROTEIN</span>
              <span className="text-3xl font-black text-slate-800 italic">HSN</span>
              <span className="text-2xl font-bold text-slate-800 tracking-widest">BULK</span>
              <span className="text-2xl font-extrabold text-slate-800 uppercase">Prozis</span>
              <span className="text-xl font-bold text-slate-800">SPORT LIVE</span>
            </div>
          </div>

          <div className="w-full max-w-7xl mt-2 md:mt-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300 fill-mode-both ease-out relative">
            <div className="relative z-10 w-full">
              <Catalog />
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
