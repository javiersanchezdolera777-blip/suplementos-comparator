"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import StackDetalleModal from './StackDetalleModal';

interface Props {
  perfil: any;
  recargarPerfil: () => void;
}

export default function GestorStacks({ perfil, recargarPerfil }: Props) {
  const router = useRouter();
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);
  const [stackSeleccionado, setStackSeleccionado] = useState<any>(null);

  const misStacks = perfil?.stacks || [];

  const crearStackYRedirigir = async (e?: React.FormEvent, categoriaDestino?: string) => {
    if (e) e.preventDefault();
    if (!nombre.trim()) {
      setMensaje("❌ Escribe un nombre para tu Stack primero.");
      return;
    }
    
    setCargando(true);
    setMensaje("");
    
    try {
      const token = localStorage.getItem("suparator_token");
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/stacks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: nombre,
          descripcion: descripcion,
          es_publico: true
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMensaje("✅ ¡Stack creado con éxito!");
        setNombre("");
        setDescripcion("");
        recargarPerfil(); 
        
        // Redirigir mágicamente al catálogo filtrado para añadir productos
        if (categoriaDestino) {
           router.push(`/?add_to_stack=${data.id}&categoria=${categoriaDestino}`);
        }
      } else {
        const textError = await res.text();
        try {
           const jsonError = JSON.parse(textError);
           setMensaje("❌ " + (jsonError.detail || "Error al crear el stack"));
        } catch {
           setMensaje("❌ Error interno del servidor.");
        }
      }
    } catch (error) {
      setMensaje("❌ Error de red: No se pudo conectar con el servidor.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-3xl shadow-lg shadow-blue-900/5 border border-gray-100 relative overflow-hidden">
      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-b from-blue-50 to-transparent rounded-full blur-3xl -mr-20 -mt-20 opacity-70 pointer-events-none"></div>
      
      <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-block bg-blue-100 text-blue-700 font-bold px-3 py-1 rounded-full text-xs mb-3 tracking-wide uppercase">Tu Colección</div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tight">Mis Stacks</h2>
          <p className="text-gray-500 text-base mt-2 max-w-lg">Organiza tus suplementos en rutinas para cada objetivo. Compártelos y demuestra cómo entrenas.</p>
        </div>
      </div>

      {/* Cuadrícula de Stacks Actuales */}
      {misStacks.length > 0 ? (
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-10">
          {misStacks.map((stack: any) => (
            <div 
              key={stack.id} 
              onClick={() => setStackSeleccionado(stack)}
              className="group relative bg-white border border-slate-200 rounded-2xl p-6 hover:border-blue-400 hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300 cursor-pointer overflow-hidden transform hover:-translate-y-1 flex flex-col h-full"
            >
              {/* Subtle top border gradient */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-400 to-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 text-xl group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300 shadow-inner">
                  ⚡
                </div>
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-slate-300 group-hover:bg-blue-50 group-hover:text-blue-500 transition-all duration-300">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                </div>
              </div>
              
              <h3 className="font-bold text-xl text-slate-800 mb-2 group-hover:text-blue-600 transition-colors line-clamp-1">{stack.nombre}</h3>
              {stack.descripcion && <p className="text-gray-500 text-sm line-clamp-2 mb-4 flex-1">{stack.descripcion}</p>}
              
              <div className="flex items-center gap-2 mt-auto pt-4 border-t border-slate-100 w-full">
                <span className="flex items-center justify-center bg-slate-100 text-slate-600 font-bold px-3 py-1.5 rounded-lg text-xs group-hover:bg-blue-100 group-hover:text-blue-700 transition-colors">
                  📦 {stack.productos?.length || 0} Productos
                </span>
                {stack.es_publico && (
                  <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1.5 rounded-lg border border-emerald-100 ml-auto">Público</span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="relative z-10 bg-gradient-to-br from-slate-50 to-blue-50/30 rounded-3xl p-10 text-center mb-10 border-2 border-dashed border-blue-200/50">
          <div className="text-6xl mb-4 drop-shadow-sm">🗂️</div>
          <h3 className="text-xl font-bold text-slate-800 mb-2">Tu arsenal está vacío</h3>
          <p className="text-gray-500 max-w-sm mx-auto">Crea tu primer Stack para organizar tu suplementación diaria y presumir de rutina.</p>
        </div>
      )}

      {/* Formulario para Crear Nuevo Stack */}
      <div className="relative z-10 bg-slate-900 rounded-3xl p-1 overflow-hidden shadow-2xl shadow-slate-900/10">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-500 opacity-20 blur-xl"></div>
        <form onSubmit={(e) => crearStackYRedirigir(e)} className="relative bg-white rounded-[23px] p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600 font-black text-xl">+</div>
            <div>
              <h3 className="text-xl font-bold text-slate-900">Arma tu Combo</h3>
              <p className="text-xs text-slate-500 font-medium mt-0.5">Un "Stack" es tu conjunto de suplementos.</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-black text-slate-400 uppercase tracking-wider mb-2">Nombre del Stack</label>
              <input 
                type="text" 
                required 
                placeholder="Ej: Definición Extrema 2026" 
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 focus:bg-white outline-none transition-all font-medium text-slate-800 placeholder-slate-400"
              />
            </div>
            
            <div>
              <label className="block text-[11px] font-black text-slate-400 uppercase tracking-wider mb-2">Descripción (Opcional)</label>
              <input 
                type="text" 
                placeholder="¿Para qué usas este combo?" 
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 focus:bg-white outline-none transition-all font-medium text-slate-800 placeholder-slate-400"
              />
            </div>
          </div>

          <div className="mt-8 border-t border-slate-100 pt-6">
            <label className="block text-[11px] font-black text-slate-400 uppercase tracking-wider mb-3 text-center">
              Añadir un producto y crear
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button 
                type="button" 
                onClick={() => crearStackYRedirigir(undefined, 'proteina')}
                className="flex flex-col items-center justify-center gap-2 bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 rounded-2xl p-4 transition-all hover:scale-105 active:scale-95 group"
              >
                <div className="text-3xl group-hover:scale-110 transition-transform">🥛</div>
                <span className="text-xs font-bold text-slate-600 group-hover:text-blue-700">+ Proteína</span>
              </button>
              
              <button 
                type="button" 
                onClick={() => crearStackYRedirigir(undefined, 'creatina')}
                className="flex flex-col items-center justify-center gap-2 bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 rounded-2xl p-4 transition-all hover:scale-105 active:scale-95 group"
              >
                <div className="text-3xl group-hover:scale-110 transition-transform">⚡</div>
                <span className="text-xs font-bold text-slate-600 group-hover:text-indigo-700">+ Creatina</span>
              </button>

              <button 
                type="button" 
                onClick={() => crearStackYRedirigir(undefined, 'vitaminas')}
                className="flex flex-col items-center justify-center gap-2 bg-slate-50 hover:bg-amber-50 border border-slate-200 hover:border-amber-200 rounded-2xl p-4 transition-all hover:scale-105 active:scale-95 group"
              >
                <div className="text-3xl group-hover:scale-110 transition-transform">💊</div>
                <span className="text-xs font-bold text-slate-600 group-hover:text-amber-700">+ Vitaminas</span>
              </button>

              <button 
                type="button" 
                onClick={() => crearStackYRedirigir(undefined, '')}
                className="flex flex-col items-center justify-center gap-2 bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-200 rounded-2xl p-4 transition-all hover:scale-105 active:scale-95 group"
              >
                <div className="text-3xl group-hover:scale-110 transition-transform">🏋️</div>
                <span className="text-xs font-bold text-slate-600 group-hover:text-emerald-700">+ Otros</span>
              </button>
            </div>
            
            <div className="mt-4 pt-4 flex justify-center">
              <button 
                type="submit" 
                disabled={cargando}
                className="text-xs font-bold text-slate-400 hover:text-slate-700 underline decoration-slate-300 underline-offset-4 disabled:opacity-50"
              >
                {cargando ? 'Creando...' : 'Crear Stack vacío sin añadir productos'}
              </button>
            </div>
          </div>
          
          {mensaje && (
            <div className={`mt-5 p-4 rounded-xl text-sm font-bold flex items-center justify-center gap-3 border ${mensaje.includes('✅') ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-red-50 text-red-700 border-red-100'}`}>
              <span className="text-xl">{mensaje.includes('✅') ? '🎉' : '⚠️'}</span>
              {mensaje.replace('✅', '').replace('❌', '')}
            </div>
          )}
        </form>
      </div>

      <StackDetalleModal 
        stack={stackSeleccionado} 
        isOpen={stackSeleccionado !== null} 
        onClose={() => setStackSeleccionado(null)} 
        esMio={true} 
      />
    </div>
  );
}