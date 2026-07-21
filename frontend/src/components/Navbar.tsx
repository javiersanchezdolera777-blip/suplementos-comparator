"use client";

import Link from 'next/link';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isLoggedIn, openLoginModal, logout } = useAuth();

  return (
    <nav className="w-full py-5 px-6 md:px-12 flex justify-between items-center z-50 border-b border-white/5 bg-[#030712]/70 backdrop-blur-xl sticky top-0 supports-[backdrop-filter]:bg-[#030712]/40">
      <div className="text-2xl font-black tracking-tighter flex items-center gap-2">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-blue-500 drop-shadow-[0_0_10px_rgba(59,130,246,0.8)] group-hover:scale-110 transition-transform">⚡</span>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Suparator</span>
        </Link>
      </div>
      <div className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-400">
        <Link href="/#catalogo" className="hover:text-white transition-colors">Catálogo</Link>
        <Link href="#" className="hover:text-white transition-colors">Proteínas</Link>
        <Link href="#" className="hover:text-white transition-colors">Creatinas</Link>
        <div className="w-px h-4 bg-white/10"></div>
        
        {isLoggedIn ? (
          <div className="flex items-center gap-4">
            <Link 
              href="/favoritos"
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-100 transition-all hover:scale-105 active:scale-95"
            >
              <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span className="font-bold hidden sm:inline">Favoritos</span>
            </Link>
            <button 
              onClick={logout}
              className="flex items-center gap-2 px-5 py-2 rounded-full bg-slate-800/50 hover:bg-slate-700/50 border border-white/10 text-white transition-all hover:scale-105 active:scale-95"
            >
              <span className="font-bold">Salir</span>
            </button>
          </div>
        ) : (
          <div className="relative group">
            <button 
              onClick={openLoginModal}
              className="flex items-center gap-2 px-5 py-2 rounded-full bg-blue-600/10 hover:bg-blue-600/20 border border-blue-500/30 text-blue-100 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-blue-900/20"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z" />
              </svg>
              <span className="font-bold">Acceder</span>
            </button>
            <div className="absolute top-full right-0 mt-4 w-60 p-4 bg-[#0a0f1d] border border-blue-500/20 rounded-2xl shadow-2xl shadow-black/80 opacity-0 translate-y-2 pointer-events-none group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 z-50 text-xs text-slate-300 text-center leading-relaxed backdrop-blur-xl">
              <span className="font-semibold text-white block mb-1.5 text-sm">Crea tu cuenta gratis</span>
              Guarda tus suplementos favoritos y sigue sus precios.
              <div className="absolute -top-2 right-10 w-4 h-4 bg-[#0a0f1d] border-t border-l border-blue-500/20 transform rotate-45"></div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
