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
}

export default function ProductCard({ product }: { product: Product }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false); // Mock de estado de favorito inicial
  const { isLoggedIn, openLoginModal, token } = useAuth();
  
  const hasImage = product.image_url && product.image_url.trim() !== "";
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const toggleFavorite = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Evita que se abra el modal del producto al clicar el corazón
    
    if (!isLoggedIn) {
      openLoginModal();
      return;
    }

    try {
      if (isFavorite) {
        // Petición DELETE a Diego
        const res = await fetch(`${apiUrl}/api/favoritos/${product.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setIsFavorite(false);
      } else {
        // Petición POST a Diego
        const res = await fetch(`${apiUrl}/api/favoritos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ producto_id: product.id })
        });
        if (res.ok) setIsFavorite(true);
      }
    } catch (error) {
      console.error("Error al actualizar favorito", error);
    }
  };

  return (
    <>
      <div className="group relative flex flex-col bg-[#0a0f1d]/80 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden hover:border-white/20 transition-all duration-500 hover:shadow-2xl hover:shadow-white/5 hover:-translate-y-1">
        
        {/* Zona Superior: Imagen y Badges */}
        <div 
          className="relative aspect-square p-8 flex items-center justify-center bg-gradient-to-br from-white/[0.04] to-transparent overflow-hidden cursor-pointer"
          onClick={() => setIsModalOpen(true)}
        >
          <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 blur-3xl transition-opacity duration-700" />

          {hasImage ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-48 h-48 sm:w-56 sm:h-56 object-contain drop-shadow-2xl group-hover:scale-105 transition-transform duration-700 ease-out relative z-10"
            />
          ) : (
            <div className="w-48 h-48 sm:w-56 sm:h-56 flex items-center justify-center bg-white/5 rounded-2xl border border-white/10 relative z-10">
               <span className="text-slate-500/50 font-black tracking-[0.3em] text-xs uppercase">Suparator</span>
            </div>
          )}

          {/* Badge de Categoría */}
          <div className="absolute top-4 left-4 z-20">
            <span className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-300 bg-black/40 border border-white/10 rounded-full backdrop-blur-md">
              {product.category?.name || "Sin categoría"}
            </span>
          </div>

          {/* Icono de Favorito con nueva lógica de Auth */}
          <div className="absolute top-4 right-4 z-20 group/heart cursor-pointer" onClick={toggleFavorite}>
            <div className={`p-2 rounded-full border backdrop-blur-md transition-colors ${
              isFavorite 
                ? "bg-red-500/20 border-red-500/50" 
                : "bg-black/40 border-white/10 group-hover/heart:bg-white/10 group-hover/heart:border-white/30"
            }`} title="Guarda tus suplementos favoritos">
              <svg 
                className={`w-4 h-4 transition-colors ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-white"}`} 
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
        <div className="p-6 sm:p-7 flex flex-col flex-grow bg-gradient-to-t from-[#030712] to-transparent">
          <div className="text-[10px] font-bold tracking-widest text-slate-500 mb-2 uppercase">{product.brand?.name || "Sin marca"}</div>
          <h3 
            className="text-lg font-bold text-slate-200 mb-3 leading-snug group-hover:text-white transition-colors duration-300 cursor-pointer"
            onClick={() => setIsModalOpen(true)}
          >
            {product.name}
          </h3>
          <p className="text-sm text-slate-400/80 line-clamp-2 mb-8 flex-grow font-medium leading-relaxed">
            {product.description}
          </p>
          
          <div className="flex items-center justify-between mt-auto gap-4">
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 font-medium mb-0.5">Mejor precio</span>
              
              <div className="flex items-baseline gap-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Desde</span>
                <span className="text-2xl font-black text-white tracking-tight">
                  {product.price?.toFixed(2)}€
                </span>
              </div>
            </div>
            <a
              href={product.affiliate_url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2.5 bg-white hover:bg-slate-200 text-black rounded-xl text-sm font-bold transition-all duration-300 active:scale-95 shadow-lg shadow-white/10 hover:shadow-white/20 whitespace-nowrap"
            >
              Ver oferta
            </a>
          </div>
        </div>
      </div>

      {/* Modal Quick View Overlay */}
      {isModalOpen && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-sm transition-opacity"
          onClick={() => setIsModalOpen(false)} 
        >
          <div 
            className="bg-[#0a0f1d] border border-white/10 rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-y-auto relative shadow-2xl flex flex-col md:flex-row animate-in zoom-in-95 duration-300"
            onClick={(e) => e.stopPropagation()} 
          >
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 z-50 p-2 bg-black/40 hover:bg-white/10 rounded-full transition-colors text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="w-full md:w-1/2 bg-white/5 p-8 flex items-center justify-center min-h-[300px]">
                {hasImage ? (
                  <img src={product.image_url} alt={product.name} className="w-full h-auto max-h-[400px] object-contain drop-shadow-2xl" />
                ) : (
                  <span className="text-slate-500/50 font-black tracking-[0.3em] text-xl uppercase">Suparator</span>
                )}
            </div>

            <div className="w-full md:w-1/2 p-6 md:p-8 flex flex-col">
               <div className="flex justify-between items-start mb-2">
                 <div className="text-xs font-bold tracking-widest text-slate-500 uppercase">{product.brand?.name}</div>
                 
                 {/* Icono Favorito dentro del Modal */}
                 <div className="group/heart cursor-pointer" onClick={toggleFavorite}>
                   <div className={`p-2 rounded-full border backdrop-blur-md transition-colors ${
                     isFavorite 
                       ? "bg-red-500/20 border-red-500/50" 
                       : "bg-white/5 border-white/10 group-hover/heart:bg-white/10"
                   }`} title="Guardar favorito">
                     <svg 
                       className={`w-5 h-5 transition-colors ${isFavorite ? "text-red-500 fill-red-500" : "text-slate-400 group-hover/heart:text-white"}`} 
                       fill={isFavorite ? "currentColor" : "none"}
                       stroke="currentColor" 
                       viewBox="0 0 24 24"
                     >
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                     </svg>
                   </div>
                 </div>
               </div>

               <h2 className="text-2xl sm:text-3xl font-black text-white mb-4 leading-snug">{product.name}</h2>
               
               <div className="text-3xl font-black text-white mb-6">
                 <span className="text-slate-500 text-lg font-bold mr-2">Desde</span>
                 {product.price?.toFixed(2)}€
               </div>
               
               <p className="text-slate-400 text-sm leading-relaxed mb-8">{product.description}</p>
               
               <div className="flex flex-wrap gap-2 mb-8">
                 {product.format && <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-slate-300">{product.format}</span>}
                 {product.is_vegan && <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-xs text-emerald-400 font-medium">Vegano</span>}
                 {product.quality_seal && <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs text-blue-400 font-medium">{product.quality_seal}</span>}
                 {product.protein_type && <span className="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-400 font-medium">{product.protein_type}</span>}
                 {product.creatine_type && <span className="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-400 font-medium">{product.creatine_type}</span>}
               </div>
               
               <div className="mt-auto pt-6 border-t border-white/10">
                 <a 
                   href={product.affiliate_url || "#"} 
                   target="_blank" 
                   rel="noopener noreferrer" 
                   className="w-full flex justify-center py-4 bg-white hover:bg-slate-200 text-black rounded-xl font-bold transition-colors shadow-lg shadow-white/10 hover:shadow-white/20 active:scale-95"
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
