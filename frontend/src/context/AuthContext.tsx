"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface AuthContextType {
  token: string | null;
  isLoggedIn: boolean;
  isLoginModalOpen: boolean;
  login: (token: string) => void;
  logout: () => void;
  openLoginModal: () => void;
  closeLoginModal: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    // Recuperar token del localStorage al cargar
    const storedToken = localStorage.getItem("suparator_token");
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem("suparator_token", newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("suparator_token");
  };

  const openLoginModal = () => setIsLoginModalOpen(true);
  const closeLoginModal = () => setIsLoginModalOpen(false);

  // Evitamos hidratación incorrecta
  if (!isMounted) return null;

  return (
    <AuthContext.Provider
      value={{
        token,
        isLoggedIn: !!token,
        isLoginModalOpen,
        login,
        logout,
        openLoginModal,
        closeLoginModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider");
  }
  return context;
}
