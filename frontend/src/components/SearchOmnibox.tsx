"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface ProductSuggestion {
  id: number;
  name: string;
  slug?: string;
  image_url: string;
  price: number;
  precio_actual?: number | null;
  brand?: {
    name: string;
  };
  tienda?: string | { name: string } | null;
}

const decodeHTML = (str: string) => {
  if (!str) return "";
  return str
    .replace(/&#8211;/g, "–")
    .replace(/&#8212;/g, "—")
    .replace(/&amp;/g, "&")
    .replace(/&#8217;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
};

const formatTitle = (nombre: string, marca?: string) => {
  if (!marca || !nombre) return nombre;
  const escapedMarca = marca.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`^${escapedMarca}\\s+`, "i");
  return nombre.replace(regex, "");
};

export default function SearchOmnibox() {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState<ProductSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [failedImages, setFailedImages] = useState<Record<number, boolean>>({});

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Debounce de 250ms
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query.trim());
    }, 250);

    return () => clearTimeout(handler);
  }, [query]);

  // Consulta API al cambiar debouncedQuery
  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults([]);
      setIsOpen(false);
      setLoading(false);
      return;
    }

    setLoading(true);
    setIsOpen(true);

    const controller = new AbortController();

    fetch(`${apiUrl}/api/productos?busqueda=${encodeURIComponent(debouncedQuery)}&limit=4`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error("Error al consultar API");
        return res.json();
      })
      .then((data) => {
        const productosList = Array.isArray(data) ? data : data.productos || [];
        setResults(productosList.slice(0, 4));
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          console.error("Error en SearchOmnibox:", err);
          setResults([]);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [debouncedQuery, apiUrl]);

  // Manejador de click fuera del componente
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Manejador de teclado local (Escape / Enter)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      setIsOpen(false);
    } else if (e.key === "Enter" && query.trim()) {
      e.preventDefault();
      handleGlobalSearch();
    }
  };

  const handleGlobalSearch = () => {
    if (!query.trim()) return;
    setIsOpen(false);
    router.push(`/?busqueda=${encodeURIComponent(query.trim())}#catalogo`);
  };

  const handleSelectProduct = () => {
    setIsOpen(false);
    setQuery("");
  };

  const handleImageError = (id: number) => {
    setFailedImages((prev) => ({ ...prev, [id]: true }));
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-md mx-auto">
      {/* Campo de Entrada de Búsqueda SaaS (Alto Contraste y Limpieza) */}
      <div className="relative flex items-center group/search bg-slate-100/80 hover:bg-slate-100 focus-within:bg-white border border-slate-200/80 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 rounded-full transition-all duration-200">
        
        {/* Icono de Lupa (Azul de marca) */}
        <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-blue-600 pointer-events-none transition-colors">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (e.target.value.trim().length >= 2) setIsOpen(true);
          }}
          onFocus={() => {
            if (query.trim().length >= 2) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder="Buscar suplementos, marcas..."
          className="w-full pl-10 pr-8 py-1.5 sm:py-2 bg-transparent text-slate-900 caret-slate-900 font-medium text-sm placeholder:text-slate-500 focus:outline-none"
          style={{ color: '#0f172a', caretColor: '#0f172a' }}
        />

        {/* Botón Borrar (X) únicamente cuando hay texto (Sin píldora Ctrl+K) */}
        {query && (
          <button
            onClick={() => {
              setQuery("");
              setResults([]);
              setIsOpen(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-0.5 rounded-full cursor-pointer"
            title="Limpiar búsqueda"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Popover Desplegable Live (Fondo Blanco Limpio Sobrio) */}
      {isOpen && query.trim().length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-2 z-50 !bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden p-4 animate-in fade-in-50 zoom-in-95 duration-150">
          {loading ? (
            /* Estado de Carga (Skeletons Animados) */
            <div className="p-2 space-y-2">
              {[1, 2, 3].map((idx) => (
                <div key={idx} className="flex items-center gap-3 animate-pulse p-1.5">
                  <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex-shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-2.5 bg-slate-100 dark:bg-slate-800 rounded w-16" />
                    <div className="h-3 bg-slate-100 dark:bg-slate-800 rounded w-3/4" />
                  </div>
                  <div className="w-12 h-5 bg-slate-100 dark:bg-slate-800 rounded-md" />
                </div>
              ))}
            </div>
          ) : results.length > 0 ? (
            /* Resultados de Coincidencias (Máximo 4) */
            <div className="space-y-1">
              {results.map((product) => {
                const formattedName = formatTitle(decodeHTML(product.name), product.brand?.name);
                const priceToDisplay = product.precio_actual ?? product.price;

                return (
                  <Link
                    key={product.id}
                    href={product.slug ? `/producto/${product.slug}` : `/#catalogo`}
                    onClick={handleSelectProduct}
                    className="group flex items-center gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-800/60 rounded-xl transition-colors cursor-pointer"
                  >
                    {/* Thumbnail 40x40px */}
                    <div className="w-10 h-10 flex-shrink-0 bg-slate-50 dark:bg-slate-800 p-1 rounded-lg border border-slate-100 dark:border-slate-700/80 flex items-center justify-center overflow-hidden">
                      {product.image_url && !failedImages[product.id] ? (
                        <img
                          src={product.image_url}
                          alt={formattedName}
                          onError={() => handleImageError(product.id)}
                          className="w-full h-full object-contain group-hover:scale-105 transition-transform"
                        />
                      ) : (
                        <div className="text-[9px] font-black text-slate-400 text-center uppercase">
                          {product.brand?.name || "TS"}
                        </div>
                      )}
                    </div>

                    {/* Bloque Central (Marca + Título) */}
                    <div className="flex-1 min-w-0">
                      <div className="text-[10px] font-black tracking-wider text-slate-400 dark:text-slate-500 uppercase truncate">
                        {product.brand?.name || "Sin marca"}
                      </div>
                      <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-100 line-clamp-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {formattedName}
                      </h4>
                    </div>

                    {/* Precio (Derecha) */}
                    <div className="text-xs font-bold text-slate-900 dark:text-white bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md ml-auto flex-shrink-0">
                      {priceToDisplay?.toFixed(2)} €
                    </div>
                  </Link>
                );
              })}

              {/* Pie del Desplegable ("Ver todos") */}
              <button
                onClick={handleGlobalSearch}
                className="w-full text-left p-2.5 mt-1 text-xs font-bold text-blue-600 dark:text-blue-400 bg-slate-50/80 dark:bg-slate-800/40 hover:bg-blue-50 dark:hover:bg-slate-800 rounded-xl transition-colors flex items-center justify-between cursor-pointer"
              >
                <span>Ver todos los resultados para &quot;{query.trim()}&quot;</span>
                <span className="text-sm font-extrabold ml-1">→</span>
              </button>
            </div>
          ) : (
            /* Estado Sin Resultados */
            <div className="!bg-slate-50 p-6 text-center rounded-xl border border-slate-100">
              <svg className="w-8 h-8 text-slate-400 mx-auto mb-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
              <p className="text-sm font-bold !text-slate-800 mb-1">
                No se encontraron productos para &quot;{query.trim()}&quot;
              </p>
              <p className="text-xs !text-slate-500">
                Prueba a buscar por ingrediente (ej. Creatina, Whey) o por marca (ej. HSN, Prozis).
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
