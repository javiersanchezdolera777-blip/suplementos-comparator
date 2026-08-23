"use client";

import Link from 'next/link';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import SearchOmnibox from './SearchOmnibox';

export default function Navbar() {
  const { isLoggedIn, openLoginModal, logout, favoriteIds } = useAuth();
  const searchParams = useSearchParams();
  const isSoloOfertas = searchParams ? searchParams.get('solo_ofertas') === 'true' : false;

  return (
    <nav className="w-full py-3 px-4 md:px-8 lg:px-12 flex items-center justify-between z-40 border-b border-slate-100 bg-white sticky top-0 transition-all duration-300 gap-4">

      {/* Logo Identidad Oficial Tus Suplementos */}
      <Link href="/" className="flex items-center gap-2.5 group cursor-pointer focus:outline-none select-none flex-shrink-0">
        <Image
          src="/Logo_icon2.png"
          alt="Tus Suplementos"
          width={44}
          height={44}
          style={{ width: 'auto', height: 'auto' }}
          className="w-10 h-10 sm:w-11 sm:h-11 object-contain group-hover:scale-105 transition-transform duration-200"
          priority
        />
        <div className="hidden sm:flex items-baseline text-lg sm:text-xl md:text-2xl tracking-tight">
          <span className="font-semibold text-slate-700">Tus</span>
          <span className="font-black text-slate-900 ml-1">Suplementos</span>
          <span className="text-blue-600 font-extrabold text-2xl leading-none ml-0.5">.</span>
        </div>
      </Link>

      {/* Buscador Global Omnibox Live (Centro) */}
      <div className="flex-1 max-w-sm md:max-w-md lg:max-w-lg mx-2 sm:mx-4">
        <SearchOmnibox />
      </div>

      {/* Menú Principal */}
      <div className="flex items-center gap-4 lg:gap-8 text-sm font-medium text-slate-600 flex-shrink-0">
        <div className="hidden md:flex items-center gap-6">
          <Link href="/#catalogo" className="hover:text-slate-900 transition-colors">
            Catálogo
          </Link>

          {/* Botón Top Ofertas */}
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

          <div className="w-px h-4 bg-slate-200"></div>
        </div>

        {/* --- NUEVA ZONA: PUENTES A LA COMUNIDAD --- */}
        <div className="hidden sm:flex items-center gap-3">
          <Link href="/comunidad" className="text-slate-600 hover:text-blue-600 font-bold text-sm transition-colors flex items-center gap-1">
            🔍 Comunidad
          </Link>
          <Link href="/mi-zona" className="bg-blue-600 text-white hover:bg-blue-700 font-bold text-xs px-3.5 py-1.5 rounded-lg shadow-sm transition-transform transform hover:-translate-y-0.5 flex items-center gap-1.5">
            🎮 Mi Zona
          </Link>
          <div className="w-px h-4 bg-slate-200 ml-1 hidden md:block"></div>
        </div>
        {/* ------------------------------------------- */}

        {/* Autenticación & Favoritos */}
        {isLoggedIn ? (
          <div className="flex items-center gap-3">
            {/* Botón Favoritos */}
            <Link className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs transition-all group" href="/favoritos">
              <svg className="w-4 h-4 text-slate-600 group-hover:text-rose-500 group-hover:fill-rose-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span className="text-slate-800 group-hover:font-bold transition-all">
                Favoritos
              </span>
              {favoriteIds && favoriteIds.length > 0 && (
                <span className="bg-slate-900 text-white text-[10px] px-1.5 py-0.2 rounded-md font-bold min-w-[18px] text-center">
                  {favoriteIds.length}
                </span>
              )}
            </Link>

            {/* Botón Salir */}
            <button
              onClick={logout}
              className="flex items-center gap-1.5 bg-slate-100/80 hover:bg-slate-200/80 text-slate-700 font-medium text-xs px-3.5 py-1.5 rounded-lg border border-slate-200/60 transition-colors cursor-pointer"
            >
              <span className="font-bold">Salir</span>
            </button>
          </div>
        ) : (
          <div className="relative group">
            {/* Botón Acceder */}
            <button
              onClick={openLoginModal}
              className="flex items-center gap-1.5 bg-slate-100/80 hover:bg-slate-200/80 text-slate-700 font-medium text-xs px-3.5 py-1.5 rounded-lg border border-slate-200/60 transition-colors cursor-pointer"
            >
              <svg className="w-4 h-4 text-slate-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z" />
              </svg>
              <span className="font-bold">Acceder</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}