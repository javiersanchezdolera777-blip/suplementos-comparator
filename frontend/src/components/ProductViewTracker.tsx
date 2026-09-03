"use client";

import { useEffect } from 'react';

export default function ProductViewTracker({ productId }: { productId: number }) {
  useEffect(() => {
    const trackView = async () => {
      try {
        // Obtenemos el token de donde lo tengas guardado (ajusta la key si se llama distinto)
        const token = localStorage.getItem('access_token') || localStorage.getItem('suparator_token');
        if (!token) return;

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        await fetch(`${apiUrl}/api/historial/${productId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
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
