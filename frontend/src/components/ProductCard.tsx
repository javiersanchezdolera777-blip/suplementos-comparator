"use client";

import Image from 'next/image';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../context/AuthContext';
import { useCompareStore } from '@/store/useCompareStore';

export interface Oferta {
  id: number;
  tienda: string;
  precio: number;
  precio_anterior?: number | null;
  precio_por_kg?: number | null;
  afiliado_url: string;
  activo: boolean;
}

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  precio_anterior?: number | null;
  precio_actual?: number | null;
  image_url: string;
  affiliate_url: string;
  slug?: string;
  brand: {
    name: string;
  };
  category: {
    name: string;
  };
  tienda?: string | { name: string } | null;
  tienda_nombre?: string | null;
  store?: string | { name: string } | null;
  format?: string;
  is_vegan?: boolean;
  quality_seal?: string;
  protein_type?: string;
  protein_percentage?: number;
  porcentaje_proteina?: number;
  creatine_type?: string;
  amino_profile?: string;
  vitamin_type?: string;
  price_per_kg?: number | null;
  // El backend ahora puede enviar múltiples sabores por producto
  flavor?: string[] | string | null;
  presentacion?: string;
  ofertas?: Oferta[];
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

const sanitizeDescription = (text?: string | null): string => {
  if (!text) return "";
  let cleaned = text.trim();

  // 1. Eliminar preguntas genéricas de relleno SEO al inicio del texto (ej: "¿por qué debemos utilizar...?")
  cleaned = cleaned.replace(/^¿por qué [^?]+\?\s*/i, '');

  // 2. Corregir puntos pegados a palabras sin espacio (ej: "apatía.es frecuente" -> "apatía. es frecuente")
  cleaned = cleaned.replace(/\.([a-zA-ZáéíóúñÁÉÍÓÚÑ])/g, '. $1');

  // 3. Capitalizar la primera letra después de un punto y seguido (ej: ". los más" -> ". Los más")
  cleaned = cleaned.replace(/\.\s+([a-zñáéíóú])/g, (_, letter) => `. ${letter.toUpperCase()}`);

  // 4. Capitalizar la primera letra alfabética del texto (incluso si empieza por signos como ¿, ", ()
  cleaned = cleaned.replace(/^([^a-zA-ZáéíóúñÁÉÍÓÚÑ]*)([a-zñáéíóú])/, (_, prefix, letter) => prefix + letter.toUpperCase());

  return cleaned;
};

const formatTitle = (nombre: string, marca?: string, presentacion?: string) => {
  if (!nombre) return "";
  let cleaned = nombre;

  if (marca) {
    const escapedMarca = marca.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regexMarca = new RegExp(`^${escapedMarca}\\s+`, 'i');
    cleaned = cleaned.replace(regexMarca, '');
  }

  if (presentacion) {
    // Escapar regex primero, luego cambiar espacios por \s*
    const escapedPres = presentacion.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s*');
    const regexPres = new RegExp(`[\\s\\-,|]*${escapedPres}(?![a-zA-ZáéíóúÁÉÍÓÚ])`, 'gi');
    cleaned = cleaned.replace(regexPres, '');
  }

  cleaned = cleaned.replace(/^[\s\-,|]+/, '').replace(/[\s\-,|]+$/, '');
  return cleaned.trim() || nombre.trim();
};

const formatStoreName = (name: string) => {
  if (!name) return "";
  const lower = name.trim().toLowerCase();
  if (lower === 'hsn') return 'HSN';
  if (lower === 'farma2go' || lower === 'pharma2go') return 'Farma2Go';
  if (lower === 'amazon') return 'Amazon';
  if (lower === 'miravia') return 'Miravia';
  if (lower === 'promofarma') return 'PromoFarma';
  if (lower === 'nutritienda') return 'Nutritienda';
  return lower.replace(/\b\w/g, c => c.toUpperCase());
};

const AFFILIATE_NETWORKS = ['tradedoubler', 'awin', 'cj', 'impact', 'webgains', 'belboon', 'zanox', 'linkshare', 'tradetracker', 'hsnafiliados', 'hsnaffiliates', 'amazonafiliados', 'zumub'];


