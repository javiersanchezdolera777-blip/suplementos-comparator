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
  
  // Nuevos estados para el Hub Social
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [stacksDescubrimiento, setStacksDescubrimiento] = useState<any[]>([]);
  const [loadingHub, setLoadingHub] = useState(true);

  // Cargar datos iniciales del Hub
  useEffect(() => {
    const cargarHub = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const [resLideres, resStacks] = await Promise.all([
          fetch(`${API_URL}/api/comunidad/leaderboard`),
          fetch(`${API_URL}/api/comunidad/descubrir-stacks`)
        ]);
        
        if (resLideres.ok) setLeaderboard(await resLideres.json());
        if (resStacks.ok) setStacksDescubrimiento(await resStacks.json());
      } catch (error) {
        console.error("Error cargando el hub:", error);
      } finally {
        setLoadingHub(false);
      }
    };
    cargarHub();
  }, []);

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
        const token = localStorage.getItem("suparator_token");
        const headers: Record<string, string> = {};
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }
        
        const res = await fetch(`${API_URL}/api/comunidad/buscar?q=${busqueda}`, { headers });
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

  const toggleLikeStack = async (e: React.MouseEvent, stackId: number) => {
    e.stopPropagation(); // Evitar navegar al perfil al hacer click en Like
    
    const token = localStorage.getItem("suparator_token");
    if (!token) {
      alert("Debes iniciar sesión para dar like.");
      return;
    }

    // Optimistic Update
    setStacksDescubrimiento(prev => prev.map(stack => {
      if (stack.id === stackId) {
        const isLiked = !stack.is_liked_by_me;
        return {
          ...stack,
          is_liked_by_me: isLiked,
          likes_count: isLiked ? (stack.likes_count || 0) + 1 : Math.max(0, (stack.likes_count || 0) - 1)
        };
      }
      return stack;
    }));

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/stacks/${stackId}/like`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        // Revertir si falla (opcional)
        console.error("Error al dar like");
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center pt-8 px-4 sm:px-6 relative pb-20">
      <div className="w-full max-w-5xl relative z-10 space-y-8">

        {/* NAVEGACIÓN Y CABECERA (HERO BUSCADOR) */}
        <div className="bg-white rounded-3xl shadow-sm border border-slate-100 relative">
          {/* Fondo decorativo encapsulado para no recortar los menús desplegables */}
          <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl -mr-20 -mt-20"></div>
          </div>
          
          <div className="relative z-10 p-6 sm:p-10 flex flex-col items-center text-center">
            <div className="w-full max-w-4xl mx-auto mb-6">
              <NavbarSocial />
            </div>

            <h1 className="text-4xl font-black text-slate-900 tracking-tight mt-4">Hub de Atletas</h1>
          <p className="text-slate-500 mb-8 text-sm sm:text-base max-w-lg mx-auto">Encuentra a tus amigos, compite en el ranking y descubre los mejores stacks de suplementación.</p>

          <div className="relative w-full max-w-xl mx-auto z-20">
            <form onSubmit={enviarFormulario} className="relative shadow-lg shadow-slate-200/50 rounded-full bg-white z-20">
              <span className="absolute inset-y-0 left-0 flex items-center pl-5 text-xl">🔍</span>
              <input
                type="text"
                placeholder="Busca por @username..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="w-full text-base py-4 pl-14 pr-24 rounded-full border border-slate-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 focus:outline-none transition-all text-slate-800 font-medium placeholder-slate-400"
                autoComplete="off"
              />
              <button
                type="submit"
                className="absolute inset-y-1.5 right-1.5 bg-slate-900 text-white font-bold px-6 rounded-full hover:bg-blue-600 transition-colors text-sm"
              >
                Buscar
              </button>
            </form>

            {/* --- MENÚ DESPLEGABLE DE SUGERENCIAS --- */}
            {busqueda.length >= 2 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden z-30 animate-fade-in-up">
                {buscando ? (
                  <div className="p-4 text-slate-400 font-medium text-sm text-center">Buscando atletas...</div>
                ) : sugerencias.length > 0 ? (
                  <div className="flex flex-col max-h-[400px] overflow-y-auto">
                    {sugerencias.map((user) => (
                      <button
                        key={user.username}
                        onClick={() => irAlPerfil(user.username)}
                        className="flex items-center justify-between p-4 hover:bg-slate-50 transition-all border-b border-slate-50 last:border-0 w-full text-left group"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-slate-100 to-slate-200 text-slate-400 font-bold flex items-center justify-center shadow-sm overflow-hidden border border-slate-200 group-hover:border-blue-300 transition-colors flex-shrink-0">
                            {user.foto_perfil ? (
                              <img src={user.foto_perfil} alt={user.username} className="w-full h-full object-cover" />
                            ) : (
                              <span className="text-lg text-slate-500">{user.username.charAt(0).toUpperCase()}</span>
                            )}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-slate-900 group-hover:text-blue-600 transition-colors">@{user.username}</span>
                              {user.is_following && (
                                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-green-50 text-green-700 border border-green-200 uppercase tracking-wide">
                                  Siguiendo ✓
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-slate-500 font-medium uppercase tracking-wider mt-0.5">{user.objetivo}</div>
                          </div>
                        </div>
                        <div className="text-xs font-black text-slate-400 group-hover:text-blue-500 transition-colors bg-slate-50 group-hover:bg-blue-50 px-2 py-1 rounded-md">
                          {user.xp} XP
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-slate-500 text-center text-sm">
                    No hemos encontrado a nadie con "<span className="font-bold text-slate-700">{busqueda}</span>"
                  </div>
                )}
              </div>
            )}
          </div>
          </div>
        </div>

        {/* CONTENIDO PRINCIPAL: 2 COLUMNAS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* COLUMNA IZQUIERDA: LEADERBOARD */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-amber-50 rounded-bl-full pointer-events-none"></div>
              
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-xl shadow-inner border border-amber-200">🏆</div>
                <div>
                  <h2 className="text-lg font-black text-slate-900">Salón de la Fama</h2>
                  <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Top Atletas Global</p>
                </div>
              </div>

              {loadingHub ? (
                <div className="animate-pulse space-y-4">
                  {[1,2,3,4,5].map(i => <div key={i} className="h-12 bg-slate-100 rounded-xl"></div>)}
                </div>
              ) : leaderboard.length > 0 ? (
                <div className="flex flex-col gap-3">
                  {leaderboard.map((user, index) => (
                    <button 
                      key={user.username}
                      onClick={() => irAlPerfil(user.username)}
                      className="flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100 group w-full text-left"
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-sm shadow-sm border ${
                        index === 0 ? 'bg-amber-100 text-amber-700 border-amber-200' :
                        index === 1 ? 'bg-slate-200 text-slate-700 border-slate-300' :
                        index === 2 ? 'bg-orange-100 text-orange-800 border-orange-200' :
                        'bg-white text-slate-400 border-slate-100 group-hover:border-slate-300'
                      }`}>
                        {index + 1}
                      </div>
                      
                      <div className="w-10 h-10 rounded-full bg-slate-100 border border-slate-200 overflow-hidden flex-shrink-0 flex items-center justify-center text-slate-400 font-bold">
                        {user.foto_perfil ? (
                          <img src={user.foto_perfil} alt={user.username} className="w-full h-full object-cover" />
                        ) : (
                          user.username.charAt(0).toUpperCase()
                        )}
                      </div>
                      
                      <div className="flex-1 overflow-hidden">
                        <div className="font-bold text-sm text-slate-800 truncate group-hover:text-blue-600 transition-colors">@{user.username}</div>
                        <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{user.xp} XP • {user.racha}🔥</div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center text-sm text-slate-500 py-4">Aún no hay atletas en el ranking.</div>
              )}
            </div>
          </div>

          {/* COLUMNA DERECHA: ESCAPARATE DE STACKS */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between px-2">
              <h2 className="text-2xl font-black text-slate-900 flex items-center gap-2">
                Explorar Stacks <span className="text-xl">💊</span>
              </h2>
            </div>

            {loadingHub ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[1,2,3,4].map(i => <div key={i} className="h-40 bg-white rounded-2xl border border-slate-100 shadow-sm animate-pulse"></div>)}
              </div>
            ) : stacksDescubrimiento.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {stacksDescubrimiento.map((stack) => {
                  const numProductos = stack.productos?.length || 0;
                  return (
                    <div 
                      key={stack.id}
                      onClick={() => irAlPerfil(stack.autor_username)}
                      className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg hover:border-blue-200 transition-all cursor-pointer group flex flex-col relative overflow-hidden h-full"
                    >
                      <div className="absolute -right-4 -bottom-4 text-8xl opacity-[0.03] transform group-hover:scale-110 transition-transform pointer-events-none">⚡</div>
                      
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 overflow-hidden flex-shrink-0 flex items-center justify-center text-slate-400 font-bold text-xs">
                            {stack.autor_foto ? (
                              <img src={stack.autor_foto} alt="Autor" className="w-full h-full object-cover" />
                            ) : (
                              stack.autor_username.charAt(0).toUpperCase()
                            )}
                          </div>
                          <div className="text-xs font-bold text-slate-500 group-hover:text-blue-500 transition-colors truncate">
                            @{stack.autor_username}
                          </div>
                        </div>

                        {/* LIKE BUTTON */}
                        <button 
                          onClick={(e) => toggleLikeStack(e, stack.id)}
                          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-bold transition-all relative z-20 ${
                            stack.is_liked_by_me 
                              ? 'bg-red-50 text-red-600 border border-red-100' 
                              : 'bg-slate-50 text-slate-400 border border-slate-100 hover:bg-red-50 hover:text-red-500 hover:border-red-100'
                          }`}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox={stack.is_liked_by_me ? "0 0 20 20" : "0 0 24 24"} fill={stack.is_liked_by_me ? "currentColor" : "none"} stroke="currentColor" strokeWidth={stack.is_liked_by_me ? "0" : "2"}>
                            {stack.is_liked_by_me ? (
                              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                            ) : (
                              <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                            )}
                          </svg>
                          <span>{stack.likes_count || 0}</span>
                        </button>
                      </div>

                      <h3 className="text-lg font-black text-slate-800 group-hover:text-blue-600 transition-colors line-clamp-1">{stack.nombre}</h3>
                      {stack.descripcion && (
                        <p className="text-sm text-slate-500 mt-1 line-clamp-2 flex-grow">{stack.descripcion}</p>
                      )}

                      <div className="mt-4 flex items-center justify-between pt-4 border-t border-slate-50">
                        <div className="text-xs font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded-md border border-blue-100">
                          {numProductos} Productos
                        </div>
                        
                        {numProductos > 0 && (
                          <div className="flex items-center -space-x-2">
                            {stack.productos.slice(0, 3).map((p: any, idx: number) => (
                              <div key={idx} className="w-7 h-7 rounded-full bg-white border border-slate-200 shadow-sm overflow-hidden flex items-center justify-center bg-slate-50">
                                {p.imagen_url ? (
                                  <img src={p.imagen_url} alt="P" className="w-full h-full object-contain p-0.5" />
                                ) : (
                                  <span className="text-[8px]">💊</span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="bg-white rounded-3xl p-10 text-center border border-dashed border-slate-200">
                <span className="text-5xl opacity-50 block mb-4">🏜️</span>
                <h4 className="text-lg font-bold text-slate-800">No hay Stacks recientes</h4>
                <p className="text-slate-500 text-sm mt-1">Sé el primero en compartir tu suplementación con la comunidad.</p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}