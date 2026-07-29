import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function LegalPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white selection:bg-white/20">
      <Navbar />
      <main className="flex-1 w-full max-w-4xl mx-auto px-6 py-16 md:py-24 relative z-10">
        <h1 className="text-3xl md:text-4xl font-black tracking-tighter mb-12 text-white">
          Aviso Legal
        </h1>
        
        <div className="space-y-8 text-slate-400 text-sm leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">1. Datos Identificativos</h2>
            <p>
              En cumplimiento con el deber de información recogido en artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y del Comercio Electrónico, a continuación se reflejan los siguientes datos: la plataforma web Suparator (en adelante, "la Plataforma") es operada de forma independiente y es de acceso libre.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">2. Exención de Responsabilidad Médica</h2>
            <p>
              La información contenida en Suparator, incluyendo textos, gráficos, imágenes y otros materiales, tiene fines puramente informativos y comparativos. Ningún contenido de esta web pretende ser un sustituto de asesoramiento médico profesional, diagnóstico o tratamiento.
              Consulta siempre con tu médico o nutricionista antes de comenzar cualquier régimen de suplementación.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">3. Precios y Disponibilidad</h2>
            <p>
              Aunque nuestro motor de búsqueda se actualiza de forma constante, no podemos garantizar que los precios y la disponibilidad mostrados sean 100% exactos en tiempo real, ya que dependen directamente de las plataformas de los terceros (vendedores).
              El precio final y válido será siempre el que se muestre en la página oficial del vendedor (HSN, Myprotein, etc.) en el momento del pago.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">4. Enlaces a Terceros y Afiliación</h2>
            <p>
              Suparator contiene enlaces que dirigen a sitios web de terceros. Operamos bajo el modelo de Afiliación (CPA). Esto exime a Suparator de cualquier responsabilidad sobre las transacciones, envíos, devoluciones o reclamaciones que deban gestionarse directamente con el vendedor final.
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
