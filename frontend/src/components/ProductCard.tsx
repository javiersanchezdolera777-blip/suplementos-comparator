"use client";

import Image from 'next/image';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../context/AuthContext';
import ModalAñadirStack from './ModalAñadirStack';
// Usamos la ruta correcta para la tienda de Javi
import { useCompareStore } from '@/store/useCompareStore';

// Definimos qué es una Oferta para que TypeScript deje de quejarse
interface Oferta {
  id?: number;
  precio?: number;
  tienda?: string;
  [key: string]: any;
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
  cleaned = cleaned.replace(/^¿por qué [^?]+\?\s*/i, '');
  cleaned = cleaned.replace(/\.([a-zA-ZáéíóúñÁÉÍÓÚÑ])/g, '. $1');
  cleaned = cleaned.replace(/\.\s+([a-zñáéíóú])/g, (_, letter) => `. ${letter.toUpperCase()}`);
  cleaned = cleaned.replace(/^([^a-zA-ZáéíóúñÁÉÍÓÚÑ]*)([a-zñáéíóú])/, (_, prefix, letter) => prefix + letter.toUpperCase());
  return cleaned;
};

const formatTitle = (nombre: string, marca?: string) => {
  if (!marca || !nombre) return nombre;
  const escapedMarca = marca.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`^${escapedMarca}\\s+`, 'i');
  return nombre.replace(regex, '');
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

