import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata = {
  title: 'Quiénes Somos | Suparator',
};

export default function AboutPage() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 font-sans text-white">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-6 py-20 w-full z-10 relative">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/20 blur-[120px] pointer-events-none z-[-1]" />
        
        <h1 className="text-4xl md:text-5xl font-bold mb-8">Quiénes Somos</h1>
        <div className="prose prose-invert max-w-none text-slate-300 space-y-6 leading-relaxed">
          <p className="text-lg">
            En <strong>Suparator</strong>, nuestra misión es simplificar la búsqueda y compra de suplementos deportivos en España. Nacimos con la visión de crear la herramienta definitiva para atletas y entusiastas del fitness que buscan la mejor calidad al mejor precio.
          </p>
          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Nuestra Misión</h2>
          <p>
            Creemos que la suplementación debe ser accesible y transparente. Por ello, desarrollamos tecnología que rastrea, analiza y compara los precios de las principales marcas del mercado en tiempo real.
          </p>
          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">¿Por qué elegirnos?</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Transparencia total:</strong> Te mostramos los precios reales sin costes ocultos.</li>
            <li><strong>Ahorro de tiempo:</strong> Todo el catálogo de tus marcas favoritas en un solo lugar.</li>
            <li><strong>Decisiones informadas:</strong> Descripciones detalladas y categorías organizadas para ayudarte a elegir.</li>
          </ul>
        </div>
      </main>
      <Footer />
    </div>
  );
}
