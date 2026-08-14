"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

interface ProductoLive {
  id: number;
  nombre: string;
  marca: string;
  categoria?: string;
  imagen_url?: string;
  precio_minimo?: number;
  formato?: string;
}

export default function SearchOmnibox() {
  const [query, setQuery] = useState("");
  const [resultados, setResultados] = useState<ProductoLive[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Debounced Fetch en tiempo real
  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResultados([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setIsOpen(true);

    const timer = setTimeout(async () => {
      try {
        const url = `${API_BASE}/api/productos/live-search?q=${encodeURIComponent(trimmed)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Error en respuesta live-search");
        const data = await res.json();
        const lista = Array.isArray(data) ? data : (data.productos || []);
        setResultados(lista);
      } catch (err) {
        console.error("Error al buscar productos en vivo:", err);
        setResultados([]);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, API_BASE]);

  // Cerrar al hacer click fuera o presionar Escape
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setIsOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsOpen(false);
    router.push(`/?q=${encodeURIComponent(query.trim())}`);
  };

  const handleSelectProduct = (prod: ProductoLive) => {
    setIsOpen(false);
    setQuery("");
    router.push(`/?q=${encodeURIComponent(prod.nombre)}`);
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-lg mx-auto">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-3.5 text-slate-400 pointer-events-none">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => { if (query.trim().length >= 2) setIsOpen(true); }}
          placeholder="Buscar proteína, creatina, marca..."
          className="w-full pl-10 pr-9 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-sm"
        />

        {query && (
          <button
            type="button"
            onClick={() => { setQuery(""); setResultados([]); setIsOpen(false); }}
            className="absolute right-3 text-slate-400 hover:text-slate-600 p-0.5"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </form>

      {/* Popover de Resultados en Vivo */}
      {isOpen && query.trim().length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-1 duration-150">
          {isLoading ? (
            <div className="p-4 text-center text-sm text-slate-500 flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
              <span>Buscando suplementos...</span>
            </div>
          ) : resultados.length > 0 ? (
            <div>
              <div className="p-2 divide-y divide-slate-100">
                {resultados.map((prod) => (
                  <div
                    key={prod.id}
                    onClick={() => handleSelectProduct(prod)}
                    className="flex items-center gap-3 p-2.5 hover:bg-slate-50 rounded-xl cursor-pointer transition-colors"
                  >
                    <div className="w-10 h-10 flex-shrink-0 bg-slate-100 rounded-lg flex items-center justify-center p-1 border border-slate-100 overflow-hidden relative">
                      <img
                        src={prod.imagen_url || "/Logo_icon2.png"}
                        alt={prod.nombre}
                        className="w-full h-full object-contain"
                        onError={(e) => { (e.target as HTMLImageElement).src = "/Logo_icon2.png"; }}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          {prod.marca}
                        </span>
                        {prod.categoria && (
                          <span className="text-[9px] font-medium bg-blue-50 text-blue-600 px-1.5 py-0.2 rounded">
                            {prod.categoria}
                          </span>
                        )}
                      </div>
                      <p className="text-xs font-semibold text-slate-800 truncate">
                        {prod.nombre}
                      </p>
                    </div>
                    {prod.precio_minimo && (
                      <div className="text-right flex-shrink-0">
                        <span className="text-xs font-black text-emerald-600">
                          {prod.precio_minimo.toFixed(2)} €
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              <div
                onClick={handleSubmit}
                className="bg-slate-50 hover:bg-slate-100 p-2.5 text-center text-xs font-semibold text-blue-600 cursor-pointer border-t border-slate-100 transition-colors"
              >
                Ver todos los resultados para "{query}" →
              </div>
            </div>
          ) : (
            <div className="p-6 text-center">
              <p className="text-xs font-semibold text-slate-700 mb-1">
                No se encontraron productos para "{query}"
              </p>
              <p className="text-[11px] text-slate-400">
                Prueba con otro término como Whey, Creatina o HSN.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
