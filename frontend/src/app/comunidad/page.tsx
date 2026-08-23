"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ComunidadHub() {
  const [busqueda, setBusqueda] = useState("");
  const router = useRouter();

  const buscarUsuario = (e: React.FormEvent) => {
    e.preventDefault();
    if (busqueda.trim()) {
      router.push(`/comunidad/${busqueda.trim()}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center pt-10 px-4 sm:pt-20">
      <div className="w-full max-w-2xl">
        
        {/* Navegación Superior */}
        <div className="flex justify-between items-center mb-16">
          <Link href="/" className="text-gray-500 hover:text-slate-900 font-bold transition-colors flex items-center gap-2">
            <span>⬅️</span> Volver al comparador
          </Link>
          <Link href="/mi-zona" className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-full font-bold shadow-md transition-transform hover:-translate-y-1">
            🎮 Mi Zona
          </Link>
        </div>

        {/* Buscador Central */}
        <div className="text-center">
          <h1 className="text-5xl font-black text-slate-900 mb-6 tracking-tight">Comunidad</h1>
          <p className="text-gray-500 mb-10 text-lg">Encuentra a tus amigos, cotillea sus rutinas y descubre nuevos suplementos.</p>

          <form onSubmit={buscarUsuario} className="relative shadow-2xl rounded-full">
            <span className="absolute inset-y-0 left-0 flex items-center pl-6 text-2xl">🔍</span>
            <input
              type="text"
              placeholder="Escribe un @username..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full text-lg py-5 pl-16 pr-32 rounded-full border border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none transition-all"
            />
            <button 
              type="submit" 
              className="absolute inset-y-2 right-2 bg-slate-900 text-white font-bold px-8 rounded-full hover:bg-slate-800 transition-colors"
            >
              Buscar
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}