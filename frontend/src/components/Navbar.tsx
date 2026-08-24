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
    if (!isLoggedIn) {
      openLoginModal();
    } else {
      router.push('/versus');
    }
  };

  return (
    <nav className="w-full py-3 px-4 md:px-8 lg:px-12 flex flex-wrap md:flex-nowrap items-center justify-between z-40 border-b border-slate-100 bg-white sticky top-0 transition-all duration-300 gap-y-3 md:gap-4">
      
      {/* 1. LOGO (Siempre primero) */}
      <Link href="/" className="order-1 flex items-center gap-2.5 group cursor-pointer focus:outline-none select-none flex-shrink-0">
        <Image
          src="/Logo_icon2.png"
          alt="Tus Suplementos"
          width={44}
          height={44}
          style={{ width: 'auto', height: 'auto' }}
          className="w-10 h-10 sm:w-11 sm:h-11 object-contain group-hover:scale-105 transition-transform duration-200"
          priority
        />
        <div className="flex items-baseline text-lg sm:text-xl md:text-2xl tracking-tight">
          <span className="font-semibold text-slate-700">Tus</span>
          <span className="font-black text-slate-900 ml-1">Suplementos</span>
          <span className="text-blue-600 font-extrabold text-2xl leading-none ml-0.5">.</span>
        </div>
      </Link>

      {/* 2. BUSCADOR (Tercero en móvil, segundo en PC) */}
      <div className="order-3 md:order-2 w-full md:flex-1 md:max-w-md lg:max-w-lg md:mx-4">
        <SearchOmnibox />
      </div>

      {/* 3. BOTONES (Segundo en móvil, tercero en PC) */}
      <div className="order-2 md:order-3 flex items-center gap-2 md:gap-4 lg:gap-8 text-sm font-medium text-slate-600 flex-shrink-0">
        <div className="hidden md:flex items-center gap-6">
          <Link href="/#catalogo" className="hover:text-slate-900 transition-colors">
            Catálogo
          </Link>
          <Link
            href="/?solo_ofertas=true#catalogo"
            className={
              isSoloOfertas
                ? "bg-amber-50 text-amber-900 border border-amber-200 px-3 py-1.5 rounded-lg font-semibold text-sm flex items-center gap-1.5 transition-all shadow-2xs"
                : "flex items-center gap-1.5 text-slate-600 hover:text-slate-900 font-medium text-sm transition-colors"
            }
          >
            <svg className="w-4 h-4 text-amber-500 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 23c-4.97 0-9-3.58-9-8 0-4.19 3.01-7.12 6.09-10.09.43-.41 1.15-.12 1.15.47 0 1.95 1.13 3.12 2.26 4.29 1.13 1.17 2.26 2.34 2.26 4.75 0 .28.22.5.5.5s.5-.22.5-.5c0-1.42-.56-2.56-1.12-3.69-.56-1.13-1.13-2.27-1.13-4.31 0-.58.71-.87 1.14-.46C18.06 10.15 21 13.06 21 17c0 4.42-4.03 8-9 8z" />
            </svg>
            <span>Top Ofertas</span>
          </Link>
        </div>

        {/* Botón Modo Versus (Premium) */}
        <button
          onClick={handleVersusClick}
          className="flex items-center justify-center sm:gap-1.5 text-slate-600 hover:text-blue-600 font-medium transition-colors group cursor-pointer px-2 py-1 md:px-2 md:py-0 relative"
        >
          <span className="bg-blue-100 text-blue-700 text-[11px] md:text-xs font-black px-1.5 py-0.5 md:px-2 md:py-1 rounded border border-blue-200 uppercase tracking-tighter shadow-sm group-hover:scale-105 transition-transform">VS</span>
          <span className="hidden md:inline text-sm font-bold uppercase tracking-tight md:normal-case md:tracking-normal">Versus</span>
          {compareIds && compareIds.length > 0 && (
            <span className="absolute -top-1 right-0 md:relative md:top-auto md:right-auto bg-blue-600 text-white text-[9px] md:text-[10px] px-1 md:px-1.5 py-0 md:py-0.5 rounded-md font-bold min-w-[14px] md:min-w-[18px] text-center shadow-sm md:ml-0.5 animate-in zoom-in duration-200">
              {compareIds.length}
            </span>
          )}
        </button>

        <div className="hidden md:block w-px h-4 bg-slate-200"></div>

        {/* Autenticación & Favoritos */}
        {isLoggedIn ? (
          <div className="flex items-center gap-1 md:gap-3">
            <Link className="flex items-center justify-center sm:gap-1.5 px-2 py-1 md:px-3.5 md:py-1.5 rounded-lg md:bg-slate-100 md:hover:bg-slate-200 text-slate-800 transition-all group relative" href="/favoritos">
              <svg className="w-6 h-6 md:w-4 md:h-4 text-slate-600 group-hover:text-rose-500 group-hover:fill-rose-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span className="hidden md:inline text-xs font-bold uppercase tracking-tight md:normal-case md:tracking-normal text-slate-800 group-hover:font-bold transition-all">
                Favs
              </span>
              {favoriteIds && favoriteIds.length > 0 && (
                <span className="absolute -top-1 right-0 md:relative md:top-auto md:right-auto bg-slate-900 text-white text-[9px] md:text-[10px] px-1 md:px-1.5 py-0 md:py-0.2 rounded-md font-bold min-w-[14px] md:min-w-[18px] text-center shadow-sm">
                  {favoriteIds.length}
                </span>
              )}
            </Link>

            <button
              onClick={logout}
              className="flex items-center justify-center sm:gap-1.5 px-2 py-1 md:px-3.5 md:py-1.5 md:bg-slate-100/80 md:hover:bg-slate-200/80 text-slate-700 rounded-lg md:border md:border-slate-200/60 transition-colors cursor-pointer"
              title="Salir"
            >
              <svg className="w-6 h-6 md:w-4 md:h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
              <span className="hidden md:inline text-xs font-bold uppercase tracking-tight md:normal-case md:tracking-normal">Salir</span>
            </button>
          </div>
        ) : (
          <div className="relative group">
            <button
              onClick={openLoginModal}
              className="flex items-center justify-center sm:gap-1.5 px-2 py-1 md:px-3.5 md:py-1.5 md:bg-slate-100/80 md:hover:bg-slate-200/80 text-slate-700 rounded-lg md:border md:border-slate-200/60 transition-colors cursor-pointer"
            >
              <svg className="w-6 h-6 md:w-4 md:h-4 text-slate-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z" />
              </svg>
              <span className="hidden md:inline text-xs font-bold uppercase tracking-tight md:normal-case md:tracking-normal">Acceder</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}