export default function ProductCard({ product }: { product: Product }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  const [isStackModalOpen, setIsStackModalOpen] = useState(false);

  const trackClick = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${apiUrl}/api/click/${product.id}`, { method: 'POST' }).catch(() => { });
  };

  useEffect(() => {
    setMounted(true);
  }, []);

  const { isLoggedIn, openLoginModal, token, favoriteIds, addFavoriteId, removeFavoriteId } = useAuth();

  // 👇 AQUÍ ESTABA EL ERROR: Hemos descomentado las variables de Javi
  const { addId, removeId, compareIds } = useCompareStore();
  const isCompared = compareIds.includes(product.id);

  const [imageError, setImageError] = useState(false);
  const isFavorite = favoriteIds.includes(product.id);
  const showImage = product.image_url && product.image_url.trim() !== "" && !imageError;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const rawStore =
    (typeof product.tienda === 'object' && product.tienda?.name) ||
    (typeof product.tienda === 'string' && product.tienda) ||
    (typeof product.tienda_nombre === 'string' && product.tienda_nombre) ||
    (typeof product.store === 'object' && product.store?.name) ||
    (typeof product.store === 'string' && product.store) ||
    "";

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

  const urlStore = getStoreFromUrl(product.affiliate_url);
  const rawDbStore = rawStore;
  const cleanDbStore = rawDbStore && !['tradedoubler', 'awin', 'cj'].some(net => rawDbStore.toLowerCase().includes(net)) ? rawDbStore : null;
  const sellerStore = urlStore || cleanDbStore;
  const brandName = product.brand?.name || "";

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

  const formattedName = formatTitle(decodeHTML(product.name), product.brand?.name);

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
        const res = await fetch(`${apiUrl}/api/favoritos/${product.id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) addFavoriteId(product.id);
      } else {
        addFavoriteId(product.id);
        setToastMsg("Guardado en tus favoritos");
        setTimeout(() => setToastMsg(null), 2000);
        const res = await fetch(`${apiUrl}/api/favoritos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
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
    if (isCompared) {
      removeId(product.id);
      setToastMsg("Quitado de la comparativa");
    } else {
      addId(product.id);
      setToastMsg("Añadido a la comparativa");
    }
    setTimeout(() => setToastMsg(null), 2000);
  };

  const handleOpenStackModal = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isLoggedIn) {
      openLoginModal();
      return;
    }
    setIsStackModalOpen(true);
  };

  return (
    <>
      <div
        className="group relative flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-slate-300 transition-all duration-200 shadow-sm hover:shadow-lg hover:-translate-y-1 cursor-pointer"
        onClick={handleOpenProduct}
      >
        <div className="relative aspect-square p-6 sm:p-8 flex items-center justify-center bg-slate-50 overflow-hidden">
          {showImage ? (
            <img
              src={product.image_url}
              alt={formattedName}
              onError={() => setImageError(true)}
              className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500 ease-out relative z-10"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-slate-100 rounded-2xl border border-slate-200/80 p-2 md:p-4 text-center relative z-10">
              <span className="text-slate-400 font-extrabold tracking-[0.2em] text-[8px] md:text-xs uppercase mb-1">Tus Suplementos</span>
              <span className="text-slate-400 text-[9px] md:text-[10px] font-semibold">{product.brand?.name || "Oficial"}</span>
            </div>
          )}

          <div className="absolute top-2.5 left-2.5 z-20 flex flex-col items-start gap-1 pointer-events-none max-w-[calc(100%-65px)]">
            {hasOffer && (
              <span className="bg-red-600 text-white font-extrabold text-[11px] px-2 py-0.5 rounded-md shadow-sm">-{discountPercentage}%</span>
            )}
          </div>

          <div className="absolute bottom-3 left-3 z-20 pointer-events-none">
            <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-white/90 text-slate-700 border border-slate-200/80 shadow-sm rounded-md backdrop-blur-md">
              {product.category?.name || "Sin categoría"}
            </span>
          </div>

          <div className="absolute top-3 right-3 z-20 flex flex-col gap-2">

            <div className="group/heart cursor-pointer active:scale-125 transition-transform duration-200" onClick={toggleFavorite}>
              <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm w-[34px] h-[34px] flex items-center justify-center ${isFavorite
                  ? "bg-red-50 border-red-200 scale-105"
                  : "bg-white/90 border-slate-200 group-hover/heart:bg-slate-100 group-hover/heart:border-slate-300"
                }`} title={isFavorite ? "Quitar de favoritos" : "Guardar en favoritos"}>
                <svg className={`w-4 h-4 transition-colors duration-200 ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-slate-600"}`} fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
            </div>

            <div className="group/vs cursor-pointer active:scale-125 transition-transform duration-200" onClick={handleCompare}>
              <div className={`p-2 rounded-full border transition-all duration-200 shadow-sm w-[34px] h-[34px] flex items-center justify-center ${isCompared
                  ? "bg-blue-50 border-blue-200 scale-105"
                  : "bg-white/90 border-slate-200 group-hover/vs:bg-slate-100 group-hover/vs:border-slate-300"
                }`} title={isCompared ? "Ya en la comparativa" : "Añadir a comparativa"}>
                <span className={`text-[10px] font-black tracking-tighter ${isCompared ? "text-blue-600" : "text-slate-400 group-hover/vs:text-slate-600"}`}>VS</span>
              </div>
            </div>

            <div className="group/stack cursor-pointer active:scale-125 transition-transform duration-200" onClick={handleOpenStackModal}>
              <div className="p-2 rounded-full border transition-all duration-200 shadow-sm w-[34px] h-[34px] flex items-center justify-center bg-white/90 border-slate-200 group-hover/stack:bg-slate-100 group-hover/stack:border-slate-300" title="Añadir a mis Stacks">
                <svg className="w-4 h-4 text-slate-400 group-hover/stack:text-slate-600 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                </svg>
              </div>
            </div>

          </div>
        </div>

        <div className="p-5 flex flex-col flex-grow bg-white border-t border-slate-100">
          <div className="flex flex-col gap-0.5 mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 truncate">
              {brandName || "Sin marca"}
            </span>

            {sellerStore && !isSameBrandAndStore && (
              <span className="text-[12px] font-normal text-slate-500 truncate">
                Vendido por <span className="font-semibold text-slate-700">{sellerStore}</span>
              </span>
            )}
          </div>

          <h3 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug flex-grow">
            {formattedName}
          </h3>

          <div className="flex flex-col md:flex-row md:items-center md:justify-between mt-auto pt-3 md:pt-4 gap-2">
            <div className="flex items-center flex-wrap gap-1.5">
              <span className="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                {currentPrice?.toFixed(2)} €
              </span>
              {hasOffer && (
                <span className="text-xs md:text-sm font-semibold text-slate-400 line-through ml-1">
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
              onClick={(e) => {
                e.stopPropagation();
                trackClick();
              }}
              className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm cursor-pointer whitespace-nowrap text-center"
            >
              Ver oferta
            </a>
          </div>
        </div>
      </div>

      {mounted && isModalOpen && createPortal(
        <div
          className="fixed inset-0 z-[99999] w-screen h-screen bg-black/80 backdrop-blur-md flex items-center justify-center p-4 md:p-6 overflow-hidden"
          onClick={closeModal}
        >
          <div
            className="relative w-full max-w-4xl h-[85vh] max-h-[680px] bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row animate-in zoom-in-95 duration-300"
            onClick={(e) => e.stopPropagation()}
          >
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

            <div className="w-full md:w-1/2 h-48 md:h-full bg-slate-50 p-6 md:p-8 flex items-center justify-center relative overflow-hidden border-b md:border-b-0 md:border-r border-slate-100">
              {showImage ? (
                <img src={product.image_url} alt={formattedName} onError={() => setImageError(true)} className="w-full h-full object-contain max-h-full max-w-full drop-shadow-md" />
              ) : (
                <div className="flex flex-col items-center justify-center text-center p-4">
                  <span className="text-slate-400 font-black tracking-[0.2em] text-base uppercase mb-1">Tus Suplementos</span>
                  <span className="text-slate-400 text-xs font-semibold">{product.brand?.name || "Oficial"}</span>
                </div>
              )}
            </div>

            <div className="w-full md:w-1/2 flex flex-col h-full bg-white p-6 md:p-8 relative overflow-hidden">
              <div className="flex justify-between items-start mb-2 pr-10">
                <div className="flex flex-col gap-0.5 mb-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
                    {brandName || "Sin marca"}
                  </span>
                  {sellerStore && !isSameBrandAndStore && (
                    <span className="text-[12px] font-normal text-slate-500">
                      Vendido por <span className="font-semibold text-slate-700">{sellerStore}</span>
                    </span>
                  )}
                </div>

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

              <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar my-2">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-100 text-sm w-full">
                  <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Categoría</span><span className="text-slate-700 font-medium">{product.category?.name || '-'}</span></div>
                  {sellerStore && (
                    <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tienda</span><span className="text-slate-700 font-medium">{formatStoreName(sellerStore)}</span></div>
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

              {/* Zona Inferior: TABLA MULTI-TIENDA COMPACTA */}
              <div className="pt-4 border-t border-slate-100 mt-auto">
                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Ofertas Disponibles
                </h3>

                {product.ofertas && product.ofertas.filter((o) => o.activo).length > 0 ? (
                  <div className="flex flex-col gap-2 max-h-[150px] overflow-y-auto custom-scrollbar pr-1">
                    {product.ofertas
                      .filter((o) => o.activo)
                      .sort((a, b) => (a.precio ?? 0) - (b.precio ?? 0))
                      .map((oferta, index) => (
                        <div
                          key={oferta.id ?? index}
                          className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-white"
                        >
                          <div className="flex flex-col">
                            <span className="font-extrabold text-slate-900 text-sm">
                              {oferta.tienda}
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="font-black text-slate-900">
                              {oferta.precio?.toFixed(2)} €
                            </span>
                            <a
                              href={product.slug && oferta.tienda ? `${apiUrl}/api/out/${oferta.tienda.toLowerCase()}/${product.slug}` : (product.affiliate_url || "#")}
                              target="_blank"
                              rel="nofollow noopener noreferrer"
                              onClick={(e) => { e.stopPropagation(); trackClick(); }}
                              className="px-4 py-1.5 rounded-lg font-bold text-xs transition-all shadow-sm bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 hover:text-slate-900 hover:shadow-md cursor-pointer"
                            >
                              Ver
                            </a>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <a
                    href={product.affiliate_url || "#"}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={trackClick}
                    className="w-full flex justify-center py-3.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold transition-colors shadow-lg active:scale-95 cursor-pointer"
                  >
                    Ver oferta en la tienda oficial
                  </a>
                )}

                {/* Enlace a Ficha Técnica SEO */}
                {product.slug && (
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
                )}
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      <ModalAñadirStack
        isOpen={isStackModalOpen}
        onClose={() => setIsStackModalOpen(false)}
        productoId={product.id}
        productoNombre={decodeHTML(product.name)}
      />
    </>
  );
}