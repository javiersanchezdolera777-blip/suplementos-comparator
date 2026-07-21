"use client";

import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../context/AuthContext";

export default function LoginModal() {
  const { isLoginModalOpen, closeLoginModal, login } = useAuth();

  if (!isLoginModalOpen) return null;

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      const res = await fetch(`${apiUrl}/api/auth/google`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: credentialResponse.credential }),
      });

      if (res.ok) {
        const data = await res.json();
        login(data.access_token); // Guardamos el JWT de Diego
        closeLoginModal(); // Cerramos el modal tras éxito
      } else {
        console.error("Fallo al autenticar en el backend");
      }
    } catch (error) {
      console.error("Error conectando con la API de autenticación:", error);
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
        <div className="w-16 h-16 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        
        <h2 className="text-2xl font-black text-white mb-2 text-center">Inicia sesión</h2>
        <p className="text-slate-400 text-sm text-center mb-8 px-4">
          Guarda tus suplementos favoritos y monitoriza sus precios.
        </p>

        {/* Google Login Button */}
        <div className="w-full flex justify-center mb-4">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => {
              console.log('Error de inicio de sesión con Google');
            }}
            theme="filled_black"
            shape="pill"
            size="large"
            text="continue_with"
          />
        </div>
        
        <p className="text-xs text-slate-500 text-center mt-6">
          Al continuar, aceptas nuestros Términos de Servicio y la Política de Privacidad.
        </p>
      </div>
    </div>
  );
}
