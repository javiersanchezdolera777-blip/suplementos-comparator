import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function ContactPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white selection:bg-white/20">
      <Navbar />
      <main className="flex-1 w-full max-w-2xl mx-auto px-6 py-16 md:py-24 relative z-10 flex flex-col items-center text-center">
        <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
        </div>
        <h1 className="text-3xl md:text-5xl font-black tracking-tighter mb-4 text-white">
          Contacto
        </h1>
        <p className="text-base text-slate-400 mb-10 leading-relaxed">
          ¿Tienes alguna sugerencia, has encontrado un error o eres una marca que quiere aparecer en Suparator? Escríbenos y te responderemos lo antes posible.
        </p>

        <a href="mailto:contacto@suparator.com" className="px-8 py-4 bg-white text-black rounded-xl font-bold text-lg hover:bg-slate-200 transition-all shadow-lg shadow-white/10 hover:shadow-white/20 active:scale-95">
          contacto@suparator.com
        </a>

        <p className="text-xs text-slate-500 mt-12">
          Actualmente, debido al volumen de trabajo en el desarrollo, podemos tardar hasta 48h en contestar.
        </p>
      </main>
      <Footer />
    </div>
  );
}
