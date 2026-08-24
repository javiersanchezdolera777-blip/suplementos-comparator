'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useCompareStore } from '@/store/useCompareStore';

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
  const escapedMarca = marca.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`^${escapedMarca}\\s+`, 'i');
  return nombre.replace(regex, '');
};

export default function VersusPage() {
  const { compareIds, removeId } = useCompareStore();
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (compareIds.length === 0) {
      setProductos([]);
      return;
    }

    const fetchComparativa = async () => {
      setLoading(true);
      try {
        const idsParam = compareIds.join(',');
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/productos/comparar?ids=${idsParam}`);
        if (!res.ok) throw new Error('Error al cargar la comparativa');

        const data = await res.json();
        setProductos(data);
      } catch (error) {
        console.error("Error fetching compare data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchComparativa();
  }, [compareIds]);

  if (compareIds.length === 0) {
    return (
      <div className="min-h-[80vh] bg-gray-50 flex flex-col items-center justify-center p-6 text-center">
        <h1 className="text-4xl font-black text-gray-900 mb-4">Comparativa Cara a Cara ⚖️</h1>
        <p className="text-gray-500 mb-8 max-w-md">No has seleccionado ningún producto. Visita el catálogo y elige a los contendientes para ver quién es el ganador.</p>
        <Link className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/20" href="/">
          Explorar Catálogo
        </Link>
      </div>
    );
  }

  // --- FILTROS INTELIGENTES PARA MOSTRAR/OCULTAR FILAS ---
  const hasFormat = productos.some(p => p.format || p.formato);
  const hasFlavors = productos.some(p => {
    const f = p.flavor || p.sabor;
    return Array.isArray(f) ? f.length > 0 : (f && f !== '-');
  });
  const hasDiet = productos.some(p => p.is_vegan || p.es_vegano || p.sin_gluten || p.sin_lactosa);
  const hasQualitySeal = productos.some(p => p.quality_seal || p.sello_calidad);
  const hasProteinPercentage = productos.some(p => (p.protein_percentage ?? p.porcentaje_proteina) > 0);
  const hasSpecificProfile = productos.some(p => p.protein_type || p.tipo_proteina || p.creatine_type || p.tipo_creatina || p.amino_profile || p.perfil_aminoacidos || p.vitamin_type || p.tipo_vitamina);

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6 lg:p-8 flex flex-col">
      <div className="max-w-[1400px] mx-auto w-full flex-1 flex flex-col justify-center py-4">
        <div className="mb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-black text-gray-900">Comparativa Cara a Cara ⚖️</h1>
          </div>
          <Link href="/" className="group flex items-center gap-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-900 transition-all px-4 py-2 rounded-xl shadow-sm hover:shadow-md">
            <svg className="w-4 h-4 text-slate-400 group-hover:-translate-x-1 transition-all duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver al catálogo
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-2xl shadow-sm border border-gray-100">
            <span className="animate-pulse text-lg font-bold text-gray-400">Preparando el cuadrilátero...</span>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden w-full text-sm">
            <div className="w-full">

              {/* CABECERA (Ricitos de Oro) */}
              <div className="flex border-b border-gray-200 bg-gray-50/50">
                <div className="w-28 md:w-40 p-3 md:p-5 shrink-0 flex items-end">
                  <span className="font-bold text-gray-400 uppercase tracking-wider text-[10px] md:text-xs">Características</span>
                </div>
                {productos.map(prod => {
                  const brandName = prod.brand?.name || "HSN";
                  const formattedName = formatTitle(decodeHTML(prod.name), brandName);
                  const currentPrice = prod.precio_actual ?? prod.price ?? 0;
                  
                  return (
                    <div key={prod.id} className="flex-1 p-3 md:p-5 border-l border-gray-200 flex flex-col relative group min-w-0">
                      <button
                        onClick={() => removeId(prod.id)}
                        className="absolute top-2 right-2 md:top-3 md:right-3 text-gray-300 hover:text-red-500 transition font-black bg-white rounded-full w-6 h-6 md:w-8 md:h-8 flex items-center justify-center shadow-sm opacity-100 md:opacity-0 md:group-hover:opacity-100 z-10 border border-gray-100"
                        title="Eliminar de la comparativa"
                      >
                        <span className="text-xs md:text-sm">✕</span>
                      </button>
                      <div className="h-24 md:h-28 w-full flex items-center justify-center mb-2 bg-white rounded-xl border border-gray-100 p-2 md:p-3">
                        <img src={prod.image_url || prod.imagen_url || '/placeholder.png'} alt={formattedName} className="max-h-full max-w-full object-contain mix-blend-multiply" />
                      </div>
                      <span className="text-[10px] md:text-xs text-blue-600 font-black tracking-widest uppercase mb-1 truncate">{brandName}</span>
                      <h3 className="text-xs md:text-sm font-bold text-gray-900 leading-snug line-clamp-2 h-8 md:h-10" title={formattedName}>{formattedName}</h3>
                      <div className="mt-1 md:mt-2 flex items-baseline gap-1">
                        <span className="text-lg md:text-xl font-black text-gray-900">{currentPrice.toFixed(2)}</span>
                        <span className="text-gray-500 font-semibold text-xs md:text-sm">€</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* FILA: FORMATO */}
              {hasFormat && (
                <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <div className="w-28 md:w-40 py-3 md:py-3.5 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                    <span className="text-xs md:text-sm font-semibold text-gray-600">📦 Formato</span>
                  </div>
                  {productos.map(prod => (
                    <div key={prod.id} className="flex-1 py-3 md:py-3.5 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                      <span className="text-xs md:text-sm font-medium text-gray-600 capitalize truncate" title={prod.format || prod.formato || '-'}>
                        {prod.format || prod.formato || '-'}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* FILA: SABORES */}
              {hasFlavors && (
                <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <div className="w-28 md:w-40 py-3 md:py-3.5 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                    <span className="text-xs md:text-sm font-semibold text-gray-600">👅 Sabores</span>
                  </div>
                  {productos.map(prod => {
                    const flavs = prod.flavor || prod.sabor;
                    const display = Array.isArray(flavs) && flavs.length > 0 
                            ? flavs.join(', ') 
                            : (flavs && typeof flavs === 'string' ? flavs : '-');
                    return (
                      <div key={prod.id} className="flex-1 py-3 md:py-3.5 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                        <span className="text-[11px] md:text-xs font-medium text-gray-600 line-clamp-2" title={display}>
                          {display}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* FILA: DIETA / ALÉRGENOS */}
              {hasDiet && (
                <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <div className="w-28 md:w-40 py-3 md:py-3.5 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                    <span className="text-xs md:text-sm font-semibold text-gray-600">🌱 Dieta / Alérgenos</span>
                  </div>
                  {productos.map(prod => {
                    const tags = [];
                    if (prod.is_vegan || prod.es_vegano) tags.push("Vegano");
                    if (prod.sin_gluten) tags.push("Sin gluten");
                    if (prod.sin_lactosa) tags.push("Sin lactosa");
                    const label = tags.length > 0 ? tags.join(' · ') : '-';
                    return (
                      <div key={prod.id} className="flex-1 py-3 md:py-3.5 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                        <span className={`text-[11px] md:text-xs font-medium line-clamp-2 ${tags.length > 0 ? 'text-emerald-700 font-semibold' : 'text-gray-600'}`} title={label}>
                          {label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* FILA: SELLOS DE CALIDAD */}
              {hasQualitySeal && (
                <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <div className="w-28 md:w-40 py-3 md:py-3.5 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                    <span className="text-xs md:text-sm font-semibold text-gray-600">🏅 Sello de calidad</span>
                  </div>
                  {productos.map(prod => (
                    <div key={prod.id} className="flex-1 py-3 md:py-3.5 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                      <span className="text-[11px] md:text-xs font-medium text-gray-600 truncate" title={prod.quality_seal || prod.sello_calidad || '-'}>
                        {prod.quality_seal || prod.sello_calidad || '-'}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* FILA: PORCENTAJE DE PROTEÍNA */}
              {hasProteinPercentage && (
                <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <div className="w-28 md:w-40 py-3 md:py-3.5 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                    <span className="text-xs md:text-sm font-semibold text-gray-600">💪 % Proteína</span>
                  </div>
                  {productos.map(prod => {
                    const perc = prod.protein_percentage ?? prod.porcentaje_proteina;
                    return (
                      <div key={prod.id} className="flex-1 py-3 md:py-3.5 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                        <span className="text-xs md:text-sm font-bold text-gray-700">
                          {perc ? `${perc}%` : '-'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* FILA: PERFIL ESPECÍFICO */}
              {hasSpecificProfile && (
                <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <div className="w-28 md:w-40 py-3 md:py-3.5 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                    <span className="text-xs md:text-sm font-semibold text-gray-600">🧬 Perfil Específico</span>
                  </div>
                  {productos.map(prod => {
                    let perfilStr = '-';
                    if (prod.protein_type || prod.tipo_proteina) {
                      perfilStr = prod.protein_type || prod.tipo_proteina;
                    } else if (prod.creatine_type || prod.tipo_creatina) {
                      perfilStr = prod.creatine_type || prod.tipo_creatina;
                    } else if (prod.amino_profile || prod.perfil_aminoacidos) {
                      perfilStr = prod.amino_profile || prod.perfil_aminoacidos;
                    } else if (prod.vitamin_type || prod.tipo_vitamina) {
                      perfilStr = prod.vitamin_type || prod.tipo_vitamina;
                    }

                    return (
                      <div key={prod.id} className="flex-1 py-3 md:py-3.5 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                        {perfilStr !== '-' ? (
                          <span className="text-[11px] md:text-xs font-medium text-blue-700 bg-blue-50 px-2 py-1 rounded truncate max-w-full" title={perfilStr}>
                            {perfilStr}
                          </span>
                        ) : (
                          <span className="text-xs md:text-sm font-medium text-gray-600">-</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* FILA: ACCIÓN (COMPRAR) */}
              <div className="flex bg-gray-50/50 rounded-b-2xl">
                <div className="w-28 md:w-40 py-3 md:py-4 px-3 md:px-4 shrink-0 border-r border-gray-100 flex items-center">
                  {/* Celda vacía para dar aire al diseño en el footer de la tabla */}
                </div>
                {productos.map(prod => {
                  const url = prod.affiliate_url || prod.afiliado_url || "#";
                  return (
                    <div key={prod.id} className="flex-1 py-3 md:py-4 px-3 md:px-4 border-r border-gray-100 flex items-center justify-center text-center last:border-r-0 min-w-0">
                      <a 
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full max-w-[140px] bg-slate-900 hover:bg-slate-800 text-white font-bold text-[10px] md:text-xs py-2 md:py-2.5 px-2 md:px-4 rounded-lg transition-transform active:scale-95 shadow-md inline-block truncate"
                      >
                        Ver oferta
                      </a>
                    </div>
                  );
                })}
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}

