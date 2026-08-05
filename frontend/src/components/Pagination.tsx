import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  // Lógica para mostrar máximo 5 números de página con elipsis si es necesario
  const getVisiblePages = () => {
    const delta = 2;
    const range = [];
    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }
    
    if (currentPage - delta > 2) {
      range.unshift("...");
    }
    if (currentPage + delta < totalPages - 1) {
      range.push("...");
    }

    range.unshift(1);
    if (totalPages > 1) {
      range.push(totalPages);
    }

    return range;
  };

  const visiblePages = getVisiblePages();

  return (
    <div className="flex items-center justify-center gap-2 mt-10 mb-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 hover:text-slate-900 transition-colors font-medium shadow-sm"
      >
        Anterior
      </button>
      
      <div className="flex items-center gap-1 hidden sm:flex">
        {visiblePages.map((page, index) => {
          if (page === "...") {
            return (
              <span key={`ellipsis-${index}`} className="w-8 text-center text-slate-400 font-medium">
                ...
              </span>
            );
          }
          return (
            <button
              key={`page-${page}`}
              onClick={() => onPageChange(page as number)}
              className={`w-10 h-10 rounded-xl font-bold flex items-center justify-center transition-all ${
                currentPage === page 
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20' 
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 shadow-sm'
              }`}
            >
              {page}
            </button>
          );
        })}
      </div>

      <div className="sm:hidden flex items-center px-4 font-medium text-slate-600">
        Página {currentPage} de {totalPages}
      </div>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 hover:text-slate-900 transition-colors font-medium shadow-sm"
      >
        Siguiente
      </button>
    </div>
  );
}
