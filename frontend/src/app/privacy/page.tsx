import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata = {
  title: 'Política de Privacidad | Suparator',
};

export default function PrivacyPage() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 font-sans text-white">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-6 py-20 w-full z-10 relative">
        <div className="absolute top-[20%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/20 blur-[120px] pointer-events-none z-[-1]" />
        
        <h1 className="text-4xl md:text-5xl font-bold mb-8">Política de Privacidad</h1>
        <div className="prose prose-invert max-w-none text-slate-300 space-y-6 leading-relaxed">
          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Protección de Datos</h2>
          <p>
            Suparator cumple con las directrices del Reglamento General de Protección de Datos (RGPD) y demás normativa vigente en cada momento, y vela por garantizar un correcto uso y tratamiento de los datos personales del usuario.
          </p>
          
          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Cookies</h2>
          <p>
            Este sitio web utiliza cookies propias y de terceros para mejorar la experiencia de usuario y ofrecer contenidos adaptados a sus intereses. Al navegar por nuestro sitio web, aceptas el uso de cookies en las condiciones establecidas en esta Política de Privacidad.
          </p>

          <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Enlaces a Terceros</h2>
          <p>
            Este sitio web pudiera contener enlaces a otros sitios que pudieran ser de su interés. Una vez que usted de clic en estos enlaces y abandone nuestra página, ya no tenemos control sobre al sitio al que es redirigido y por lo tanto no somos responsables de los términos o privacidad ni de la protección de sus datos en esos otros sitios terceros.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
