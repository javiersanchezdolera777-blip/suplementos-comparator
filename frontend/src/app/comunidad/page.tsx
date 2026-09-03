"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
// IMPORTAMOS LA NUEVA BARRA DE NAVEGACIÓN
import NavbarSocial from '@/components/navBarSocial';

export default function ComunidadHub() {
  const [busqueda, setBusqueda] = useState("");
  const [sugerencias, setSugerencias] = useState<any[]>([]);
  const [buscando, setBuscando] = useState(false);
  const router = useRouter();

  // EFECTO MÁGICO: Se ejecuta cada vez que escribes una letra
  useEffect(() => {
    const buscarEnTiempoReal = async () => {
      if (busqueda.length < 2) {
        setSugerencias([]);
        return;
      }

      setBuscando(true);
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${API_URL}/api/comunidad/buscar?q=${busqueda}`);
        if (res.ok) {
          const data = await res.json();
          setSugerencias(data);
        }
      } catch (error) {
        console.error("Error al buscar");
      } finally {
        setBuscando(false);
      }
    };

    // Un pequeño "retraso" (debounce) para no saturar el servidor si escribes muy rápido
    const temporizador = setTimeout(() => {
      buscarEnTiempoReal();
    }, 300);

    return () => clearTimeout(temporizador);
  }, [busqueda]);

  const irAlPerfil = (username: string) => {
    router.push(`/comunidad/${username}`);
  };

  const enviarFormulario = (e: React.FormEvent) => {
    e.preventDefault();
    if (busqueda.trim()) {
      irAlPerfil(busqueda.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center pt-10 px-4 sm:pt-20 relative">
      <div className="w-full max-w-2xl relative z-10">

        {/* Buscador Central y Títulos */}
        <div className="text-center relative">

          {/* BARRA DE NAVEGACIÓN NUEVA INTEGRADA */}
          <NavbarSocial />

          <h1 className="text-5xl font-black text-slate-900 mb-6 tracking-tight mt-6">Comunidad</h1>
          <p className="text-gray-500 mb-10 text-lg">Encuentra a tus amigos, cotillea sus rutinas y descubre nuevos suplementos.</p>

          <div className="relative">
            <form onSubmit={enviarFormulario} className="relative shadow-2xl rounded-full bg-white z-20">
              <span className="absolute inset-y-0 left-0 flex items-center pl-6 text-2xl">🔍</span>
              <input
                type="text"
                placeholder="Escribe un @username..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="w-full text-lg py-5 pl-16 pr-32 rounded-full border border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none transition-all"
                autoComplete="off"
              />
              <button
                type="submit"
                className="absolute inset-y-2 right-2 bg-slate-900 text-white font-bold px-8 rounded-full hover:bg-slate-800 transition-colors"
              >
                Buscar
              </button>
            </form>

            {/* --- EL MENÚ DESPLEGABLE DE SUGERENCIAS --- */}
            {busqueda.length >= 2 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-30 animate-fade-in-up">
                {buscando ? (
                  <div className="p-4 text-gray-400 font-medium text-sm">Buscando en la comunidad...</div>
                ) : sugerencias.length > 0 ? (
                  <div className="flex flex-col">
                    {sugerencias.map((user) => (
                      <button
                        key={user.username}
                        onClick={() => irAlPerfil(user.username)}
                        className="flex items-center justify-between p-4 hover:bg-blue-50 transition-colors border-b border-gray-50 last:border-0 w-full text-left group"
                      >
                        <div className="flex items-center gap-3">
                          {/* AVATAR DINÁMICO EN EL BUSCADOR TAMBIÉN */}
                          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-cyan-400 text-white font-bold flex items-center justify-center shadow-sm overflow-hidden border border-slate-100">
                            {user.foto_perfil ? (
                              <img src={user.foto_perfil} alt={user.username} className="w-full h-full object-cover" />
                            ) : (
                              user.username.charAt(0).toUpperCase()
                            )}
                          </div>
                          <div>
                            <div className="font-bold text-slate-800 group-hover:text-blue-700">@{user.username}</div>
                            <div className="text-xs text-gray-500 font-medium">{user.objetivo}</div>
                          </div>
                        </div>
                        <div className="text-sm font-bold text-slate-300 group-hover:text-blue-400">
                          {user.xp} XP ✨
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-gray-500 text-center">
                    <span className="text-2xl mb-2 block">🤷‍♂️</span>
                    No hemos encontrado a nadie con "<span className="font-bold text-slate-700">{busqueda}</span>"
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}