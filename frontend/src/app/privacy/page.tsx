import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function PrivacyPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] font-sans text-white selection:bg-white/20">
      <Navbar />
      <main className="flex-1 w-full max-w-4xl mx-auto px-6 py-16 md:py-24 relative z-10">
        <h1 className="text-3xl md:text-4xl font-black tracking-tighter mb-12 text-white">
          Política de Privacidad
        </h1>
        
        <div className="space-y-8 text-slate-400 text-sm leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">1. Recopilación de Datos</h2>
            <p>
              En Suparator respetamos tu privacidad. Como usuarios de nuestra herramienta de comparación, actualmente no recopilamos datos personales de navegación de manera intrusiva ni requerimos registro obligatorio para visualizar los precios de los suplementos.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">2. Uso de Cookies</h2>
            <p>
              Utilizamos cookies técnicas estrictamente necesarias para el funcionamiento del sitio web. Adicionalmente, al utilizar los enlaces de afiliado para ir a comprar un producto, las redes de afiliación (como Awin o Tradedoubler) pueden insertar cookies en tu navegador para rastrear el origen de la venta y asignar la comisión correspondiente a Suparator de forma completamente anónima.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-200 mb-3">3. Cuentas de Usuario (Próximamente)</h2>
            <p>
              Si en un futuro decides crear una cuenta mediante "Google Login" u otro proveedor para guardar tus productos favoritos, tu correo electrónico y nombre público serán almacenados de forma segura con el único fin de ofrecerte la funcionalidad solicitada en tu perfil. No venderemos ni cederemos esta información a terceros.
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
