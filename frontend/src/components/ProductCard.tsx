"use client";

import Image from 'next/image';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  image_url: string;
  affiliate_url: string;
  brand: {
    name: string;
  };
  category: {
    name: string;
  };
  format?: string;
  is_vegan?: boolean;
  quality_seal?: string;
  protein_type?: string;
  creatine_type?: string;
  amino_profile?: string;
  vitamin_type?: string;
  // El backend ahora puede enviar múltiples sabores por producto
  flavor?: string[] | string | null;
}

export default function ProductCard({ product }: { product: Product }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const { isLoggedIn, openLoginModal, token, favoriteIds, addFavoriteId, removeFavoriteId } = useAuth();
  
  const isFavorite = favoriteIds.includes(product.id);
  
  const hasImage = product.image_url && product.image_url.trim() !== "";
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const toggleFavorite = async (e: React.MouseEvent) => {
    e.stopPropagation(); 
    
    if (!isLoggedIn) {
      openLoginModal();
      return;
    }

    try {
      if (isFavorite) {
        const res = await fetch(`${apiUrl}/api/favoritos/${product.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) removeFavoriteId(product.id);
      } else {
        const res = await fetch(`${apiUrl}/api/favoritos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ producto_id: product.id })
        });
        if (res.ok) addFavoriteId(product.id);
      }
    } catch (error) {
      console.error("Error al actualizar favorito", error);
    }
  };

  return (
    <>
      <div className="group relative flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-slate-300 transition-all duration-200 shadow-sm hover:shadow-lg hover:-translate-y-1">
        
        {/* Zona Superior: Imagen y Badges */}
        <div 
          className="relative aspect-square p-6 sm:p-8 flex items-center justify-center bg-slate-50 overflow-hidden cursor-pointer"
          onClick={() => setIsModalOpen(true)}
        >
          {hasImage ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500 ease-out relative z-10"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-slate-100 rounded-xl border border-slate-200 relative z-10">
               <span className="text-slate-400 font-bold tracking-[0.2em] text-xs uppercase">Suparator</span>
            </div>
          )}

          {/* Badge de Categoría */}
          <div className="absolute top-4 left-4 z-20">
            <span className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest bg-white/90 text-slate-700 border border-slate-200 shadow-sm rounded-full backdrop-blur-md">
              {product.category?.name || "Sin categoría"}
            </span>
          </div>

          {/* Icono de Favorito */}
          <div className="absolute top-4 right-4 z-20 group/heart cursor-pointer" onClick={toggleFavorite}>
            <div className={`p-2 rounded-full border transition-colors shadow-sm ${
              isFavorite 
                ? "bg-red-50 border-red-200" 
                : "bg-white/90 border-slate-200 group-hover/heart:bg-slate-100 group-hover/heart:border-slate-300"
            }`} title="Guarda tus suplementos favoritos">
              <svg 
                className={`w-4 h-4 transition-colors ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-slate-600"}`} 
                fill={isFavorite ? "currentColor" : "none"}
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Zona Inferior: Información del producto */}
        <div className="p-5 sm:p-6 flex flex-col flex-grow bg-white border-t border-slate-100">
          <div className="text-[10px] font-bold tracking-widest text-slate-400 mb-1.5 uppercase">{product.brand?.name || "Sin marca"}</div>
          <h3 
            className="text-base font-bold text-slate-900 mb-2 leading-snug group-hover:text-blue-600 transition-colors duration-300 cursor-pointer"
            onClick={() => setIsModalOpen(true)}
          >
            {product.name}
          </h3>
          <p className="text-sm text-slate-500 line-clamp-2 mb-6 flex-grow font-medium leading-relaxed">
            {product.description}
          </p>
          
          <div className="flex items-center justify-between mt-auto gap-4">
            <div className="flex flex-col">
              <span className="text-xs text-slate-400 font-medium mb-0.5">Mejor precio</span>
              
              <div className="flex items-baseline gap-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Desde</span>
                <span className="text-2xl font-black text-blue-600 tracking-tight">
                  {product.price?.toFixed(2)}€
                </span>
              </div>
            </div>
            <a
              href={product.affiliate_url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold transition-all duration-200 active:scale-95 shadow-md shadow-blue-600/20 whitespace-nowrap"
            >
              Ver oferta
            </a>
          </div>
        </div>
      </div>

      {/* Modal Quick View Overlay Light Mode */}
      {isModalOpen && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-slate-900/40 backdrop-blur-sm transition-opacity"
          onClick={() => setIsModalOpen(false)} 
        >
          <div 
            className="bg-white rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-y-auto relative shadow-2xl flex flex-col md:flex-row animate-in zoom-in-95 duration-300"
            onClick={(e) => e.stopPropagation()} 
          >
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 z-50 p-2 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors text-slate-500">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="w-full md:w-1/2 bg-slate-50 p-8 flex items-center justify-center min-h-[300px] border-r border-slate-100">
                {hasImage ? (
                  <img src={product.image_url} alt={product.name} className="w-full h-auto max-h-[400px] object-contain drop-shadow-md" />
                ) : (
                  <span className="text-slate-300 font-black tracking-[0.3em] text-xl uppercase">Suparator</span>
                )}
            </div>

            <div className="w-full md:w-1/2 p-6 md:p-8 flex flex-col">
               <div className="flex justify-between items-start mb-2">
                 <div className="text-xs font-bold tracking-widest text-slate-400 uppercase">{product.brand?.name}</div>
                 
                 <div className="group/heart cursor-pointer" onClick={toggleFavorite}>
                   <div className={`p-2 rounded-full border transition-colors shadow-sm ${
                     isFavorite 
                       ? "bg-red-50 border-red-200" 
                       : "bg-white border-slate-200 group-hover/heart:bg-slate-50"
                   }`} title="Guardar favorito">
                     <svg 
                       className={`w-5 h-5 transition-colors ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-slate-600"}`} 
                       fill={isFavorite ? "currentColor" : "none"}
                       stroke="currentColor" 
                       viewBox="0 0 24 24"
                     >
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                     </svg>
                   </div>
                 </div>
               </div>

               <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mb-4 leading-snug">{product.name}</h2>
                           <div className="text-3xl font-black text-blue-600 mb-6">
                 <span className="text-slate-400 text-lg font-bold mr-2">Desde</span>
                 {product.price?.toFixed(2)}€
               </div>
               
               <div className={`text-slate-600 text-sm leading-relaxed mb-2 ${!isExpanded ? 'line-clamp-3' : ''}`}>
                 {product.description}
               </div>
               {product.description && product.description.length > 120 && (
                 <button onClick={() => setIsExpanded(!isExpanded)} className="text-blue-600 text-xs font-bold mb-6 hover:text-blue-700 self-start">
                   {isExpanded ? 'Leer menos' : 'Leer más...'}
                 </button>
               )}
               
               <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8 bg-slate-50 p-5 rounded-2xl border border-slate-100 text-sm w-full">
                 <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Categoría</span><span className="text-slate-700 font-medium">{product.category?.name || '-'}</span></div>
                 <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Formato</span><span className="text-slate-700 font-medium">{product.format || '-'}</span></div>

                 {/* Sabores: soporta nuevo array o string legacy */}
                 <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Sabores</span><span className="text-slate-700 font-medium">{Array.isArray(product.flavor) ? (product.flavor.length ? product.flavor.join(', ') : '-') : (product.flavor ? String(product.flavor) : '-')}</span></div>

                 {product.is_vegan && <div className="flex flex-col"><span className="text-[10px] text-emerald-600 uppercase font-bold tracking-wider">Dietético</span><span className="text-emerald-700 font-medium">100% Vegano</span></div>}
                 {product.protein_type && <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Proteína</span><span className="text-slate-700 font-medium">{product.protein_type}</span></div>}
                 {product.quality_seal && <div className="flex flex-col"><span className="text-[10px] text-blue-500 uppercase font-bold tracking-wider">Sello Calidad</span><span className="text-blue-600 font-medium">{product.quality_seal}</span></div>}
               </div>
               
               <div className="mt-auto pt-6 border-t border-slate-100">
                 <a 
                   href={product.affiliate_url || "#"} 
                   target="_blank" 
                   rel="noopener noreferrer" 
                   className="w-full flex justify-center py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-colors shadow-lg shadow-blue-600/20 active:scale-95"
                 >
                   Ver oferta en la tienda oficial
                 </a>
               </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
