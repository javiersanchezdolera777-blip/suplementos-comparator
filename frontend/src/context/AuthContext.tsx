"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface AuthContextType {
  user: any | null;
  isLoggedIn: boolean;
  authChecked: boolean;
  isLoginModalOpen: boolean;
  checkAuth: () => Promise<void>;
  logout: () => void;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  favoriteIds: number[];
  addFavoriteId: (id: number) => void;
  removeFavoriteId: (id: number) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const checkAuth = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/auth/me`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (e) {
      setUser(null);
    } finally {
      setAuthChecked(true);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  // Cargar favoritos cuando el usuario esté disponible
  useEffect(() => {
    if (user) {
      const fetchFavs = async () => {
        try {
          const res = await fetch(`${apiUrl}/api/favoritos`, {
            credentials: 'include'
          });
          if (res.ok) {
            const data = await res.json();
            setFavoriteIds(data.map((f: any) => f.producto_id));
          }
        } catch (e) {
          console.error("Error cargando favoritos:", e);
        }
      };
      fetchFavs();
    } else {
      setFavoriteIds([]);
    }
  }, [user]);

  const addFavoriteId = (id: number) => setFavoriteIds(prev => [...prev, id]);
  const removeFavoriteId = (id: number) => setFavoriteIds(prev => prev.filter(fId => fId !== id));

  const logout = async () => {
    try {
      await fetch(`${apiUrl}/api/logout`, { method: 'POST', credentials: 'include' });
    } catch (e) {
      console.error(e);
    }
    setUser(null);
    setAuthChecked(false);
  };

  const openLoginModal = () => setIsLoginModalOpen(true);
  const closeLoginModal = () => setIsLoginModalOpen(false);

  // Evitamos hidratación incorrecta hasta que Auth se verifique
  if (!authChecked) return null;

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoggedIn: !!user,
        authChecked,
        isLoginModalOpen,
        checkAuth,
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
