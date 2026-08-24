"use client";
import React, { useState } from 'react';
import StackDetalleModal from './StackDetalleModal';

interface Props {
  perfil: any;
  recargarPerfil: () => void;
}

export default function GestorStacks({ perfil, recargarPerfil }: Props) {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);
  const [stackSeleccionado, setStackSeleccionado] = useState<any>(null);

  const misStacks = perfil?.stacks || [];

  const crearStack = async (e: React.FormEvent) => {
    e.preventDefault();
    setCargando(true);
    setMensaje("");
    
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://127.0.0.1:8000/api/stacks", {
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
        setMensaje("✅ ¡Stack creado con éxito!");
        setNombre("");
        setDescripcion("");
        recargarPerfil(); // Le pide al backend los datos actualizados
      } else {
        const data = await res.json();
        setMensaje("❌ " + (data.detail || "Error al crear"));
      }
    } catch (error) {
      setMensaje("❌ Error de conexión con el servidor.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Mis Stacks</h2>
          <p className="text-gray-500 text-sm mt-1">Crea listas con tus suplementos favoritos y compártelas.</p>
        </div>
      </div>

      {/* Cuadrícula de Stacks Actuales */}
      {misStacks.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {misStacks.map((stack: any) => (
            <div 
              key={stack.id} 
              onClick={() => setStackSeleccionado(stack)}
              className="border border-gray-200 rounded-xl p-4 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer bg-white group"
            >
              <div className="flex justify-between items-start">
                <h3 className="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition-colors">{stack.nombre}</h3>
                <span className="text-gray-400 group-hover:text-blue-500">↗️</span>
              </div>
              {stack.descripcion && <p className="text-gray-500 text-sm mt-1 line-clamp-2">{stack.descripcion}</p>}
              <div className="mt-4 text-sm font-semibold text-blue-600 bg-blue-50 inline-block px-3 py-1 rounded-full">
                {stack.productos?.length || 0} Productos
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-50 rounded-xl p-6 text-center mb-8 border border-dashed border-gray-300">
          <p className="text-gray-500">Aún no tienes ningún Stack. ¡Crea el primero abajo!</p>
        </div>
      )}

      {/* Formulario para Crear Nuevo Stack */}
      <form onSubmit={crearStack} className="bg-slate-50 p-5 rounded-xl border border-gray-200">
        <h3 className="font-bold text-slate-700 mb-3">Crear un Nuevo Stack</h3>
        <div className="space-y-3">
          <input 
            type="text" 
            required 
            placeholder="Nombre (Ej: Definición Extrema)" 
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <input 
            type="text" 
            placeholder="Descripción corta (Opcional)" 
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <button 
            type="submit" 
            disabled={cargando}
            className="w-full bg-slate-800 text-white font-bold py-2 rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            {cargando ? "Creando..." : "+ Añadir Stack"}
          </button>
          
          {mensaje && <p className="text-sm font-medium text-center mt-2">{mensaje}</p>}
        </div>
      </form>
      {/* EL MODAL DE DETALLE (Que programamos en el Paso 1) */}
      <StackDetalleModal 
        stack={stackSeleccionado} 
        isOpen={stackSeleccionado !== null} 
        onClose={() => setStackSeleccionado(null)} 
        esMio={true} // Como estamos en Mi Zona, SÍ es mío
      />
    </div>
  );
}