export default function ProductCard({ product }: { product: Product }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { isLoggedIn, openLoginModal, token, favoriteIds, addFavoriteId, removeFavoriteId } = useAuth();

  const { addId, removeId, compareIds } = useCompareStore();
  const isCompared = compareIds.includes(product.id);

  const [imageError, setImageError] = useState(false);
  const isFavorite = favoriteIds.includes(product.id);
  const showImage = product.image_url && product.image_url.trim() !== "" && !imageError;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Lógica estricta para extraer tienda vendedora real (NUNCA usar marca como fallback)
  const rawStore =
    (typeof product.tienda === 'object' && product.tienda?.name) ||
    (typeof product.tienda === 'string' && product.tienda) ||
    (typeof product.tienda_nombre === 'string' && product.tienda_nombre) ||
    (typeof product.store === 'object' && product.store?.name) ||
    (typeof product.store === 'string' && product.store) ||
    "";

  // Detectar tienda de forma infalible buscando patrones en la cadena de la URL completa
  const getStoreFromUrl = (url: string): string => {
    if (!url) return "";
    const lowerUrl = url.toLowerCase();

    if (lowerUrl.includes('sportlive')) return 'SportLive';
    if (lowerUrl.includes('hsnstore') || lowerUrl.includes('hsn.')) return 'HSN';
    if (lowerUrl.includes('farma2go') || lowerUrl.includes('pharma2go')) return 'Farma2Go';
    if (lowerUrl.includes('prozis')) return 'Prozis';
    if (lowerUrl.includes('myprotein')) return 'MyProtein';
    if (lowerUrl.includes('bulk')) return 'Bulk';
    if (lowerUrl.includes('amazon')) return 'Amazon';
    if (lowerUrl.includes('miravia')) return 'Miravia';
    if (lowerUrl.includes('promofarma')) return 'PromoFarma';
    if (lowerUrl.includes('nutritienda')) return 'Nutritienda';
    if (lowerUrl.includes('masmusculo')) return 'MasMusculo';
    if (lowerUrl.includes('pontemasfuerte')) return 'PonteMasFuerte';
    if (lowerUrl.includes('zumub')) return 'Zumub';

    return "";
  };

  // Determinar la tienda vendedora real
  const urlStore = getStoreFromUrl(product.affiliate_url);
  const rawDbStore = rawStore;
  const cleanDbStore = rawDbStore && !['tradedoubler', 'awin', 'cj'].some(net => rawDbStore.toLowerCase().includes(net)) ? rawDbStore : null;

  // La tienda detectada en la URL MANDA siempre. Si no, usa la de la base de datos saneada.
  const sellerStore = urlStore || cleanDbStore;

  const brandName = product.brand?.name || "";

  // Comprobar si marca y tienda son la misma entidad (ej: HSN == HSN)
  const isSameBrandAndStore =
    brandName.trim().toLowerCase() !== "" &&
    sellerStore !== null &&
    brandName.trim().toLowerCase() === sellerStore.trim().toLowerCase();

  const previousPrice = product.precio_anterior ?? null;
  const currentPrice = product.precio_actual ?? product.price;
  const hasOffer = previousPrice !== null && previousPrice > currentPrice;
  const discountPercentage = hasOffer
    ? Math.round(((previousPrice - currentPrice) / previousPrice) * 100)
    : 0;

  const formattedName = formatTitle(decodeHTML(product.name), product.brand?.name, product.presentacion);
  const cleanDescription = sanitizeDescription(product.description);
  const isLongDescription = cleanDescription.length > 230;

  const handleOpenProduct = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setIsExpanded(false);
  };

  const toggleFavorite = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (!isLoggedIn) {
      openLoginModal();
      return;
    }

    try {
      if (isFavorite) {
        removeFavoriteId(product.id);
        setToastMsg("Eliminado de tus favoritos");
        setTimeout(() => setToastMsg(null), 2000);

        const res = await fetch(`${apiUrl}/api/favoritos/${product.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) addFavoriteId(product.id);
      } else {
        addFavoriteId(product.id);
        setToastMsg("Guardado en tus favoritos");
        setTimeout(() => setToastMsg(null), 2000);

        const res = await fetch(`${apiUrl}/api/favoritos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ producto_id: product.id })
        });
        if (!res.ok) removeFavoriteId(product.id);
      }
    } catch (error) {
      console.error("Error al actualizar favorito", error);
    }
  };

  const handleCompare = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isLoggedIn) {
      openLoginModal();
      return;
    }
    if (isCompared) {
      removeId(product.id);
    } else {
      addId(product.id);
    }
  };

  return (
    <>
      <div
        className="group relative flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-slate-300 transition-all duration-200 shadow-sm hover:shadow-lg hover:-translate-y-1 cursor-pointer"
        onClick={handleOpenProduct}
      >

        {/* Zona Superior: Imagen y Badges */}
        <div className="relative h-32 md:h-48 p-2 md:p-4 flex items-center justify-center bg-slate-50 overflow-hidden">
          {showImage ? (
            <img
              src={product.image_url}
              alt={formattedName}
              onError={() => setImageError(true)}
              className="w-full h-24 md:h-32 object-contain group-hover:scale-105 transition-transform duration-500 ease-out relative z-10"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-slate-100 rounded-2xl border border-slate-200/80 p-2 md:p-4 text-center relative z-10">
              <span className="text-slate-400 font-extrabold tracking-[0.2em] text-[8px] md:text-xs uppercase mb-1">Tus Suplementos</span>
              <span className="text-slate-400 text-[9px] md:text-[10px] font-semibold">{product.brand?.name || "Oficial"}</span>
            </div>
          )}

          {/* Badges Superpuestos Superior Izquierda: Tienda Origen y Oferta */}
          <div className="absolute top-2.5 left-2.5 z-20 flex flex-col items-start gap-1 pointer-events-none max-w-[calc(100%-65px)]">
            {hasOffer && (
              <span className="bg-red-600 text-white font-extrabold text-[11px] px-2 py-0.5 rounded-md shadow-sm">
                -{discountPercentage}%
              </span>
            )}
          </div>

          {/* Badge de Categoría */}
          <div className="absolute bottom-3 left-3 z-20 pointer-events-none">
            <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-white/90 text-slate-700 border border-slate-200/80 shadow-sm rounded-md backdrop-blur-md">
              {product.category?.name || "Sin categoría"}
            </span>
          </div>

          <div className="absolute top-3 right-3 z-20 group/heart cursor-pointer active:scale-125 transition-transform duration-200" onClick={toggleFavorite}>
            <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm ${isFavorite
              ? "bg-red-50 border-red-200 scale-105"
              : "bg-white/90 border-slate-200 group-hover/heart:bg-slate-100 group-hover/heart:border-slate-300"
              }`} title={isFavorite ? "Quitar de favoritos" : "Guardar en favoritos"}>
              <svg
                className={`w-4 h-4 transition-colors duration-200 ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-slate-600"}`}
                fill={isFavorite ? "currentColor" : "none"}
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
          </div>

          {/* Botón VS (Comparar) flotante debajo del corazón */}
          <div className="absolute top-14 right-3 z-20 group/vs cursor-pointer active:scale-125 transition-transform duration-200" onClick={handleCompare}>
            <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm flex items-center justify-center w-[34px] h-[34px] ${isCompared
              ? "bg-blue-50 border-blue-200 scale-105"
              : "bg-white/90 border-slate-200 group-hover/vs:bg-slate-100 group-hover/vs:border-slate-300"
              }`} title={isCompared ? "Ya en la comparativa" : "Añadir a comparativa"}>
              <span className={`text-[10px] font-black tracking-tighter ${isCompared ? "text-blue-600" : "text-slate-400 group-hover/vs:text-slate-600"}`}>VS</span>
            </div>
          </div>
        </div>

        {/* Zona Inferior: Información del producto (Limpia y Sobria con Alto Contraste) */}
        <div className="p-3 md:p-5 flex flex-col flex-grow bg-white border-t border-slate-100">
          <div className="flex flex-col mb-1.5">
            <span className="text-[10px] md:text-xs font-bold uppercase tracking-wider text-slate-900 truncate">
              {brandName || "Sin marca"}
            </span>
          </div>

          <div className="flex flex-col flex-grow mt-1.5">
            <h3 className="text-xs md:text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug flex-grow mt-1.5">
              {formattedName}
              {product.presentacion && (
                <span className="text-[11px] md:text-xs font-medium text-slate-500 ml-1.5 inline-block">
                  {product.presentacion}
                </span>
              )}
            </h3>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mt-auto pt-3 md:pt-4 gap-2">
            <div className="flex items-center flex-wrap gap-1.5">
              <span className="flex items-baseline gap-1 whitespace-nowrap text-lg md:text-2xl font-extrabold text-slate-900 tracking-tight">
                <span>{currentPrice?.toFixed(2)}</span>
                <span className="text-base md:text-xl font-bold text-slate-700">€</span>
              </span>
              {hasOffer && (
                <span className="flex items-baseline gap-1 whitespace-nowrap text-xs md:text-sm font-semibold text-slate-400 line-through ml-1">
                  <span>{previousPrice?.toFixed(2)}</span>
                  <span className="text-[10px] md:text-xs">€</span>
                </span>
              )}
            </div>

            <a
              href={product.slug && sellerStore ? `${apiUrl}/api/out/${sellerStore.toLowerCase()}/${product.slug}` : (product.affiliate_url || "#")}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-[10px] md:text-xs px-3 py-2 md:px-4 md:py-2.5 rounded-lg md:rounded-xl transition-all shadow-sm cursor-pointer whitespace-nowrap self-start sm:self-auto"
            >
              Ver oferta
            </a>
          </div>
        </div>
      </div>

      {/* Modal Quick View via React Portal a document.body */}
      {mounted && isModalOpen && createPortal(
        <div
          className="fixed inset-0 z-[99999] w-screen h-screen bg-black/80 backdrop-blur-md flex items-center justify-center p-4 md:p-6 overflow-hidden"
          onClick={closeModal}
        >
          <div
            className="relative w-full max-w-4xl h-[85vh] max-h-[680px] bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row animate-in zoom-in-95 duration-300"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Micro-Toast Notificación Favoritos */}
            {toastMsg && (
              <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[60] bg-slate-900/90 text-white text-xs font-bold px-4 py-2 rounded-full shadow-lg backdrop-blur-md animate-in fade-in zoom-in duration-200">
                {toastMsg}
              </div>
            )}

            <button
              onClick={closeModal}
              className="absolute top-4 right-4 z-50 p-2 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors text-slate-500 cursor-pointer shadow-sm"
              title="Cerrar modal"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Columna Izquierda: Imagen */}
            <div className="w-full md:w-1/2 h-48 md:h-full bg-slate-50 p-6 md:p-8 flex items-center justify-center relative overflow-hidden border-b md:border-b-0 md:border-r border-slate-100">
              {showImage ? (
                <img
                  src={product.image_url}
                  alt={formattedName}
                  onError={() => setImageError(true)}
                  className="w-full h-full object-contain max-h-full max-w-full drop-shadow-md"
                />
              ) : (
                <div className="flex flex-col items-center justify-center text-center p-4">
                  <span className="text-slate-400 font-black tracking-[0.2em] text-base uppercase mb-1">Tus Suplementos</span>
                  <span className="text-slate-400 text-xs font-semibold">{product.brand?.name || "Oficial"}</span>
                </div>
              )}
            </div>

            {/* Columna Derecha: Información y Scroll Exclusivo para Textos */}
            <div className="w-full md:w-1/2 flex flex-col h-full bg-white p-6 md:p-8 relative overflow-hidden">
              {/* Zona Superior Fija */}
              <div className="flex justify-between items-start mb-2 pr-10">
                <div className="flex flex-col mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      {brandName || "Sin marca"}
                    </span>
                  </div>
                </div>

                <div className="flex items-center">
                  <div className="group/heart cursor-pointer active:scale-125 transition-transform duration-200 mt-1" onClick={toggleFavorite}>
                    <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm ${isFavorite
                      ? "bg-red-50 border-red-200 scale-105"
                      : "bg-white border-slate-200 group-hover/heart:bg-slate-50"
                      }`} title={isFavorite ? "Quitar de favoritos" : "Guardar en favoritos"}>
                      <svg
                        className={`w-5 h-5 transition-colors duration-200 ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-slate-600"}`}
                        fill={isFavorite ? "currentColor" : "none"}
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </div>
                  </div>

                  <div className="group/vs cursor-pointer active:scale-125 transition-transform duration-200 mt-1 ml-2" onClick={handleCompare}>
                    <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm flex items-center justify-center w-9 h-9 ${isCompared
                      ? "bg-blue-50 border-blue-200 scale-105"
                      : "bg-white border-slate-200 group-hover/vs:bg-slate-50"
                      }`} title={isCompared ? "Ya en la comparativa" : "Añadir a comparativa"}>
                      <span className={`text-[11px] font-black tracking-tighter ${isCompared ? "text-blue-600" : "text-slate-400 group-hover/vs:text-slate-600"}`}>VS</span>
                    </div>
                  </div>
                </div>
              </div>

              <h2 className="text-xl sm:text-2xl font-black text-slate-900 mb-2 leading-snug">{formattedName}</h2>
              <div className="flex items-center flex-wrap gap-3 mb-4">
                <span className="flex items-baseline gap-1 whitespace-nowrap text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
                  <span>{currentPrice?.toFixed(2)}</span>
                  <span className="text-xl md:text-2xl font-bold text-slate-700">€</span>
                </span>
                {hasOffer && (
                  <span className="flex items-baseline gap-1 whitespace-nowrap text-base font-semibold text-slate-400 line-through">
                    <span>{previousPrice?.toFixed(2)}</span>
                    <span className="text-sm">€</span>
                  </span>
                )}
              </div>

              {/* Zona Central con Scroll Interno Exclusivo */}
              <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar my-2">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-100 text-sm w-full">
                  <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Categoría</span><span className="text-slate-700 font-medium">{product.category?.name || '-'}</span></div>
                  <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Formato</span><span className="text-slate-700 font-medium">{product.format || '-'}</span></div>
                  <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tamaño</span><span className="text-slate-700 font-medium">{product.presentacion || '-'}</span></div>

                  <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Sabores</span><span className="text-slate-700 font-medium">{Array.isArray(product.flavor) ? (product.flavor.length ? product.flavor.join(', ') : '-') : (product.flavor ? String(product.flavor) : '-')}</span></div>

                  {product.is_vegan && <div className="flex flex-col"><span className="text-[10px] text-emerald-600 uppercase font-bold tracking-wider">Dietético</span><span className="text-emerald-700 font-medium">100% Vegano</span></div>}
                  {product.protein_type && <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Proteína</span><span className="text-slate-700 font-medium">{product.protein_type}</span></div>}
                  {(product.protein_percentage || product.porcentaje_proteina) && (
                    <div className="flex flex-col">
                      <span className="text-[10px] text-blue-600 uppercase font-bold tracking-wider">% Proteína</span>
                      <span className="text-slate-700 font-medium">{product.protein_percentage ?? product.porcentaje_proteina}%</span>
                    </div>
                  )}
                  {product.quality_seal && <div className="flex flex-col"><span className="text-[10px] text-blue-500 uppercase font-bold tracking-wider">Sello Calidad</span><span className="text-blue-600 font-medium">{product.quality_seal}</span></div>}
                </div>
              </div>

              {/* Zona Inferior Fija / Anclada: TABLA MULTI-TIENDA COMPACTA */}
              <div className="pt-4 border-t border-slate-100 mt-auto">
                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Ofertas Disponibles
                </h3>

                {product.ofertas && product.ofertas.filter((o) => o.activo).length > 0 ? (
                  <div className="flex flex-col gap-2 max-h-[150px] overflow-y-auto custom-scrollbar pr-1">
                    {product.ofertas
                      .filter((o) => o.activo)
                      .sort((a, b) => a.precio - b.precio)
                      .map((oferta, index) => (
                        <div
                          key={oferta.id}
                          className={`flex items-center justify-between p-2.5 rounded-xl border ${index === 0
                            ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                            : "border-slate-200 bg-white dark:bg-slate-800"
                            }`}
                        >
                          {/* Tienda */}
                          <div className="flex flex-col">
                            <span className="font-extrabold text-slate-900 dark:text-white text-sm">
                              {oferta.tienda}
                            </span>
                          </div>

                          {/* Precio y Cloaker */}
                          <div className="flex items-center gap-3">
                            <span className={`font-black ${index === 0 ? "text-green-700 dark:text-green-400" : "text-slate-900 dark:text-white"}`}>
                              {oferta.precio.toFixed(2)} €
                            </span>
                            <a
                              href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/out/${oferta.tienda.toLowerCase()}/${product.slug}`}
                              target="_blank"
                              rel="nofollow noopener noreferrer"
                              className={`px-4 py-1.5 rounded-lg font-bold text-xs transition-all shadow-sm ${index === 0
                                ? "bg-green-600 hover:bg-green-700 text-white"
                                : "bg-slate-900 hover:bg-slate-800 text-white"
                                }`}
                            >
                              Ver
                            </a>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="p-3 bg-red-50 text-red-600 rounded-xl border border-red-200 text-xs font-medium">
                    Actualmente no hay ofertas activas.
                  </div>
                )}

                {/* Enlace real a la página SEO */}
                <div className="mt-4 text-center">
                  <Link
                    href={`/producto/${product.slug}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      closeModal();
                    }}
                    className="text-xs font-bold text-blue-600 hover:text-blue-800 transition-colors inline-block pb-1 border-b border-transparent hover:border-blue-800"
                  >
                    Ver ficha técnica completa &rarr;
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
