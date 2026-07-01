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
    <div className="group relative flex flex-col bg-slate-900/50 backdrop-blur-sm border border-white/5 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(37,99,235,0.15)]">
      <div className="relative aspect-square p-6 flex items-center justify-center bg-gradient-to-br from-slate-800/50 to-slate-900/50 overflow-hidden">
        {/* Glow effect on hover */}
        <div className="absolute inset-0 bg-blue-500/20 opacity-0 group-hover:opacity-100 blur-3xl transition-opacity duration-500" />
        
        <Image
          src={product.image_url}
          alt={product.name}
          width={250}
          height={250}
          className="object-contain drop-shadow-2xl group-hover:scale-110 transition-transform duration-500 relative z-10"
        />
        <div className="absolute top-4 left-4 z-20">
          <span className="px-3 py-1 text-xs font-bold uppercase tracking-wider text-blue-300 bg-blue-500/10 border border-blue-500/20 rounded-full backdrop-blur-md">
            {product.category.name}
          </span>
        </div>
      </div>
      
      <div className="p-6 flex flex-col flex-grow">
        <div className="text-xs font-semibold tracking-wider text-slate-400 mb-2 uppercase">{product.brand.name}</div>
        <h3 className="text-xl font-bold text-white mb-3 leading-tight group-hover:text-blue-400 transition-colors">
          {product.name}
        </h3>
        <p className="text-sm text-slate-400 line-clamp-2 mb-6 flex-grow">
          {product.description}
        </p>
        <div className="flex items-center justify-between mt-auto">
          <span className="text-2xl font-black text-white">
            {product.price.toFixed(2)}€
          </span>
          <a
            href={product.affiliate_url}
            className="px-5 py-2.5 bg-white/5 hover:bg-blue-600 border border-white/10 hover:border-blue-500 rounded-xl text-sm font-semibold text-white transition-all active:scale-95 shadow-sm hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]"
          >
            Comprar
          </a>
        </div>
      </div>
    </div>
  );
}
