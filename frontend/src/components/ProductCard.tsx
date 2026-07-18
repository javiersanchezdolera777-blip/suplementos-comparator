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
  return (
    <div className="group relative flex flex-col bg-[#0f172a]/40 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden hover:border-blue-500/30 transition-all duration-500 hover:shadow-2xl hover:shadow-blue-900/20 hover:-translate-y-1">
      <div className="relative aspect-square p-8 flex items-center justify-center bg-gradient-to-br from-white/[0.02] to-transparent overflow-hidden">
        {/* Glow effect on hover */}
        <div className="absolute inset-0 bg-blue-500/10 opacity-0 group-hover:opacity-100 blur-3xl transition-opacity duration-700" />

        <Image
          src={product.image_url || "/placeholder-image.png"}
          alt={product.name}
          width={220}
          height={220}
          className="object-contain drop-shadow-2xl group-hover:scale-105 transition-transform duration-700 ease-out relative z-10"
        />
        <div className="absolute top-4 left-4 z-20">
          <span className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-blue-300 bg-blue-500/10 border border-blue-500/20 rounded-full backdrop-blur-md">
            {product.category?.name || "Sin categoría"}
          </span>
        </div>
      </div>

      <div className="p-6 sm:p-7 flex flex-col flex-grow bg-gradient-to-t from-[#030712] to-transparent">
        <div className="text-[10px] font-bold tracking-widest text-slate-500 mb-2 uppercase">{product.brand?.name || "Sin marca"}</div>
        <h3 className="text-xl font-bold text-slate-100 mb-3 leading-snug group-hover:text-blue-400 transition-colors duration-300">
          {product.name}
        </h3>
        <p className="text-sm text-slate-400/80 line-clamp-2 mb-8 flex-grow font-medium leading-relaxed">
          {product.description}
        </p>
        <div className="flex items-center justify-between mt-auto">
          <div className="flex flex-col">
            <span className="text-xs text-slate-500 font-medium mb-0.5">Mejor precio</span>
            <span className="text-2xl font-black text-white tracking-tight">
              {product.price?.toFixed(2)}€
            </span>
          </div>
          <a
            href={product.affiliate_url || "#"}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-bold text-white transition-all duration-300 active:scale-95 shadow-lg shadow-blue-900/30 hover:shadow-blue-600/40"
          >
            Ver oferta
          </a>
        </div>
      </div>
    </div>
  );
}
