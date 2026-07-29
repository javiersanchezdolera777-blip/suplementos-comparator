"use client";

import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../context/AuthContext";

export default function LoginModal() {
  const { isLoginModalOpen, closeLoginModal, login } = useAuth();
  
  // Estados para el formulario tradicional
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (!isLoginModalOpen) return null;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Manejo del Login tradicional
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setIsLoading(true);

    try {
      if (isRegister) {
        // 1. Crear Cuenta
        const resReg = await fetch(`${apiUrl}/api/registro`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!resReg.ok) {
          const errData = await resReg.json();
          throw new Error(errData.detail || "Error al registrarse");
        }
      }

      // 2. Iniciar Sesión (se ejecuta tanto en Login directo como tras un Registro exitoso)
      const resLog = await fetch(`${apiUrl}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!resLog.ok) {
        const errData = await resLog.json();
        throw new Error(errData.detail || "Credenciales incorrectas");
      }

      const data = await resLog.json();
      login(data.access_token); // Guardamos el JWT de Diego
      closeLoginModal(); // Cerramos el modal
      
      // Limpiar campos por seguridad
      setEmail("");
      setPassword("");
      
    } catch (error: any) {
      setErrorMsg(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Manejo del Login con Google
  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const res = await fetch(`${apiUrl}/api/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: credentialResponse.credential }),
      });

      if (res.ok) {
        const data = await res.json();
        login(data.access_token); 
        closeLoginModal(); 
      } else {
        setErrorMsg("Fallo al conectar con Google");
      }
    } catch (error) {
      setErrorMsg("Error de conexión");
    }
  };

  return (
    <div 
      className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md transition-opacity"
      onClick={closeLoginModal}
    >
      <div 
        className="bg-[#0a0f1d] border border-white/10 rounded-3xl w-full max-w-md p-8 relative shadow-2xl flex flex-col items-center animate-in zoom-in-95 duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Botón Cerrar */}
        <button 
          onClick={closeLoginModal} 
          className="absolute top-4 right-4 p-2 bg-black/40 hover:bg-white/10 rounded-full transition-colors text-white"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header Modal */}
        <div className="w-14 h-14 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mb-6">
          <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        
        <h2 className="text-2xl font-black text-white mb-2 text-center">
          {isRegister ? "Crea tu cuenta" : "Inicia sesión"}
        </h2>
        <p className="text-slate-400 text-sm text-center mb-8 px-4">
          Guarda tus suplementos favoritos y monitoriza sus precios.
        </p>

        {/* Mensaje de Error */}
        {errorMsg && (
          <div className="w-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold px-4 py-3 rounded-xl mb-6 text-center">
            {errorMsg}
          </div>
        )}

        {/* Formulario Tradicional */}
        <form onSubmit={handleEmailSubmit} className="w-full flex flex-col gap-4 mb-6">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-widest pl-1">Email</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-slate-600 transition-all"
              placeholder="tu@correo.com"
            />
          </div>
          
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-widest pl-1">Contraseña</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-slate-600 transition-all"
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full mt-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            {isLoading ? "Procesando..." : (isRegister ? "Registrarme" : "Entrar")}
          </button>
        </form>

        {/* Divisor Visual */}
        <div className="w-full flex items-center gap-4 mb-6">
          <div className="h-px bg-white/10 flex-grow"></div>
          <span className="text-xs text-slate-500 font-semibold uppercase">o continúa con</span>
          <div className="h-px bg-white/10 flex-grow"></div>
        </div>

        {/* Google Login Button */}
        <div className="w-full flex justify-center mb-6">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setErrorMsg("Error de inicio de sesión con Google")}
            theme="filled_black"
            shape="pill"
            width="100%"
            size="large"
            text={isRegister ? "signup_with" : "continue_with"}
          />
        </div>
        
        {/* Toggle Login/Registro */}
        <p className="text-sm text-slate-400 text-center">
          {isRegister ? "¿Ya tienes cuenta?" : "¿No tienes cuenta?"}{" "}
          <button 
            type="button" 
            onClick={() => { setIsRegister(!isRegister); setErrorMsg(""); }}
            className="text-white font-bold hover:text-blue-400 transition-colors underline decoration-white/30 underline-offset-4"
          >
            {isRegister ? "Inicia sesión" : "Regístrate"}
          </button>
        </p>
      </div>
    </div>
  );
}
