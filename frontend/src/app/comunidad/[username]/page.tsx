"use client";
import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import GymMascota from '@/components/GymMascota';
import StackDetalleModal from '@/components/StackDetalleModal';
import NavbarSocial from '@/components/navBarSocial';

export default function PerfilPublico() {
  const params = useParams();
  const username = params.username as string;

  const [perfil, setPerfil] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [siguiendo, setSiguiendo] = useState(false);
  
  const [stackSeleccionado, setStackSeleccionado] = useState<any>(null);

  useEffect(() => {
    const cargarPerfilPublico = async () => {
      try {
        const token = localStorage.getItem("suparator_token");
        const headers: Record<string, string> = {};
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }
        
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${API_URL}/api/perfil/${username}`, { headers });
        
        if (res.ok) {
          const data = await res.json();
          setPerfil(data);
          setSiguiendo(data.is_following || false);
        } else if (res.status === 404) {
          setError(`No hemos encontrado a ningún usuario llamado @${username}`);
        } else {
          setError("Error al cargar el perfil.");
        }
      } catch (err) {
        setError("Error de conexión con el servidor. ¿Está encendido el backend?");
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      cargarPerfilPublico();
    }
  }, [username]);

  const seguirUsuario = async () => {
    try {
      const token = localStorage.getItem("suparator_token");
      if (!token) {
        alert("Debes iniciar sesión para seguir a otros usuarios.");
        return;
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/comunidad/seguir/${username}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });

      const data = await res.json();
      
      if (res.ok) {
        setPerfil({
          ...perfil,
          seguidores_count: perfil.seguidores_count + (siguiendo ? -1 : 1)
        });
        
        setSiguiendo(!siguiendo); 
        alert(data.mensaje); 
      } else {
        alert(`❌ ${data.detail}`);
      }
    } catch (error) {
      alert("Error de conexión al intentar seguir al usuario.");
    }
  };

  const toggleLikeStack = async (e: React.MouseEvent, stackId: number) => {
    e.stopPropagation();
    
    const token = localStorage.getItem("suparator_token");
    if (!token) {
      alert("Debes iniciar sesión para dar like.");
      return;
    }

    // Optimistic Update
    setPerfil((prev: any) => {
      const newStacks = prev.stacks.map((stack: any) => {
        if (stack.id === stackId) {
          const isLiked = !stack.is_liked_by_me;
          return {
            ...stack,
            is_liked_by_me: isLiked,
            likes_count: isLiked ? (stack.likes_count || 0) + 1 : Math.max(0, (stack.likes_count || 0) - 1)
          };
        }
        return stack;
      });
      return { ...prev, stacks: newStacks };
    });

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/stacks/${stackId}/like`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        console.error("Error al dar like");
      }
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-500 font-semibold">Buscando perfil...</div>;
  
  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4 text-center">
        <h1 className="text-4xl mb-4">🕵️‍♂️</h1>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Perfil no encontrado</h2>
        <p className="text-gray-500">{error}</p>
        <a href="/" className="mt-6 text-blue-600 font-semibold hover:underline">Volver a la tienda</a>
      </div>
    );
  }

  const stacksPublicos = perfil.stacks?.filter((stack: any) => stack.es_publico) || [];

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* BARRA DE NAVEGACIÓN NUEVA */}
        <NavbarSocial />

        <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-8 rounded-2xl shadow-sm border border-gray-100 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-3xl -mr-10 -mt-10"></div>
          
          <div className="relative z-10 flex flex-col sm:flex-row items-center sm:items-start gap-4">
            <div className="w-20 h-20 bg-gradient-to-tr from-blue-600 to-cyan-500 rounded-full flex items-center justify-center text-white text-3xl font-black shadow-md overflow-hidden">
              {perfil.foto_perfil ? (
                <img src={perfil.foto_perfil} alt="Avatar" className="w-full h-full object-cover" />
              ) : (
                perfil.username.charAt(0).toUpperCase()
              )}
            </div>
            <div className="text-center sm:text-left">
              <h1 className="text-3xl font-black text-slate-900">@{perfil.username}</h1>
              <p className="text-gray-500 mt-1">Fase Actual: <span className="font-semibold text-blue-600">{perfil.objetivo_etapa}</span></p>
              
              {perfil.descripcion && (
                <p className="mt-2 text-sm text-slate-600 max-w-md bg-slate-50 p-3 rounded-lg border border-slate-100">{perfil.descripcion}</p>
              )}

              <div className="flex items-center gap-4 mt-3 justify-center sm:justify-start">
                <div className="text-sm font-semibold text-slate-700"><span className="text-lg font-black text-slate-900">{perfil.racha_actual}</span> 🔥 Racha</div>
                <div className="text-sm font-semibold text-slate-700"><span className="text-lg font-black text-slate-900">{perfil.puntos_totales}</span> ✨ XP</div>
              </div>
              
              <div className="flex items-center gap-4 mt-4 justify-center sm:justify-start pt-4 border-t border-gray-100">
                <div className="text-sm font-medium text-gray-500 hover:text-slate-800 cursor-pointer transition-colors">
                  <span className="text-lg font-bold text-slate-900 mr-1">{perfil.seguidores_count || 0}</span> 
                  Seguidores
                </div>
                <div className="text-sm font-medium text-gray-500 hover:text-slate-800 cursor-pointer transition-colors">
                  <span className="text-lg font-bold text-slate-900 mr-1">{perfil.siguiendo_count || 0}</span> 
                  Siguiendo
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 sm:mt-0 relative z-10">
            <button 
              onClick={seguirUsuario}
              className={`font-bold py-3 px-8 rounded-full shadow-lg transition-all transform hover:-translate-y-1 active:scale-95 ${
                siguiendo 
                  ? "bg-gray-200 text-slate-700 border border-gray-300 hover:bg-red-100 hover:text-red-600 hover:border-red-200 hover:shadow-none" 
                  : "bg-slate-900 text-white hover:bg-slate-800"
              }`}
            >
              {siguiendo ? "Siguiendo" : "+ Seguir"}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <GymMascota xpTotales={perfil.puntos_totales} objetivo={perfil.objetivo_etapa || "Mantenimiento"} />
          </div>

          <div className="md:col-span-2 flex flex-col gap-4">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-black text-slate-800">Stacks de {perfil.username}</h2>
                <p className="text-slate-500 text-sm mt-1">Descubre su suplementación y el presupuesto invertido.</p>
              </div>
              <div className="text-4xl hidden sm:block">💊</div>
            </div>
            
            {stacksPublicos.length > 0 ? (
              <div className="grid grid-cols-1 gap-5">
                {stacksPublicos.map((stack: any) => {
                  const numProductos = stack.productos?.length || 0;
                  const precioTotal = stack.productos?.reduce((acc: number, p: any) => {
                    return acc + (p.precio_actual || p.precio_anterior || 0);
                  }, 0) || 0;
                  const categoriasUnicas = Array.from(new Set(stack.productos?.map((p: any) => p.categoria?.nombre).filter(Boolean)));

                  return (
                    <div 
                      key={stack.id} 
                      onClick={() => setStackSeleccionado(stack)}
                      className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 hover:shadow-lg hover:border-blue-200 transition-all cursor-pointer group flex flex-col sm:flex-row gap-6 relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-50 to-transparent opacity-50 rounded-bl-full pointer-events-none transition-transform group-hover:scale-110"></div>
                      
                      <div className="flex-1 z-10">
                        <div className="flex justify-between items-start">
                          <h3 className="font-black text-xl text-slate-900 group-hover:text-blue-600 transition-colors">{stack.nombre}</h3>
                          
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
                        {stack.descripcion && <p className="text-slate-500 text-sm mt-2 max-w-md">{stack.descripcion}</p>}
                        
                        <div className="flex flex-wrap items-center gap-2 mt-4">
                          <div className="text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
                            {numProductos} Productos
                          </div>
                          {precioTotal > 0 && (
                            <div className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-100">
                              ~{precioTotal.toFixed(2)}€
                            </div>
                          )}
                          {categoriasUnicas.slice(0, 2).map((cat: any, idx: number) => (
                            <div key={idx} className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-md uppercase tracking-wider">
                              {cat}
                            </div>
                          ))}
                        </div>
                      </div>

                      {numProductos > 0 && (
                        <div className="flex items-center gap-2 z-10 sm:w-1/3 justify-start sm:justify-end">
                          {stack.productos.slice(0, 3).map((p: any, idx: number) => (
                            <div key={idx} className="w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden flex-shrink-0 -ml-4 first:ml-0 relative group-hover:border-blue-300 transition-colors z-20 hover:z-30 hover:scale-110">
                              {p.imagen_url ? (
                                <img src={p.imagen_url} alt="Prod" className="w-full h-full object-contain p-1" />
                              ) : (
                                <div className="w-full h-full bg-slate-100 flex items-center justify-center text-xs">💊</div>
                              )}
                            </div>
                          ))}
                          {numProductos > 3 && (
                            <div className="w-10 h-10 rounded-full bg-slate-50 border border-slate-200 text-slate-500 text-xs font-bold flex items-center justify-center -ml-4 z-10">
                              +{numProductos - 3}
                            </div>
                          )}
                        </div>
                      )}
                      
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="bg-white rounded-2xl p-10 text-center border border-dashed border-slate-200">
                <span className="text-5xl opacity-50 block mb-4">📭</span>
                <h4 className="text-lg font-bold text-slate-800">No hay Stacks públicos</h4>
                <p className="text-slate-500 text-sm mt-1 max-w-sm mx-auto">Este atleta aún no ha compartido su suplementación con la comunidad.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <StackDetalleModal 
        stack={stackSeleccionado} 
        isOpen={stackSeleccionado !== null} 
        onClose={() => setStackSeleccionado(null)} 
        esMio={false} 
      />
    </div>
  );
}