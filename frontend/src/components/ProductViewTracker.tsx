"use client";

import { useEffect } from 'react';

export default function ProductViewTracker({ productId }: { productId: number }) {
  useEffect(() => {
    const trackView = async () => {
      try {
        // La validación se hace por cookie HttpOnly, ya no necesitamos extraer del localStorage
        const token = "dummy"; // Dummy fallback to avoid refactoring entire effect logic if not strictly needed. Wait, actually I can just use checkAuth or assume user is logged in
        // However, I can just remove token usage.

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        await fetch(`${apiUrl}/api/historial/${productId}`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });
      } catch (error) {
        // Discreto, si falla no hacemos ruido en la UI
        console.error("Tracking silencioso falló:", error);
      }
    };

    if (productId) {
      trackView();
    }
  }, [productId]);

  return null;
}
