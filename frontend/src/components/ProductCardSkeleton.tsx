export default function ProductCardSkeleton() {
  return (
    <div className="flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm animate-pulse">
      {/* Zona Superior: Imagen y Badges en Skeleton */}
      <div className="relative aspect-square p-6 sm:p-8 flex items-center justify-center bg-slate-50">
        <div className="w-3/4 h-3/4 bg-slate-200 rounded-2xl"></div>

        {/* Skeleton Badge Categoría (Bottom Left) */}
        <div className="absolute bottom-3 left-3">
          <div className="w-20 h-5 bg-slate-200 rounded-md"></div>
        </div>

        {/* Skeleton Icono Favoritos (Top Right) */}
        <div className="absolute top-3 right-3">
          <div className="w-8 h-8 bg-slate-200 rounded-full"></div>
        </div>
      </div>

      {/* Zona Inferior: Marca, Título, Precio y Botón */}
      <div className="p-5 flex flex-col flex-grow bg-white border-t border-slate-100">
        {/* Marca */}
        <div className="w-1/3 h-3 bg-slate-200 rounded mb-2"></div>

        {/* Título (2 Líneas) */}
        <div className="w-full h-4 bg-slate-200 rounded mb-1.5"></div>
        <div className="w-4/5 h-4 bg-slate-200 rounded mb-6"></div>

        {/* Zona de Precio y Botón Anclados */}
        <div className="flex items-center justify-between mt-auto pt-4 gap-2">
          <div className="flex items-center gap-2">
            <div className="w-20 h-7 bg-slate-200 rounded-md"></div>
            <div className="w-14 h-5 bg-slate-200 rounded-md"></div>
          </div>
          <div className="w-24 h-9 bg-slate-200 rounded-xl"></div>
        </div>
      </div>
    </div>
  );
}
