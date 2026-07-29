import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function AboutPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white selection:bg-white/20">
      <Navbar />
      <main className="flex-1 w-full max-w-4xl mx-auto px-6 py-16 md:py-24 relative z-10">
        {/* Glow de fondo corporativo */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[80%] h-[300px] bg-slate-500/5 blur-[150px] pointer-events-none -z-10" />
        
        <h1 className="text-4xl md:text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
          Quiénes Somos
        </h1>
        <p className="text-xl text-slate-400 font-medium mb-12">La misión detrás de Suparator.</p>
        
        <div className="space-y-8 text-slate-300 leading-relaxed font-medium">
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">Nuestro Objetivo</h2>
            <p>
              Suparator nació con una misión muy clara: aportar <strong>transparencia y ahorro</strong> al mundo de la suplementación deportiva en España.
              Como deportistas, sabemos lo frustrante que puede ser saltar de una tienda a otra buscando el mejor precio para tu proteína o creatina, calculando gastos de envío y descifrando ofertas engañosas.
            </p>
          </section>
          
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">¿Cómo lo hacemos?</h2>
            <p>
              Hemos desarrollado un motor de búsqueda propio que se conecta a los catálogos de las principales marcas del país: <em>Myprotein, HSN, Bulk, Prozis y Sport Live</em>. 
              Nuestro algoritmo analiza, compara y organiza miles de productos para que tú solo veas lo que importa: <strong>el precio más competitivo en tiempo real</strong>.
            </p>
          </section>

          <section className="p-8 rounded-3xl bg-white/5 border border-white/10 mt-12">
            <h2 className="text-2xl font-bold text-white mb-4">Nuestro Modelo (Transparencia Total)</h2>
            <p className="text-slate-400">
              Queremos ser 100% transparentes contigo. Suparator es y siempre será una herramienta gratuita. Para mantener los servidores y seguir mejorando la plataforma, participamos en programas de afiliación.
              Esto significa que, si encuentras un suplemento que te gusta a través de nuestra web y lo compras, es posible que la marca nos dé una pequeña comisión.
              <br/><br/>
              <strong className="text-white">El precio para ti siempre será el mismo (o incluso mejor gracias a nuestros códigos de descuento), pero estarás ayudando a mantener vivo este proyecto.</strong>
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
