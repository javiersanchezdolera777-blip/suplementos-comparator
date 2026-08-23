"use client";
import React, { useState, useEffect } from 'react';
import GymMascota from '@/components/GymMascota';
// Importamos tu modal de login (ajusta la ruta si es distinta, por el error anterior sé que lo tienes por aquí)
import LoginModal from '@/components/LoginModal'; 

export default function MiZonaPage() {
  const [perfil, setPerfil] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Control de estados de la pantalla
  const [necesitaLogin, setNecesitaLogin] = useState(false);
  const [necesitaPerfil, setNecesitaPerfil] = useState(false);
  
  // Formulario de creación
  const [formUsername, setFormUsername] = useState("");
  const [formObjetivo, setFormObjetivo] = useState("Mantenimiento");
  const [errorForm, setErrorForm] = useState("");

  useEffect(() => {
    comprobarEstado();
  }, []);

  const comprobarEstado = async () => {
    const token = localStorage.getItem("token"); // Ajusta si en tu app se llama diferente
    
    if (!token) {
      setNecesitaLogin(true);
      setLoading(false);
      return;
    }

    try {
      // CAMBIO: Sustituimos localhost por 127.0.0.1 para evitar errores de red de Next.js
      const res = await fetch("http://127.0.0.1:8000/api/perfil/me", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setPerfil(data);
      } else if (res.status === 404) {
        // El usuario está logueado pero no ha creado su @username
        setNecesitaPerfil(true);
      } else {
        // El token caducó o es inválido
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

    // CAMBIO: Sustituimos localhost por 127.0.0.1
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
      // ¡Éxito! Recargamos el estado para que cargue el Tamagotchi
      setNecesitaPerfil(false);
      comprobarEstado();
    } else {
      const data = await res.json();
      setErrorForm(data.detail || "Error al crear perfil");
    }
  };

  // --- RENDERIZADO DE LAS 3 PANTALLAS ---

  if (loading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;

  // PANTALLA 1: PEDIR LOGIN
  if (necesitaLogin) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4 text-center">
        <h1 className="text-3xl font-bold mb-4">Únete a la Comunidad</h1>
        <p className="text-gray-600 mb-8 max-w-md">Inicia sesión para ganar XP diaria, subir de nivel y compartir tus rutinas con el resto.</p>
        {/* Aquí renderizamos el modal que ya teníais programado Javiki y tú */}
        <LoginModal />
        <button 
          onClick={() => {
            // Un pequeño truco por si el LoginModal no se abre solo
            alert("Si no ves el Login, revisa cómo se abre tu LoginModal en la cabecera (Navbar). Una vez logueado, recarga esta página.");
          }}
          className="mt-4 text-sm text-blue-600 underline"
        >
          Ya he iniciado sesión, recargar
        </button>
      </div>
    );
  }

  // PANTALLA 2: ONBOARDING (CREAR @USERNAME)
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
                className="flex-1 block w-full px-3 py-2 border border-gray-300 rounded-r-md focus:ring-blue-500 focus:border-blue-500" 
                placeholder="FitBoy99" />
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

  // PANTALLA 3: EL TAMAGOTCHI 
  // ¡EL PARACAÍDAS! Si el backend está apagado o falla, mostramos este error amigable en vez de romper la web entera.
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
        <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-3xl font-black text-slate-900">@{perfil.username}</h1>
            <p className="text-gray-500 mt-1">Fase: <span className="font-semibold">{perfil.objetivo_etapa}</span></p>
          </div>
          <div className="mt-4 sm:mt-0 text-center sm:text-right">
            <div className="text-sm text-gray-500 uppercase tracking-wide">Racha Actual</div>
            <div className="text-3xl font-bold text-orange-500">🔥 {perfil.racha_actual} días</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GymMascota xpTotales={perfil.puntos_totales} objetivo={perfil.objetivo_etapa || "Mantenimiento"} />
          
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center">
            <h3 className="text-xl font-bold text-slate-800 mb-2">Ritual Diario</h3>
            <button 
              onClick={async () => {
                try {
                  // CAMBIO: Sustituimos localhost por 127.0.0.1
                  const res = await fetch("http://127.0.0.1:8000/api/comunidad/checkin", {
                    method: "POST", headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
                  });
                  const data = await res.json();
                  if(res.ok) comprobarEstado(); else alert(data.detail);
                } catch (error) {
                  alert("Fallo de conexión. Revisa que el backend esté encendido.");
                }
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-full text-lg shadow-lg"
            >
              🔥 Hacer Check-in Hoy
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}