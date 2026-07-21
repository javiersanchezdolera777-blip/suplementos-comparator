import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-[#0a0f1d] pt-16 pb-8 mt-auto relative z-10">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          
          {/* Col 1: Marca y Transparencia */}
          <div className="md:col-span-2 flex flex-col items-start gap-4">
            <div className="text-2xl font-black tracking-tighter flex items-center gap-2 mb-2">
              <span className="text-slate-200">⚡</span> 
              <span className="text-white">Suparator</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-md">
              Suparator es el comparador líder de suplementación deportiva. Analizamos los catálogos de las principales marcas para asegurarnos de que siempre pagues el precio más justo.
            </p>
            <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <p className="text-xs text-slate-400 leading-relaxed">
                <strong className="text-slate-200">Transparencia de Afiliados:</strong> Suparator participa en programas de afiliación (CPA). Si compras a través de nuestros enlaces, podemos recibir una comisión sin coste extra para ti. Esto mantiene la plataforma 100% gratuita y sin anuncios.
              </p>
            </div>
          </div>

          {/* Col 2: Corporativo */}
          <div className="flex flex-col gap-4">
            <h4 className="text-white font-bold tracking-wide uppercase text-sm mb-2">Proyecto</h4>
            <Link href="/about" className="text-sm text-slate-400 hover:text-white transition-colors">Quiénes Somos</Link>
            <Link href="/roadmap" className="text-sm text-slate-400 hover:text-white transition-colors">Hoja de Ruta (V2)</Link>
            <Link href="/contact" className="text-sm text-slate-400 hover:text-white transition-colors">Contacto</Link>
          </div>

          {/* Col 3: Legal */}
          <div className="flex flex-col gap-4">
            <h4 className="text-white font-bold tracking-wide uppercase text-sm mb-2">Legal</h4>
            <Link href="/legal" className="text-sm text-slate-400 hover:text-white transition-colors">Aviso Legal</Link>
            <Link href="/privacy" className="text-sm text-slate-400 hover:text-white transition-colors">Política de Privacidad</Link>
            <Link href="/cookies" className="text-sm text-slate-400 hover:text-white transition-colors">Política de Cookies</Link>
          </div>

        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-slate-500 font-medium">
            © {new Date().getFullYear()} Suparator. Creado con precisión por Javier y Diego.
          </p>
          <div className="flex items-center gap-1 text-xs text-slate-500 font-semibold">
            <span>Versión 2.0.1 (BETA)</span>
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block ml-2 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
          </div>
        </div>
      </div>
    </footer>
  );
}
