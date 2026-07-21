import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import Catalog from "@/components/Catalog";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white overflow-hidden relative selection:bg-white/20">
      {/* Background Gradients (Monochromatic Premium) */}
      <div className="absolute top-0 inset-x-0 h-[400px] bg-gradient-to-b from-white/[0.03] to-transparent pointer-events-none z-0" />
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-white/5 blur-[120px] pointer-events-none z-0" />
      <div className="absolute top-[20%] right-[-10%] w-[30%] h-[50%] rounded-full bg-slate-400/5 blur-[150px] pointer-events-none z-0" />

      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[url('https://res.cloudinary.com/dzl9yxixg/image/upload/v1714421252/grid-pattern_qgntoz.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-20 pointer-events-none z-0" />

      {/* Navigation */}
      <Navbar />

      {/* Main Hero Section */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-6 pb-12">
        <section className="w-full flex flex-col items-center justify-center text-center mt-6 md:mt-10 mb-8 md:mb-12 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-300 mb-6 backdrop-blur-md shadow-lg shadow-emerald-900/20 transition-transform hover:scale-105 cursor-default">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Comparando precios en tiempo real</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tighter max-w-4xl leading-[1.1] mb-5 drop-shadow-2xl">
            El mayor comparador de <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-200 via-white to-slate-400 drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]">
              suplementos de España
            </span>
          </h1>

          <p className="text-base md:text-lg text-slate-400/90 max-w-2xl mb-12 leading-relaxed font-medium">
            Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. <span className="text-slate-200">Analizamos y comparamos en tiempo real</span> para que tú ahorres.
          </p>

          {/* Partner Grid - Aporta un bloque más claro/gris para romper la oscuridad */}
          <div className="w-full max-w-5xl mx-auto mb-16 pt-8 border-t border-white/10">
            <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-8">Comparamos en tiempo real el catálogo de</p>
            <div className="flex flex-wrap justify-center items-center gap-10 md:gap-16 opacity-60 grayscale hover:grayscale-0 transition-all duration-700">
              {/* Simulando logos vectoriales con tipografías para mantener el nivel Premium */}
              <span className="text-2xl font-black tracking-tighter text-white">MYPROTEIN</span>
              <span className="text-3xl font-black text-white italic">HSN</span>
              <span className="text-2xl font-bold text-white tracking-widest">BULK</span>
              <span className="text-2xl font-extrabold text-white uppercase">Prozis</span>
              <span className="text-xl font-bold text-white">SPORT LIVE</span>
            </div>
          </div>

          <div className="w-full max-w-7xl mt-2 md:mt-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300 fill-mode-both ease-out relative">
            {/* Catalog decorative glow */}
            <div className="absolute -inset-1 bg-gradient-to-r from-white/5 via-slate-400/5 to-white/5 rounded-[2rem] blur-xl opacity-50 z-0"></div>
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
