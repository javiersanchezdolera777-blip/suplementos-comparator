"use client";

import React from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const searchParams = useSearchParams();

  const getPageUrl = (page: number) => {
    const params = new URLSearchParams(searchParams?.toString() || "");
    params.set("page", page.toString());
    return `?${params.toString()}#catalogo`;
  };
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
      <Link
        href={currentPage > 1 ? getPageUrl(currentPage - 1) : '#'}
        onClick={(e) => {
          if (currentPage === 1) {
            e.preventDefault();
            return;
          }
          // We don't preventDefault to allow URL update, but we still trigger local state update
          onPageChange(currentPage - 1);
        }}
        className={`px-4 py-2 rounded-xl border border-slate-200 transition-colors font-medium shadow-sm flex items-center justify-center ${
          currentPage === 1
            ? 'bg-slate-50 text-slate-400 opacity-50 cursor-not-allowed pointer-events-none'
            : 'bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900'
        }`}
      >
        Anterior
      </Link>
      
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
            <Link
              key={`page-${page}`}
              href={getPageUrl(page as number)}
              onClick={() => onPageChange(page as number)}
              className={`w-10 h-10 rounded-xl font-bold flex items-center justify-center transition-all ${
                currentPage === page 
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20 pointer-events-none' 
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 shadow-sm'
              }`}
            >
              {page}
            </Link>
          );
        })}
      </div>

      <div className="sm:hidden flex items-center px-4 font-medium text-slate-600">
        Página {currentPage} de {totalPages}
      </div>

      <Link
        href={currentPage < totalPages ? getPageUrl(currentPage + 1) : '#'}
        onClick={(e) => {
          if (currentPage === totalPages) {
            e.preventDefault();
            return;
          }
          onPageChange(currentPage + 1);
        }}
        className={`px-4 py-2 rounded-xl border border-slate-200 transition-colors font-medium shadow-sm flex items-center justify-center ${
          currentPage === totalPages
            ? 'bg-slate-50 text-slate-400 opacity-50 cursor-not-allowed pointer-events-none'
            : 'bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900'
        }`}
      >
        Siguiente
      </Link>
    </div>
  );
}
