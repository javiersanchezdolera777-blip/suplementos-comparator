"use client";
import React, { useState, useEffect } from 'react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  perfilActual: any;
  onActualizado: () => void; // Función para recargar los datos al terminar
}

export default function ModalEditarPerfil({ isOpen, onClose, perfilActual, onActualizado }: Props) {
  const [descripcion, setDescripcion] = useState("");
  const [objetivo, setObjetivo] = useState("");
  const [fotoPerfil, setFotoPerfil] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  // Cuando se abre el modal, cargamos los datos actuales
  useEffect(() => {
    if (perfilActual) {
      setDescripcion(perfilActual.descripcion || "");
      setObjetivo(perfilActual.objetivo_etapa || "Mantenimiento");
      setFotoPerfil(perfilActual.foto_perfil || null);
    }
  }, [perfilActual, isOpen]);

  if (!isOpen) return null;

  // Magia: Convertimos la imagen de tu ordenador a un texto (Base64) para enviarlo al backend
  const handleCambioFoto = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFotoPerfil(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const guardarCambios = async (e: React.FormEvent) => {
    e.preventDefault();
    setGuardando(true);
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/perfil/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("suparator_token")}`
        },
        body: JSON.stringify({
          descripcion: descripcion,
          objetivo_etapa: objetivo,
          foto_perfil: fotoPerfil
        })
      });

      if (res.ok) {
        onActualizado(); // Le decimos a Mi Zona que se refresque
        onClose(); // Cerramos la ventana
      } else {
        alert("Error al actualizar el perfil.");
      }
    } catch (error) {
      alert("Error de conexión con el servidor.");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in-up">
        
        <div className="bg-slate-50 p-5 border-b border-gray-100 flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-800">⚙️ Ajustes del Perfil</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-slate-800 text-3xl leading-none">&times;</button>
        </div>

        <form onSubmit={guardarCambios} className="p-6 space-y-6">
          
          {/* CAMBIAR FOTO */}
          <div className="flex flex-col items-center">
            <div className="relative group cursor-pointer w-24 h-24 rounded-full overflow-hidden border-4 border-slate-50 shadow-sm bg-gradient-to-tr from-blue-100 to-cyan-50">
              {fotoPerfil ? (
                <img src={fotoPerfil} alt="Tu avatar" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-3xl font-black text-blue-500">
                  {perfilActual.username.charAt(0).toUpperCase()}
                </div>
              )}
              {/* Overlay oscuro al pasar el ratón */}
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-xs font-bold">Cambiar</span>
              </div>
              <input type="file" accept="image/*" onChange={handleCambioFoto} className="absolute inset-0 opacity-0 cursor-pointer" />
            </div>
          </div>

          {/* CAMBIAR NOMBRE (BLOQUEADO - IDEA BRILLANTE) */}
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Nombre de Usuario</label>
            <div className="relative">
              <input type="text" disabled value={`@${perfilActual.username}`} className="w-full bg-slate-100 text-slate-400 font-medium px-4 py-2.5 rounded-xl border border-slate-200 cursor-not-allowed" />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 bg-amber-100 text-amber-700 text-[10px] font-black uppercase px-2 py-0.5 rounded flex items-center gap-1 cursor-help" title="Desbloquea la suscripción PRO para cambiar tu identidad.">
                <span>👑</span> PRO
              </div>
            </div>
          </div>

          {/* BIOGRAFÍA */}
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Biografía</label>
            <textarea 
              value={descripcion} 
              onChange={(e) => setDescripcion(e.target.value)} 
              placeholder="Ej: Apasionado del gimnasio. Entrenando para mi primera competición..."
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm resize-none h-24 text-slate-700"
            />
          </div>

          {/* FASE ACTUAL */}
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Fase Actual</label>
            <select 
              value={objetivo} 
              onChange={(e) => setObjetivo(e.target.value)}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm text-slate-700 font-medium"
            >
              <option value="Volumen">💪 Volumen</option>
              <option value="Definición">✂️ Definición</option>
              <option value="Mantenimiento">⚖️ Mantenimiento</option>
            </select>
          </div>

          <button 
            type="submit" 
            disabled={guardando}
            className="w-full bg-slate-900 text-white font-bold py-3.5 rounded-xl hover:bg-slate-800 transition-colors shadow-lg active:scale-95 disabled:opacity-70"
          >
            {guardando ? "Guardando..." : "Guardar Cambios"}
          </button>
        </form>
      </div>
    </div>
  );
}