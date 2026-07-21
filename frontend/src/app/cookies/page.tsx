import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function CookiesPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white selection:bg-white/20">
      <Navbar />
      <main className="flex-1 w-full max-w-4xl mx-auto px-6 py-16 md:py-24 relative z-10">
        <h1 className="text-3xl md:text-4xl font-black tracking-tighter mb-12 text-white">
          Política de Cookies
        </h1>
        
        <div className="space-y-8 text-slate-400 text-sm leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">1. ¿Qué son las cookies?</h2>
            <p>
              Una cookie es un pequeño archivo de texto que un sitio web guarda en tu ordenador o dispositivo móvil cuando lo visitas. Facilita que la web recuerde tus acciones y preferencias (como el inicio de sesión o idioma) durante un tiempo.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">2. Tipos de Cookies que utilizamos</h2>
            <p>
              <strong>Cookies Técnicas:</strong> Son estrictamente necesarias para el funcionamiento de la web (por ejemplo, recordar tus ajustes de filtrado en el catálogo).<br/><br/>
              <strong>Cookies de Afiliación (Terceros):</strong> Como parte de nuestro modelo de negocio CPA, al hacer clic en "Ver oferta", redes como Awin pueden instalar una cookie para saber que has llegado desde Suparator y asignarnos la comisión correspondiente.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">3. Cómo gestionar o deshabilitar las cookies</h2>
            <p>
              Puedes configurar tu navegador para rechazar todas las cookies o para que te avise cuando se envíe una. Sin embargo, ten en cuenta que algunas características de la plataforma pueden no funcionar correctamente sin las cookies técnicas.
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
