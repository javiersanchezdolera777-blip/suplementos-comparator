import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import mockProducts from "@/data/mock_products.json";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 font-sans text-white overflow-hidden relative">
      {/* Background gradients and glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/30 blur-[120px] pointer-events-none z-0" />
      <div className="absolute top-[40%] right-[-10%] w-[30%] h-[50%] rounded-full bg-purple-600/20 blur-[120px] pointer-events-none z-0" />

      {/* Navigation */}
      <Navbar />

      {/* Main Hero Section */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6">
        <section className="w-full min-h-[70vh] flex flex-col items-center justify-center text-center py-20">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-blue-400 mb-8 backdrop-blur-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Lanzamiento V2 Próximamente
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-[1.1] mb-6 drop-shadow-lg">
            El mayor comparador de <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500">
              suplementos de España
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
            Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. Analizamos y comparamos en tiempo real para que tú ahorres.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full justify-center max-w-md">
            <a href="#catalogo" className="px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)] active:scale-95 text-center">
              Ver Catálogo
            </a>
            <button className="px-8 py-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold transition-all backdrop-blur-sm active:scale-95">
              Las mejores marcas
            </button>
          </div>
        </section>

        {/* Product Grid Section */}
        <section id="catalogo" className="w-full py-16 scroll-mt-20">
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-4">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Catálogo Destacado</h2>
              <p className="text-slate-400 max-w-2xl text-lg">
                Explora nuestra selección de los suplementos más populares y al mejor precio garantizado.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {mockProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
