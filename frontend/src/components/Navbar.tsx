"use client";

import Link from 'next/link';
import Image from 'next/image';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import { useCompareStore } from '@/store/useCompareStore';
import SearchOmnibox from './SearchOmnibox';

export default function Navbar() {
  const { isLoggedIn, openLoginModal, logout, favoriteIds } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { compareIds } = useCompareStore();
  const isSoloOfertas = searchParams ? searchParams.get('solo_ofertas') === 'true' : false;

  const handleVersusClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!isLoggedIn) openLoginModal();
    else router.push('/versus');
  };

  const handleFavClick = (e: React.MouseEvent) => {
    if (!isLoggedIn) {
      e.preventDefault();
      openLoginModal();
    }
  };

  // Botón Social Inteligente (Escritorio y Móvil)
  const handleSocialClick = (e: React.MouseEvent) => {
    e.preventDefault();
    router.push('/mi-zona');
  };

  return (
    <>
      {/* =========================================
          CABECERA SUPERIOR (TOP BAR)
      ========================================= */}
      <nav className="w-full bg-white sticky top-0 z-40 border-b border-slate-200 shadow-sm transition-all duration-300">
        <div className="flex flex-col md:flex-row md:items-center justify-between px-4 md:px-8 lg:px-12 py-3 pb-2 md:pb-3 gap-2 md:gap-4">
          
          {/* 1. ZONA IZQUIERDA: LOGO */}
          <div className="order-1 flex items-center justify-between w-full md:w-auto">
            <Link href="/" className="flex items-center gap-2.5 group cursor-pointer focus:outline-none select-none flex-shrink-0">
              <Image src="/Logo_icon2.png" alt="Tus Suplementos" width={44} height={44} style={{ width: 'auto', height: 'auto' }} className="w-10 h-10 sm:w-11 sm:h-11 object-contain group-hover:scale-105 transition-transform duration-200" priority />
              <div className="flex items-baseline text-lg sm:text-xl md:text-2xl tracking-tight">
                <span className="font-semibold text-slate-700">Tus</span>
                <span className="font-black text-slate-900 ml-1">Suplementos</span>
                <span className="text-blue-600 font-extrabold text-2xl leading-none ml-0.5">.</span>
              </div>
            </Link>

            {/* Auth en Móvil (Fila 1 alineada con el Logo) */}
            <div className="md:hidden flex items-center">
              {isLoggedIn ? (
                <button onClick={logout} className="group relative flex items-center justify-center w-9 h-9 rounded-lg bg-slate-50 text-slate-600 transition-all cursor-pointer">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                </button>
              ) : (
                <button onClick={openLoginModal} className="flex items-center px-3 py-1.5 bg-slate-900 text-white rounded-lg font-bold text-xs transition-all shadow-sm">
                  Acceder
                </button>
              )}
            </div>
          </div>

          {/* 2. ZONA CENTRAL: BUSCADOR */}
          <div className="order-3 md:order-2 w-full md:flex-1 md:max-w-md lg:max-w-xl">
            <SearchOmnibox />
          </div>

          {/* 3. ZONA DERECHA: ENLACES Y BOTONES */}
          <div className="hidden md:flex order-2 md:order-3 items-center justify-end gap-3 lg:gap-5 flex-shrink-0">
            
            {/* Enlaces Limpios */}
            <div className="hidden lg:flex items-center gap-1.5">
              <Link href="/#catalogo" className="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-50 text-sm font-medium transition-all">
                Catálogo
              </Link>
              <Link href="/?solo_ofertas=true#catalogo" className={isSoloOfertas ? "bg-slate-900 text-white px-3 py-1.5 rounded-lg font-bold text-sm flex items-center gap-1.5 transition-all shadow-sm" : "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-medium text-sm transition-all"}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
                <span>Ofertas</span>
              </Link>
              
              {/* Botón Social Inteligente */}
              <button onClick={handleSocialClick} className="group/social relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-medium text-sm transition-all cursor-pointer">
                <span>Social</span>
                <span className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.6)]"></span>
                <div className="absolute top-10 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-bold px-2.5 py-1 rounded-md opacity-0 group-hover/social:opacity-100 transition-opacity pointer-events-none shadow-lg z-50">
                  New
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
                </div>
              </button>
            </div>

            <div className="hidden lg:block w-px h-6 bg-slate-200 mx-1"></div>

            {/* Iconos Funcionales */}
            <div className="hidden md:flex items-center gap-2 relative">
              <button onClick={handleVersusClick} className="group relative flex items-center justify-center w-9 h-9 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 transition-all cursor-pointer">
                <span className="font-black text-[11px] tracking-tighter">VS</span>
                {compareIds && compareIds.length > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 bg-blue-600 text-white text-[9px] px-1.5 py-0.5 rounded-md font-bold shadow-sm">{compareIds.length}</span>
                )}
                <div className="absolute top-12 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-bold px-2.5 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-lg z-50">
                  Comparador
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
                </div>
              </button>

              <Link href="/favoritos" onClick={handleFavClick} className="group relative flex items-center justify-center w-9 h-9 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-rose-500 transition-all">
                <svg className="w-4 h-4 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                {favoriteIds && favoriteIds.length > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 bg-slate-900 text-white text-[9px] px-1.5 py-0.5 rounded-md font-bold shadow-sm">{favoriteIds.length}</span>
                )}
                <div className="absolute top-12 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-bold px-2.5 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-lg z-50">
                  Mis Favoritos
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
                </div>
              </Link>

              {/* Botón Acceder / Salir Directo */}
              {isLoggedIn ? (
                <button onClick={logout} className="group relative flex items-center justify-center w-9 h-9 ml-1.5 rounded-lg bg-slate-50 hover:bg-rose-50 text-slate-600 hover:text-rose-600 transition-all cursor-pointer">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                  <div className="absolute top-12 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-bold px-2.5 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-lg z-50">
                    Salir
                    <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
                  </div>
                </button>
              ) : (
                <button onClick={openLoginModal} className="ml-1.5 flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold text-sm transition-all shadow-sm">
                  Acceder
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* =========================================
          BARRA INFERIOR (BOTTOM NAV) - SOLO MÓVIL
      ========================================= */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-white/95 backdrop-blur-md border-t border-slate-200 z-50 pb-[env(safe-area-inset-bottom)] shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.1)]">
        <div className="flex items-center justify-around h-16 px-2">
          
          <Link href="/" className="flex flex-col items-center justify-center w-16 h-full gap-1 text-slate-500 hover:text-blue-600 active:scale-95 transition-transform">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
            <span className="text-[10px] font-bold tracking-tight">Inicio</span>
          </Link>

          <button onClick={handleVersusClick} className="relative flex flex-col items-center justify-center w-16 h-full gap-1 text-slate-500 hover:text-blue-600 active:scale-95 transition-transform">
            <span className="font-black text-sm leading-5">VS</span>
            <span className="text-[10px] font-bold tracking-tight">Versus</span>
            {compareIds && compareIds.length > 0 && (
              <span className="absolute top-1 right-2 bg-blue-600 text-white text-[8px] px-1 rounded-full font-bold">{compareIds.length}</span>
            )}
          </button>

          <Link href="/favoritos" onClick={handleFavClick} className="relative flex flex-col items-center justify-center w-16 h-full gap-1 text-slate-500 hover:text-rose-500 active:scale-95 transition-transform">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
            <span className="text-[10px] font-bold tracking-tight">Favoritos</span>
            {favoriteIds && favoriteIds.length > 0 && (
              <span className="absolute top-1 right-2 bg-slate-900 text-white text-[8px] px-1 rounded-full font-bold">{favoriteIds.length}</span>
            )}
          </Link>

          <button onClick={handleSocialClick} className="flex flex-col items-center justify-center w-16 h-full gap-1 text-slate-500 hover:text-blue-600 active:scale-95 transition-transform">
            <div className="relative">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span className="absolute -top-0.5 -right-1 w-1.5 h-1.5 rounded-full bg-red-500"></span>
            </div>
            <span className="text-[10px] font-bold tracking-tight">Social</span>
          </button>

        </div>
      </nav>
    </>
  );
}