"use client";
import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import GymMascota from '@/components/GymMascota';
import StackDetalleModal from '@/components/StackDetalleModal';

export default function PerfilPublico() {
  const params = useParams();
  const username = params.username as string;

  const [perfil, setPerfil] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [siguiendo, setSiguiendo] = useState(false);
  
  // Estado para el modal de ver productos
  const [stackSeleccionado, setStackSeleccionado] = useState<any>(null);

  useEffect(() => {
    const cargarPerfilPublico = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/perfil/${username}`);
        
        if (res.ok) {
          const data = await res.json();
          setPerfil(data);
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
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Debes iniciar sesión para seguir a otros usuarios.");
        return;
      }

      const res = await fetch(`http://127.0.0.1:8000/api/comunidad/seguir/${username}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });

      const data = await res.json();
      
      if (res.ok) {
        setSiguiendo(!siguiendo);
        alert(data.mensaje);
      } else {
        alert(`❌ ${data.detail}`);
      }
    } catch (error) {
      alert("Error de conexión al intentar seguir al usuario.");
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
        
        {/* MINI-MENÚ NAVEGACIÓN (Lo he movido aquí arriba para que sea lo primero que veas) */}
        <div className="flex justify-between items-center">
          <a href="/" className="text-gray-500 hover:text-slate-800 font-bold text-sm transition-colors">⬅️ Volver a tienda</a>
          <a href="/comunidad" className="bg-white border border-gray-200 text-slate-700 px-4 py-2 rounded-full font-bold shadow-sm hover:bg-gray-50 flex items-center gap-2 transition-colors">
            🔍 Buscar amigos
          </a>
        </div>

        {/* CABECERA SOCIAL */}
        <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-8 rounded-2xl shadow-sm border border-gray-100 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-3xl -mr-10 -mt-10"></div>
          
          <div className="relative z-10 flex flex-col sm:flex-row items-center sm:items-start gap-4">
            <div className="w-20 h-20 bg-gradient-to-tr from-blue-600 to-cyan-500 rounded-full flex items-center justify-center text-white text-3xl font-black shadow-md">
              {perfil.username.charAt(0).toUpperCase()}
            </div>
            <div className="text-center sm:text-left">
              <h1 className="text-3xl font-black text-slate-900">@{perfil.username}</h1>
              <p className="text-gray-500 mt-1">Fase Actual: <span className="font-semibold text-blue-600">{perfil.objetivo_etapa}</span></p>
              <div className="flex items-center gap-4 mt-3 justify-center sm:justify-start">
                <div className="text-sm font-semibold text-slate-700"><span className="text-lg font-black text-slate-900">{perfil.racha_actual}</span> 🔥 Racha</div>
                <div className="text-sm font-semibold text-slate-700"><span className="text-lg font-black text-slate-900">{perfil.puntos_totales}</span> ✨ XP</div>
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

          <div className="md:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Rutinas de {perfil.username}</h2>
            <p className="text-gray-500 text-sm mb-6">Descubre y copia los suplementos que usa en su día a día.</p>
            
            {stacksPublicos.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {stacksPublicos.map((stack: any) => (
                  <div 
                    key={stack.id} 
                    // PASO 3: Aquí está el evento que abre el modal al hacer clic
                    onClick={() => setStackSeleccionado(stack)}
                    className="border border-gray-100 bg-gray-50 rounded-xl p-5 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group"
                  >
                    <div className="flex justify-between items-start">
                      <h3 className="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition-colors">{stack.nombre}</h3>
                      <span className="text-gray-400 group-hover:text-blue-500 transition-colors">↗️</span>
                    </div>
                    {stack.descripcion && <p className="text-gray-500 text-sm mt-1">{stack.descripcion}</p>}
                    <div className="mt-4 text-sm font-semibold text-blue-600 bg-blue-100/50 inline-block px-3 py-1 rounded-full">
                      {stack.productos?.length || 0} Productos
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-xl p-8 text-center border border-dashed border-gray-200">
                <span className="text-4xl">📭</span>
                <p className="text-gray-500 mt-3 font-medium">Este usuario aún no ha publicado ninguna rutina.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* PASO 4: EL MODAL DE DETALLE PARA COTILLEAR */}
      <StackDetalleModal 
        stack={stackSeleccionado} 
        isOpen={stackSeleccionado !== null} 
        onClose={() => setStackSeleccionado(null)} 
        esMio={false} // ¡NO ES MÍO! Por eso no saldrán los botones de añadir.
      />
    </div>
  );
}