"use client";
import React, { useState, useEffect } from 'react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  productoId: number;
  productoNombre: string;
}

export default function ModalAñadirStack({ isOpen, onClose, productoId, productoNombre }: Props) {
  const [misStacks, setMisStacks] = useState<any[]>([]);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState("");

  // Cuando el modal se abre, le pedimos al backend la lista actualizada de tus Stacks
  useEffect(() => {
    if (isOpen) {
      cargarMisStacks();
      setMensaje(""); // Limpiamos mensajes anteriores
    }
  }, [isOpen]);

  const cargarMisStacks = async () => {
    setCargando(true);
    try {
      const token = localStorage.getItem("suparator_token");
      if (!token) {
        setMensaje("Debes iniciar sesión para usar los Stacks.");
        setCargando(false);
        return;
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/perfil/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setMisStacks(data.stacks || []);
      }
    } catch (error) {
      setMensaje("Error al cargar tus rutinas.");
    } finally {
      setCargando(false);
    }
  };

  const añadirAlStack = async (stackId: number) => {
    try {
      const token = localStorage.getItem("suparator_token");
      // Llamamos a la ruta exacta que programaste ayer en el backend
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/stacks/${stackId}/productos/${productoId}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });

      const data = await res.json();
      
      if (res.ok) {
        setMensaje(`✅ ${data.mensaje}`);
        // Cerramos el modal automáticamente después de 1.5 segundos
        setTimeout(() => onClose(), 1500); 
      } else {
        setMensaje(`❌ ${data.detail || "Error al añadir producto"}`);
      }
    } catch (error) {
      setMensaje("❌ Error de conexión.");
    }
  };

  // Si no está abierto, no renderizamos nada
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-fade-in-up">
        
        {/* Cabecera del Modal */}
        <div className="bg-slate-800 p-4 flex justify-between items-center text-white">
          <h3 className="font-bold text-lg">Añadir a mi Rutina</h3>
          <button onClick={onClose} className="text-gray-300 hover:text-white text-2xl leading-none">&times;</button>
        </div>

        {/* Cuerpo del Modal */}
        <div className="p-6">
          <p className="text-gray-600 mb-4 text-sm">
            ¿En qué Stack quieres guardar <span className="font-bold text-slate-800">"{productoNombre}"</span>?
          </p>

          {cargando ? (
            <div className="text-center text-gray-500 py-4">Cargando tus Stacks...</div>
          ) : misStacks.length === 0 ? (
            <div className="text-center text-orange-500 py-4 font-medium">
              Aún no has creado ningún Stack. Ve a "Mi Zona" para crear uno.
            </div>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
              {misStacks.map((stack) => (
                <button
                  key={stack.id}
                  onClick={() => añadirAlStack(stack.id)}
                  className="w-full text-left px-4 py-3 border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all group flex justify-between items-center"
                >
                  <span className="font-bold text-slate-700 group-hover:text-blue-700">{stack.nombre}</span>
                  <span className="text-xl opacity-0 group-hover:opacity-100 transition-opacity">➕</span>
                </button>
              ))}
            </div>
          )}

          {mensaje && (
            <div className={`mt-4 p-3 rounded-lg text-sm font-semibold text-center ${mensaje.includes('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {mensaje}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}