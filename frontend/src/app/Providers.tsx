"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "../context/AuthContext";
import LoginModal from "../components/LoginModal";

export default function Providers({ children }: { children: React.ReactNode }) {
  // 🔒 Cargamos el Client ID desde las variables de entorno de forma segura
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        {children}
        <LoginModal /> {/* Renderizamos el modal globalmente aquí */}
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}