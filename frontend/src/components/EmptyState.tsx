interface EmptyStateProps {
  resetFilters: () => void;
  title?: string;
  description?: string;
}

export default function EmptyState({
  resetFilters,
  title = "No hemos encontrado suplementos con estos filtros",
  description = "Prueba a eliminar algunos filtros, seleccionar otra categoría o realizar una búsqueda menos específica.",
}: EmptyStateProps) {
  return (
    <div className="w-full flex flex-col items-center justify-center py-16 px-6 bg-white border border-slate-200/80 rounded-3xl text-center shadow-sm animate-in fade-in zoom-in-95 duration-300">
      {/* Icono Ilustrativo Estilizado */}
      <div className="relative mb-6">
        <div className="w-20 h-20 bg-blue-50 border border-blue-100 rounded-3xl flex items-center justify-center text-blue-600 shadow-inner">
          <svg
            className="w-10 h-10 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.8"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-amber-400 text-white font-extrabold text-xs rounded-full flex items-center justify-center border-2 border-white shadow-sm">
          !
        </div>
      </div>

      {/* Título y Descripción */}
      <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 mb-2 leading-snug max-w-md">
        {title}
      </h3>
      <p className="text-sm text-slate-500 max-w-lg mb-8 leading-relaxed font-medium">
        {description}
      </p>

      {/* Botón de Acción Principal: Restablecer Filtros */}
      <button
        onClick={resetFilters}
        className="inline-flex items-center gap-2.5 px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm rounded-xl shadow-md hover:shadow-lg transition-all duration-200 active:scale-95 cursor-pointer"
      >
        <svg
          className="w-4 h-4 text-slate-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        <span>Restablecer filtros</span>
      </button>
    </div>
  );
}
