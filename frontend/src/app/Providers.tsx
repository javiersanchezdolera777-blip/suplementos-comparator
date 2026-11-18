"use client";

import { AuthProvider } from "../context/AuthContext";
import LoginModal from "../components/LoginModal";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <LoginModal /> {/* Renderizamos el modal globalmente aquí */}
    </AuthProvider>
  );
}