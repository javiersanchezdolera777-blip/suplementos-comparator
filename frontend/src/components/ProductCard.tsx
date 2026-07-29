"use client";

import Image from 'next/image';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../context/AuthContext';

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

// Helper para limpiar el nombre del producto si ya empieza por la marca (evita redundancia)
const formatTitle = (nombre: string, marca?: string) => {
  if (!marca || !nombre) return nombre;
  const escapedMarca = marca.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`^${escapedMarca}\\s+`, 'i');
  return nombre.replace(regex, '');
};

export default function ProductCard({ product }: { product: Product }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { isLoggedIn, openLoginModal, token, favoriteIds, addFavoriteId, removeFavoriteId } = useAuth();
  
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

  const brandName = product.brand?.name || "";

  // Solo renderizar si existe tienda vendedora real y NO coincide con la marca del producto
  const sellerStore =
    rawStore && rawStore.trim().toLowerCase() !== brandName.trim().toLowerCase()
      ? rawStore.trim()
      : null;

  const previousPrice = product.precio_anterior ?? null;
  const currentPrice = product.precio_actual ?? product.price;
  const hasOffer = previousPrice !== null && previousPrice > currentPrice;
  const discountPercentage = hasOffer
    ? Math.round(((previousPrice - currentPrice) / previousPrice) * 100)
    : 0;

  const formattedName = formatTitle(decodeHTML(product.name), product.brand?.name);

  const handleOpenProduct = () => {
    setIsModalOpen(true);
    if (product.slug) {
      window.history.pushState(null, "", `/producto/${product.slug}`);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setIsExpanded(false);
    if (typeof window !== "undefined") {
      window.history.pushState(null, "", "/");
    }
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

  return (
    <>
      <div 
        className="group relative flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-slate-300 transition-all duration-200 shadow-sm hover:shadow-lg hover:-translate-y-1 cursor-pointer"
        onClick={handleOpenProduct}
      >
        
        {/* Zona Superior: Imagen y Badges */}
        <div className="relative aspect-square p-6 sm:p-8 flex items-center justify-center bg-slate-50 overflow-hidden">
          {showImage ? (
            <img
              src={product.image_url}
              alt={formattedName}
              onError={() => setImageError(true)}
              className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500 ease-out relative z-10"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-slate-100 rounded-2xl border border-slate-200/80 p-4 text-center relative z-10">
              <span className="text-slate-400 font-extrabold tracking-[0.2em] text-xs uppercase mb-1">Tus Suplementos</span>
              <span className="text-slate-400 text-[10px] font-semibold">{product.brand?.name || "Oficial"}</span>
            </div>
          )}

          {/* Badges Superpuestos Superior Izquierda: Tienda Origen y Oferta */}
          <div className="absolute top-2.5 left-2.5 z-20 flex flex-col items-start gap-1 pointer-events-none max-w-[calc(100%-65px)]">
            {sellerStore && (
              <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-slate-900/90 text-white backdrop-blur-md shadow-md truncate max-w-full">
                Disponible en {sellerStore}
              </span>
            )}
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

          {/* Icono de Favorito */}
          <div className="absolute top-3 right-3 z-20 group/heart cursor-pointer active:scale-125 transition-transform duration-200" onClick={toggleFavorite}>
            <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm ${
              isFavorite 
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
        </div>

        {/* Zona Inferior: Información del producto (Limpia y Sobria con Alto Contraste) */}
        <div className="p-5 flex flex-col flex-grow bg-white border-t border-slate-100">
          <p className="text-[11px] font-black uppercase tracking-widest text-slate-900 mb-1 transition-none truncate">
            {product.brand?.name || "Sin marca"}
          </p>

          <h3 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug flex-grow">
            {formattedName}
          </h3>

          <div className="flex items-center justify-between mt-auto pt-4 gap-2">
            <div className="flex items-center flex-wrap gap-1.5">
              <span className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {currentPrice?.toFixed(2)} €
              </span>
              {hasOffer && (
                <span className="text-sm font-semibold text-slate-400 line-through ml-1">
                  {previousPrice?.toFixed(2)} €
                </span>
              )}
              {typeof product.price_per_kg === 'number' && product.price_per_kg > 0 && (
                <span className="inline-flex items-center bg-slate-100 border border-slate-200/60 text-slate-600 text-xs font-semibold px-2.5 py-1 rounded-md ml-2 my-auto">
                  {product.price_per_kg.toFixed(2)} € / kg
                </span>
              )}
            </div>

            <a
              href={product.affiliate_url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm cursor-pointer whitespace-nowrap"
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
               <div className="flex justify-between items-center mb-2 pr-10">
                 <p className="text-[11px] font-black uppercase tracking-widest text-slate-900 transition-none">
                   {product.brand?.name || "Sin marca"}
                 </p>
                 
                 <div className="group/heart cursor-pointer active:scale-125 transition-transform duration-200" onClick={toggleFavorite}>
                   <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm ${
                     isFavorite 
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
               </div>

               <h2 className="text-xl sm:text-2xl font-black text-slate-900 mb-2 leading-snug">{formattedName}</h2>
               <div className="flex items-center flex-wrap gap-3 mb-4">
                 <span className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
                   {currentPrice?.toFixed(2)} €
                 </span>
                 {hasOffer && (
                   <span className="text-base font-semibold text-slate-400 line-through">
                     {previousPrice?.toFixed(2)} €
                   </span>
                 )}
                 {typeof product.price_per_kg === 'number' && product.price_per_kg > 0 && (
                   <span className="inline-flex items-center bg-slate-100 border border-slate-200/60 text-slate-600 text-xs font-medium px-2.5 py-1 rounded-md my-auto">
                     {product.price_per_kg.toFixed(2)} € / kg
                   </span>
                 )}
               </div>
               
               {/* Zona Central con Scroll Interno Exclusivo */}
               <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar my-2">
                 <div className={`text-slate-600 text-sm leading-relaxed mb-2 ${!isExpanded ? 'line-clamp-3' : ''}`}>
                   {product.description}
                 </div>
                 {product.description && product.description.length > 120 && (
                   <button onClick={() => setIsExpanded(!isExpanded)} className="text-blue-600 text-xs font-bold mb-4 hover:text-blue-700 self-start cursor-pointer">
                     {isExpanded ? 'Leer menos' : 'Leer más...'}
                   </button>
                 )}
                 
                 <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-100 text-sm w-full">
                   <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Categoría</span><span className="text-slate-700 font-medium">{product.category?.name || '-'}</span></div>
                   {sellerStore && (
                     <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tienda</span><span className="text-slate-700 font-medium">{sellerStore}</span></div>
                   )}
                   <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Formato</span><span className="text-slate-700 font-medium">{product.format || '-'}</span></div>

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
               
               {/* Zona Inferior Fija / Anclada */}
               <div className="pt-4 border-t border-slate-100 mt-auto">
                 <a 
                   href={product.affiliate_url || "#"} 
                   target="_blank" 
                   rel="noopener noreferrer" 
                   className="w-full flex justify-center py-3.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold transition-colors shadow-lg active:scale-95 cursor-pointer"
                 >
                   Ver oferta en la tienda oficial
                 </a>
               </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
