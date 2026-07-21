import Image from 'next/image';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  image_url: string;
  affiliate_url: string;
  brand: {
    name: string;
  };
  category: {
    name: string;
  };
}

export default function ProductCard({ product }: { product: Product }) {
  // Verificación de si existe la imagen (Next.js Image requiere una URL válida, si está vacía fallará)
  const hasImage = product.image_url && product.image_url.trim() !== "";

  return (
    <div className="group relative flex flex-col bg-[#0a0f1d]/80 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden hover:border-white/20 transition-all duration-500 hover:shadow-2xl hover:shadow-white/5 hover:-translate-y-1">
      
      {/* Zona Superior: Imagen y Badges */}
      <div className="relative aspect-square p-8 flex items-center justify-center bg-gradient-to-br from-white/[0.04] to-transparent overflow-hidden">
        
        {/* Glow effect sutil en blanco/gris (eliminamos el azul neón) */}
        <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 blur-3xl transition-opacity duration-700" />

        {/* Renderizado Condicional de la Imagen o el Placeholder Minimalista */}
        {hasImage ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-48 h-48 sm:w-56 sm:h-56 object-contain drop-shadow-2xl group-hover:scale-105 transition-transform duration-700 ease-out relative z-10"
          />
        ) : (
          <div className="w-48 h-48 sm:w-56 sm:h-56 flex items-center justify-center bg-white/5 rounded-2xl border border-white/10 relative z-10">
             <span className="text-slate-500/50 font-black tracking-[0.3em] text-xs uppercase">Suparator</span>
          </div>
        )}

        {/* Badge de Categoría (Arriba a la izquierda) */}
        <div className="absolute top-4 left-4 z-20">
          <span className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-300 bg-black/40 border border-white/10 rounded-full backdrop-blur-md">
            {product.category?.name || "Sin categoría"}
          </span>
        </div>

        {/* Icono de Favorito (Arriba a la derecha) - Pide autenticación */}
        <div className="absolute top-4 right-4 z-20 group/heart cursor-pointer">
          <div className="p-2 rounded-full bg-black/40 border border-white/10 backdrop-blur-md transition-colors group-hover/heart:bg-white/10 group-hover/heart:border-white/30" title="Guarda tus suplementos favoritos y sigue sus precios">
            <svg 
              className="w-4 h-4 text-slate-400 group-hover/heart:text-white transition-colors" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Zona Inferior: Información del producto */}
      <div className="p-6 sm:p-7 flex flex-col flex-grow bg-gradient-to-t from-[#030712] to-transparent">
        <div className="text-[10px] font-bold tracking-widest text-slate-500 mb-2 uppercase">{product.brand?.name || "Sin marca"}</div>
        <h3 className="text-lg font-bold text-slate-200 mb-3 leading-snug group-hover:text-white transition-colors duration-300">
          {product.name}
        </h3>
        <p className="text-sm text-slate-400/80 line-clamp-2 mb-8 flex-grow font-medium leading-relaxed">
          {product.description}
        </p>
        
        {/* Footer de la tarjeta: Precio y Botón CTA */}
        <div className="flex items-center justify-between mt-auto gap-4">
          <div className="flex flex-col">
            <span className="text-xs text-slate-500 font-medium mb-0.5">Mejor precio</span>
            <span className="text-2xl font-black text-white tracking-tight">
              {product.price?.toFixed(2)}€
            </span>
          </div>
          <a
            href={product.affiliate_url || "#"}
            className="px-6 py-2.5 bg-white hover:bg-slate-200 text-black rounded-xl text-sm font-bold transition-all duration-300 active:scale-95 shadow-lg shadow-white/10 hover:shadow-white/20 whitespace-nowrap"
          >
            Ver oferta
          </a>
        </div>
      </div>
    </div>
  );
}
