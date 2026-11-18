"use client";

import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function ProductViewTracker({ productId }: { productId: number }) {
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    // Solo registramos la vista si el usuario está autenticado.
    // El endpoint /api/historial/{id} requiere sesión; no disparamos
    // la petición a usuarios anónimos para evitar el 401 innecesario.
    if (!productId || !isLoggedIn) return;

    const trackView = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        await fetch(`${apiUrl}/api/historial/${productId}`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });
      } catch (error) {
        // Silencioso: si falla no afecta a la UI
      }
    };

    trackView();
  }, [productId, isLoggedIn]);

  return null;
}
