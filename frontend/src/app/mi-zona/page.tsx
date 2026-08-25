"use client";
import React, { useState, useEffect } from 'react';
import GymMascota from '@/components/GymMascota';
import GestorStacks from '@/components/GestorStacks';
import ModalAñadirStack from '@/components/ModalAñadirStack';
import { useAuth } from '@/context/AuthContext'; 
import LoginModal from '@/components/LoginModal'; 

export default function MiZonaPage() {
  const { isLoggedIn, openLoginModal } = useAuth();
  const [perfil, setPerfil] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [necesitaLogin, setNecesitaLogin] = useState(false);
  const [necesitaPerfil, setNecesitaPerfil] = useState(false);
  
  const [formUsername, setFormUsername] = useState("");
  const [formObjetivo, setFormObjetivo] = useState("Mantenimiento");
  const [errorForm, setErrorForm] = useState("");
  const [modalAbierto, setModalAbierto] = useState(false);

  useEffect(() => {
    if (isLoggedIn) {
      setNecesitaLogin(false);
      comprobarEstado();
    } else {
      setNecesitaLogin(true);
      setPerfil(null); 
      setLoading(false);
    }
  }, [isLoggedIn]);

  const comprobarEstado = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setNecesitaLogin(true);
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/api/perfil/me", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setPerfil(data);
      } else if (res.status === 404) {
        setNecesitaPerfil(true);
      } else {
        setNecesitaLogin(true);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const crearPerfil = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorForm("");
    const token = localStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/api/perfil", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        username: formUsername,
        objetivo_etapa: formObjetivo,
        suplemento_favorito: "Por decidir"
      })
    });

    if (res.ok) {
      setNecesitaPerfil(false);
      comprobarEstado();
    } else {
      const data = await res.json();
      setErrorForm(data.detail || "Error al crear perfil");
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-500 font-semibold">Cargando tu zona...</div>;

  if (necesitaLogin) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4 text-center">
        <h1 className="text-3xl font-bold mb-4">Únete a la Comunidad</h1>
        <p className="text-gray-600 mb-8 max-w-md">Inicia sesión para ganar XP diaria, subir de nivel y compartir tus rutinas con el resto.</p>
        <button onClick={openLoginModal} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transition-transform transform hover:-translate-y-1">
          Iniciar Sesión
        </button>
      </div>
    );
  }

  if (necesitaPerfil) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <form onSubmit={crearPerfil} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 w-full max-w-md">
          <h2 className="text-2xl font-bold mb-2">Crea tu Identidad</h2>
          <p className="text-gray-500 mb-6 text-sm">Elige cómo te verán los demás usuarios.</p>
          
          <div className="mb-4">
            <label className="block text-sm font-bold text-gray-700 mb-1">Nombre de Usuario</label>
            <div className="flex">
              <span className="inline-flex items-center px-3 bg-gray-100 border border-r-0 border-gray-300 rounded-l-md text-gray-500 font-bold">@</span>
              <input type="text" required value={formUsername} onChange={e => setFormUsername(e.target.value)}
                className="flex-1 block w-full px-3 py-2 border border-gray-300 rounded-r-md focus:ring-blue-500 focus:border-blue-500" placeholder="FitBoy99" />
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-700 mb-1">Fase Actual</label>
            <select value={formObjetivo} onChange={e => setFormObjetivo(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
              <option value="Volumen">💪 Volumen</option>
              <option value="Definición">✂️ Definición</option>
              <option value="Mantenimiento">⚖️ Mantenimiento</option>
            </select>
          </div>
          {errorForm && <p className="text-red-500 text-sm mb-4">{errorForm}</p>}
          <button type="submit" className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition">
            Crear mi Perfil
          </button>
        </form>
      </div>
    );
  }

  if (!perfil) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-500 font-semibold p-4 text-center">
        Error de conexión: No se pudo cargar tu perfil. Asegúrate de tener el servidor Backend (FastAPI) encendido en otra terminal.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6">
       <div className="max-w-4xl mx-auto space-y-8">
        
        <div className="flex justify-between items-center mb-6">
          <a href="/" className="text-gray-500 hover:text-slate-800 font-bold text-sm transition-colors">⬅️ Volver a tienda</a>
          <a href="/comunidad" className="bg-white border border-gray-200 text-slate-700 px-4 py-2 rounded-full font-bold shadow-sm hover:bg-gray-50 flex items-center gap-2 transition-colors">
            🔍 Buscar amigos
          </a>
        </div>

        {/* --- CABECERA PRINCIPAL CON CONTADORES --- */}
        <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-8 rounded-2xl shadow-sm border border-gray-100 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-3xl -mr-10 -mt-10"></div>
          
          <div className="relative z-10 flex flex-col sm:flex-row items-center sm:items-start gap-4 w-full">
            <div className="w-20 h-20 bg-gradient-to-tr from-blue-600 to-cyan-500 rounded-full flex items-center justify-center text-white text-3xl font-black shadow-md">
              {perfil.username.charAt(0).toUpperCase()}
            </div>
            
            <div className="text-center sm:text-left flex-1">
              <h1 className="text-3xl font-black text-slate-900">@{perfil.username}</h1>
              <p className="text-gray-500 mt-1">Fase: <span className="font-semibold text-blue-600">{perfil.objetivo_etapa}</span></p>
              
              {/* LOS CONTADORES */}
              <div className="flex items-center gap-4 mt-4 justify-center sm:justify-start pt-4 border-t border-gray-100">
                <div className="text-sm font-medium text-gray-500">
                  <span className="text-lg font-bold text-slate-900 mr-1">{perfil.seguidores_count || 0}</span> Seguidores
                </div>
                <div className="text-sm font-medium text-gray-500">
                  <span className="text-lg font-bold text-slate-900 mr-1">{perfil.siguiendo_count || 0}</span> Siguiendo
                </div>
              </div>
            </div>

            <div className="mt-6 sm:mt-0 relative z-10 text-center sm:text-right bg-orange-50 px-6 py-4 rounded-xl border border-orange-100 shadow-inner">
              <div className="text-xs text-orange-600 uppercase tracking-wide font-bold mb-1">Racha Actual</div>
              <div className="text-3xl font-black text-orange-500">🔥 {perfil.racha_actual} días</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GymMascota xpTotales={perfil.puntos_totales} objetivo={perfil.objetivo_etapa || "Mantenimiento"} />
          
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center">
            <h3 className="text-xl font-bold text-slate-800 mb-2">Ritual Diario</h3>
            <button 
              onClick={async () => {
                try {
                  const res = await fetch("http://127.0.0.1:8000/api/comunidad/checkin", {
                    method: "POST", headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
                  });
                  const data = await res.json();
                  if(res.ok) comprobarEstado(); else alert(data.detail);
                } catch (error) {
                  alert("Fallo de conexión. Revisa que el backend esté encendido.");
                }
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-full text-lg shadow-lg mb-4"
            >
              🔥 Hacer Check-in Hoy
            </button>
            <button onClick={() => setModalAbierto(true)} className="mt-2 text-blue-600 font-bold underline text-sm">
              Test: Simular añadir "Proteína Whey" a un Stack
            </button>
            <ModalAñadirStack isOpen={modalAbierto} onClose={() => setModalAbierto(false)} productoId={1} productoNombre="Proteína Whey Gold Standard" />
          </div>
        </div>
        
        <div className="mt-8">
          <GestorStacks perfil={perfil} recargarPerfil={comprobarEstado} />
        </div>
      </div>
    </div>
  );
}