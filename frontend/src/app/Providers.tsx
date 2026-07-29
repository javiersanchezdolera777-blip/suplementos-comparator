"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "../context/AuthContext";
import LoginModal from "../components/LoginModal";

export default function Providers({ children }: { children: React.ReactNode }) {
  // El Client ID de Google configurado por Diego
  const clientId = "318282148406-908hoi15scu4vcc8v9lhqfkislin10cb.apps.googleusercontent.com";

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        {children}
        <LoginModal /> {/* Renderizamos el modal globalmente aquí */}
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}
