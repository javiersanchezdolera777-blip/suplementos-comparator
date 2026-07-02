import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import Catalog from "@/components/Catalog";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white overflow-hidden relative selection:bg-blue-500/30">
      {/* Background Gradients */}
      <div className="absolute top-0 inset-x-0 h-[500px] bg-gradient-to-b from-blue-900/20 to-transparent pointer-events-none z-0" />
      <div className="absolute top-[-15%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-600/20 blur-[150px] pointer-events-none z-0" />
      <div className="absolute top-[30%] right-[-15%] w-[40%] h-[60%] rounded-full bg-purple-600/15 blur-[150px] pointer-events-none z-0" />

      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[url('https://res.cloudinary.com/dzl9yxixg/image/upload/v1714421252/grid-pattern_qgntoz.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-20 pointer-events-none z-0" />

      {/* Navigation */}
      <Navbar />

      {/* Main Hero Section */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-12 pb-24">
        <section className="w-full flex flex-col items-center justify-center text-center mt-10 md:mt-20 mb-16 md:mb-24 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-semibold text-blue-300 mb-8 backdrop-blur-md shadow-lg shadow-blue-900/20 transition-transform hover:scale-105 cursor-default">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span>Lanzamiento V2 Próximamente</span>
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-8xl font-black tracking-tighter max-w-5xl leading-[1.05] mb-8 drop-shadow-2xl">
            El mayor comparador de <br className="hidden lg:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 drop-shadow-[0_0_20px_rgba(99,102,241,0.4)]">
              suplementos de España
            </span>
          </h1>

          <p className="text-lg md:text-2xl text-slate-400/90 max-w-3xl mb-12 leading-relaxed font-medium">
            Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. <span className="text-slate-200">Analizamos y comparamos en tiempo real</span> para que tú ahorres.
          </p>

          <div className="w-full max-w-6xl mt-4 md:mt-8 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300 fill-mode-both ease-out relative">
            {/* Catalog decorative glow */}
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-blue-500/30 rounded-[2rem] blur-xl opacity-50 z-0"></div>
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
