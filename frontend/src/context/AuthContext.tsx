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
  favoriteIds: number[];
  addFavoriteId: (id: number) => void;
  removeFavoriteId: (id: number) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);

  useEffect(() => {
    setIsMounted(true);
    // Recuperar token del localStorage al cargar
    const storedToken = localStorage.getItem("suparator_token");
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  // Cargar favoritos cuando el token esté disponible
  useEffect(() => {
    if (token) {
      const fetchFavs = async () => {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
          const res = await fetch(`${apiUrl}/api/favoritos`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (res.ok) {
            const data = await res.json();
            setFavoriteIds(data.map((f: any) => f.product_id));
          }
        } catch (e) {
          console.error("Error cargando favoritos:", e);
        }
      };
      fetchFavs();
    } else {
      setFavoriteIds([]);
    }
  }, [token]);

  const addFavoriteId = (id: number) => setFavoriteIds(prev => [...prev, id]);
  const removeFavoriteId = (id: number) => setFavoriteIds(prev => prev.filter(fId => fId !== id));

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
        favoriteIds,
        addFavoriteId,
        removeFavoriteId,
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
