"use client";

import Link from 'next/link';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isLoggedIn, openLoginModal, logout, favoriteIds } = useAuth();
  const searchParams = useSearchParams();
  const isSoloOfertas = searchParams ? searchParams.get('solo_ofertas') === 'true' : false;

  return (
    <nav className="w-full py-4 px-6 md:px-12 flex justify-between items-center z-40 border-b border-slate-200 bg-white/90 backdrop-blur-md sticky top-0 transition-all duration-300">

      {/* Logo Identidad Oficial Tus Suplementos */}
      <Link href="/" className="flex items-center gap-2.5 group cursor-pointer focus:outline-none select-none">
        <Image
          src="/Logo_icon2.png"
          alt="Tus Suplementos"
          width={44}
          height={44}
          className="w-11 h-11 object-contain group-hover:scale-105 transition-transform duration-200"
          priority
        />
        <div className="flex items-baseline text-xl sm:text-2xl tracking-tight">
          <span className="font-semibold text-slate-700">Tus</span>
          <span className="font-black text-slate-900 ml-1">Suplementos</span>
          <span className="text-blue-600 font-extrabold text-2xl leading-none ml-0.5">.</span>
        </div>
      </Link>

      {/* Menú Principal */}
      <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
        <Link href="/#catalogo" className="hover:text-slate-900 transition-colors">
          Catálogo
        </Link>
        <Link href="/#marcas" className="hover:text-slate-900 transition-colors">
          Marcas
        </Link>

        {/* Botón Top Ofertas */}
        <Link
          href="/?solo_ofertas=true#catalogo"
          className={`flex items-center gap-1.5 transition-all ${isSoloOfertas
              ? "bg-red-50 text-red-600 border border-red-200/80 px-3.5 py-1.5 rounded-full font-extrabold shadow-sm"
              : "hover:text-slate-900 font-semibold"
            }`}
        >
          <span className="animate-pulse">🔥</span>
          <span>Top Ofertas</span>
          {isSoloOfertas && (
            <span className="bg-red-600 text-white text-[9px] font-black uppercase px-1.5 py-0.2 rounded-full ml-0.5">
              ACTIVO
            </span>
          )}
        </Link>

        <div className="w-px h-4 bg-slate-200"></div>

        {/* Autenticación & Favoritos */}
        {isLoggedIn ? (
          <div className="flex items-center gap-4">
            <Link
              href="/favoritos"
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-rose-50/80 hover:bg-rose-100 border border-rose-200/60 text-rose-600 transition-all font-medium hover:scale-105 active:scale-95 shadow-sm cursor-pointer"
            >
              <svg className="w-4 h-4 text-rose-600" fill="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span className="font-bold hidden sm:inline">Favoritos</span>
              {favoriteIds && favoriteIds.length > 0 && (
                <span className="bg-rose-600 text-white text-[10px] px-1.5 py-0.5 rounded-full font-black min-w-[20px] text-center shadow-sm">
                  {favoriteIds.length}
                </span>
              )}
            </Link>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-5 py-2 rounded-full bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 transition-all hover:scale-105 active:scale-95 shadow-sm cursor-pointer"
            >
              <span className="font-bold">Salir</span>
            </button>
          </div>
        ) : (
          <div className="relative group">
            <button
              onClick={openLoginModal}
              className="flex items-center gap-2 px-5 py-2 rounded-full bg-slate-900 hover:bg-slate-800 text-white transition-all hover:scale-105 active:scale-95 shadow-md shadow-slate-900/10 cursor-pointer"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
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
