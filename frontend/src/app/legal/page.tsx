import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata = {
  title: 'Aviso Legal | Suparator',
};

export default function LegalPage() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 font-sans text-white">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-6 py-20 w-full z-10 relative">
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px] pointer-events-none z-[-1]" />
        
        <h1 className="text-4xl md:text-5xl font-bold mb-8">Aviso Legal</h1>
        <div className="prose prose-invert max-w-none text-slate-300 space-y-6 leading-relaxed">
          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">1. Datos Identificativos</h2>
          <p>
            En cumplimiento con el deber de información recogido en artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y del Comercio Electrónico, a continuación se reflejan los siguientes datos: la empresa titular de dominio web es Suparator (en adelante, Suparator), con correo electrónico de contacto: contacto@suparator.es.
          </p>
          
          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">2. Usuarios</h2>
          <p>
            El acceso y/o uso de este portal de Suparator atribuye la condición de USUARIO, que acepta, desde dicho acceso y/o uso, las Condiciones Generales de Uso aquí reflejadas.
          </p>

          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">3. Afiliación</h2>
          <p>
            Suparator participa en diversos programas de afiliación de marketing, lo que significa que Suparator recibe comisiones de las compras hechas a través de los links a sitios de los vendedores. Estas compras no suponen ningún coste adicional para el usuario.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
