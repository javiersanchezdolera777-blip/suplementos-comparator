"use client";
import React, { useState, useEffect } from 'react';
import GymMascota from '@/components/GymMascota';
import GestorStacks from '@/components/GestorStacks';
import { useAuth } from '@/context/AuthContext'; 
import Navbar from '@/components/Navbar';
import LoginModal from '@/components/LoginModal'; 
import ModalEditarPerfil from '@/components/ModalEditarPerfil';
import NavbarSocial from '@/components/navBarSocial';

export default function MiZonaPage() {
  const { isLoggedIn, openLoginModal } = useAuth();
  const [perfil, setPerfil] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [necesitaLogin, setNecesitaLogin] = useState(false);
  const [necesitaPerfil, setNecesitaPerfil] = useState(false);
  
  const [formUsername, setFormUsername] = useState("");
  const [formObjetivo, setFormObjetivo] = useState("Mantenimiento");
  const [formBio, setFormBio] = useState("");
  const [formAvatar, setFormAvatar] = useState("");
  const [errorForm, setErrorForm] = useState("");

  const [modalAjustesAbierto, setModalAjustesAbierto] = useState(false);

  useEffect(() => {
    if (necesitaPerfil) {
      const googleName = localStorage.getItem("google_name");
      const googleAvatar = localStorage.getItem("google_avatar");
      if (googleName && !formUsername) {
        const usernameStr = googleName.replace(/\s+/g, '').toLowerCase() + Math.floor(Math.random() * 100);
        setFormUsername(usernameStr);
      }
      if (googleAvatar && !formAvatar) {
        setFormAvatar(googleAvatar);
      }
    }
  }, [necesitaPerfil]);

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
    const token = localStorage.getItem("suparator_token");
    if (!token) {
      setNecesitaLogin(true);
      setLoading(false);
      return;
    }

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/perfil/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setPerfil(data);
      } else if (res.status === 404) {
        setNecesitaPerfil(true);
      } else {
        // Modo silencioso: si falla la sesión, simplemente pedimos login sin asustar al usuario
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
    const token = localStorage.getItem("suparator_token");

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${API_URL}/api/perfil`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        username: formUsername,
        bio: formBio,
        avatar_url: formAvatar,
        suplemento_favorito: "Por decidir"
      })
    });

    if (res.ok) {
      // Como el endpoint POST de Perfil no recibe objetivo_etapa, hacemos un PUT rápido para actualizarlo.
      await fetch(`${API_URL}/api/perfil/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ objetivo_etapa: formObjetivo })
      });
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
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4 relative overflow-hidden">
        {/* Glow de fondo */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-400/20 blur-3xl rounded-full pointer-events-none"></div>
        
        <form onSubmit={crearPerfil} className="relative z-10 bg-white p-8 sm:p-10 rounded-3xl shadow-2xl shadow-blue-900/10 border border-slate-100 w-full max-w-lg">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-black text-slate-900 tracking-tight mb-2">Crea tu Identidad</h2>
            <p className="text-slate-500">Completa tu perfil para unirte a la comunidad.</p>
          </div>

          <div className="flex justify-center mb-8">
            <div className="relative group">
              {formAvatar ? (
                <img src={formAvatar} alt="Avatar" className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg shadow-slate-200" />
              ) : (
                <div className="w-24 h-24 rounded-full bg-slate-100 border-4 border-white shadow-lg shadow-slate-200 flex items-center justify-center text-4xl text-slate-400">👤</div>
              )}
              <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                <span className="text-white text-xs font-bold">Cambiar</span>
                <input type="file" accept="image/*" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onloadend = () => setFormAvatar(reader.result as string);
                    reader.readAsDataURL(file);
                  }
                }} />
              </div>
            </div>
          </div>
          
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Nombre de Usuario</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 font-bold text-slate-400">@</span>
                <input type="text" required value={formUsername} onChange={e => setFormUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 focus:bg-white outline-none transition-all font-medium text-slate-800" placeholder="usuario123" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Descripción (Bio)</label>
              <input type="text" value={formBio} onChange={e => setFormBio(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 focus:bg-white outline-none transition-all font-medium text-slate-800" placeholder="Amante de los hierros..." />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Fase de Entrenamiento</label>
              <div className="relative">
                <select value={formObjetivo} onChange={e => setFormObjetivo(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 focus:bg-white outline-none transition-all font-medium text-slate-800 appearance-none">
                  <option value="Volumen">💪 Volumen</option>
                  <option value="Definición">✂️ Definición</option>
                  <option value="Mantenimiento">⚖️ Mantenimiento</option>
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">▼</div>
              </div>
            </div>
          </div>
          
          {errorForm && <div className="mt-6 p-3 bg-red-50 text-red-600 rounded-lg text-sm font-bold text-center border border-red-100">{errorForm}</div>}
          
          <button type="submit" className="w-full mt-8 h-14 bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 text-lg">
            ¡Empezar ahora!
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
    <div className="min-h-screen bg-slate-50 flex flex-col pb-24 md:pb-0">
      {/* NAVEGACIÓN GLOBAL (Incluye Bottom Bar en Móviles) */}
      <Navbar />

      <div className="flex-1 py-8 px-4 sm:px-6 w-full max-w-5xl mx-auto space-y-8">
        <NavbarSocial />

        {/* --- CABECERA PRINCIPAL PREMIUM --- */}
        <div className="relative bg-white rounded-3xl shadow-xl shadow-blue-900/5 border border-slate-100 overflow-hidden">
          {/* Fondo abstracto */}
          <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500"></div>
          <div className="absolute top-10 left-10 w-64 h-64 bg-white/20 blur-3xl rounded-full mix-blend-overlay pointer-events-none"></div>
          
          <div className="relative pt-16 px-6 sm:px-10 pb-8 flex flex-col sm:flex-row items-center sm:items-start gap-6">
            
            {/* AVATAR DINÁMICO */}
            <div className="relative group">
              <div className="w-28 h-28 bg-white rounded-full p-1.5 shadow-xl shadow-slate-900/10 z-10 relative">
                <div className="w-full h-full bg-gradient-to-tr from-slate-100 to-slate-200 rounded-full flex items-center justify-center text-slate-400 text-4xl font-black overflow-hidden">
                  {perfil.foto_perfil ? (
                    <img src={perfil.foto_perfil} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    perfil.username.charAt(0).toUpperCase()
                  )}
                </div>
              </div>
              <button onClick={() => setModalAjustesAbierto(true)} className="absolute bottom-1 right-1 bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700 hover:scale-110 transition-all z-20">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
              </button>
            </div>
            
            <div className="flex-1 text-center sm:text-left pt-2 sm:pt-14 w-full">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h1 className="text-3xl font-black text-slate-900 tracking-tight">@{perfil.username}</h1>
                  <div className="flex items-center justify-center sm:justify-start gap-2 mt-1">
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-100">
                      {perfil.objetivo_etapa === 'Volumen' ? '💪' : perfil.objetivo_etapa === 'Definición' ? '✂️' : '⚖️'} {perfil.objetivo_etapa}
                    </span>
                  </div>
                </div>

                {/* CONTADORES (Pills) */}
                <div className="flex gap-3 justify-center">
                  <div className="bg-slate-50 px-4 py-2 rounded-2xl border border-slate-100 text-center min-w-[90px]">
                    <div className="text-2xl font-black text-slate-800">{perfil.seguidores_count || 0}</div>
                    <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seguidores</div>
                  </div>
                  <div className="bg-slate-50 px-4 py-2 rounded-2xl border border-slate-100 text-center min-w-[90px]">
                    <div className="text-2xl font-black text-slate-800">{perfil.siguiendo_count || 0}</div>
                    <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Siguiendo</div>
                  </div>
                </div>
              </div>
              
              {/* LA BIOGRAFÍA EN EL PERFIL */}
              {perfil.descripcion && (
                <p className="mt-6 text-sm text-slate-600 max-w-2xl leading-relaxed">{perfil.descripcion}</p>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GymMascota xpTotales={perfil.puntos_totales} objetivo={perfil.objetivo_etapa || "Mantenimiento"} />
          
          <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-8 rounded-3xl shadow-sm border border-orange-100 relative overflow-hidden flex flex-col justify-center">
            <div className="absolute top-0 right-0 text-9xl opacity-5 pointer-events-none transform translate-x-1/4 -translate-y-1/4">🔥</div>
            
            <div className="flex justify-between items-center mb-6 relative z-10">
              <div>
                <h3 className="text-2xl font-black text-orange-900 tracking-tight">Ritual Diario</h3>
                <p className="text-orange-700/70 text-sm font-medium mt-1">Gana XP y sube tu racha.</p>
              </div>
              <div className="text-center bg-white px-4 py-2 rounded-2xl shadow-sm border border-orange-100">
                <div className="text-[10px] text-orange-500 uppercase tracking-wide font-black">Racha</div>
                <div className="text-2xl font-black text-orange-600">{perfil.racha_actual} 🔥</div>
              </div>
            </div>

            <button 
              onClick={async () => {
                const tieneStacks = perfil.stacks && perfil.stacks.length > 0;
                if (!tieneStacks) {
                  const stacksElement = document.getElementById("gestor-stacks");
                  if (stacksElement) {
                    stacksElement.scrollIntoView({ behavior: 'smooth' });
                    // Optional: animate border to draw attention
                    stacksElement.classList.add('ring-4', 'ring-blue-500', 'ring-opacity-50');
                    setTimeout(() => stacksElement.classList.remove('ring-4', 'ring-blue-500', 'ring-opacity-50'), 2000);
                  }
                  return;
                }

                try {
                  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                  const res = await fetch(`${API_URL}/api/comunidad/checkin`, {
                    method: "POST", headers: { "Authorization": `Bearer ${localStorage.getItem("suparator_token")}` }
                  });
                  const data = await res.json();
                  if(res.ok) comprobarEstado(); else alert(data.detail);
                } catch (error) {
                  alert("Fallo de conexión. Revisa que el backend esté encendido.");
                }
              }}
              className="relative z-10 w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-black py-4 px-6 rounded-2xl text-lg shadow-lg shadow-orange-500/30 transform hover:-translate-y-0.5 active:translate-y-0 transition-all duration-300 flex items-center justify-center gap-3"
            >
              <span>{perfil.stacks && perfil.stacks.length === 0 ? "Crea un Stack primero 👇" : "Hacer Check-in (+50 XP)"}</span>
            </button>
          </div>
        </div>
        
        {/* --- GESTOR DE STACKS --- */}
        <div id="gestor-stacks" className="transition-all duration-500 rounded-3xl">
          <GestorStacks 
            stacks={perfil.stacks} 
            recargarPerfil={comprobarEstado} 
          />
        </div>
      </div>

      {/* MODAL DE AJUSTES */}
      <ModalEditarPerfil 
        isOpen={modalAjustesAbierto} 
        onClose={() => setModalAjustesAbierto(false)} 
        perfilActual={perfil}
        onActualizado={comprobarEstado} 
      />
    </div>
  );
}