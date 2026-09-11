"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';

interface Notificacion {
  id: number;
  tipo: string;
  mensaje: string;
  leida: boolean;
  fecha: string;
}

// Sacar la URL fuera del componente para que sea estable
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function NotificacionesDropdown() {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // useCallback para que el useEffect de polling no re-cree el intervalo en cada render
  const fetchNotificaciones = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/comunidad/notificaciones`, {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setNotificaciones(data);
        setError(false);
      } else if (res.status === 401) {
        // Usuario no logueado — no es un error, simplemente no hay notificaciones
        setNotificaciones([]);
      }
    } catch (err) {
      // Fallo de red — no mostrar error en UI, simplemente no actualizar
      setError(true);
    }
  }, []); // Sin dependencias: API_URL es constante de módulo

  const marcarComoLeidas = useCallback(async () => {
    try {
      await fetch(`${API_URL}/api/comunidad/notificaciones/marcar-leidas`, {
        method: "POST",
        credentials: 'include'
      });
      setNotificaciones(prev => prev.map(n => ({ ...n, leida: true })));
    } catch {
      // Fallo silencioso — el estado visual ya se actualizó optimistamente
    }
  }, []);

  useEffect(() => {
    fetchNotificaciones();
    const interval = setInterval(fetchNotificaciones, 30000);
    return () => clearInterval(interval);
  }, [fetchNotificaciones]); // Ahora fetchNotificaciones está en las deps, correctamente

  // Cerrar al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleDropdown = () => {
    const newIsOpen = !isOpen;
    setIsOpen(newIsOpen);
    if (newIsOpen && noLeidas > 0) {
      marcarComoLeidas();
    }
  };

  const noLeidas = notificaciones.filter(n => !n.leida).length;

  // Si hay error de conexión, no renderizar el componente para no confundir al usuario
  if (error && notificaciones.length === 0) {
    return null;
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={toggleDropdown}
        className="relative p-2 text-slate-500 hover:text-slate-900 transition-colors rounded-full hover:bg-slate-100 focus:outline-none"
        aria-label={`Notificaciones${noLeidas > 0 ? ` (${noLeidas} sin leer)` : ''}`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {noLeidas > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-red-500 rounded-full">
            {noLeidas > 9 ? '9+' : noLeidas}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-slate-100 z-50 overflow-hidden">
          <div className="bg-slate-50 px-4 py-3 border-b border-slate-100 flex justify-between items-center">
            <h3 className="font-bold text-slate-800">Notificaciones</h3>
            {noLeidas > 0 && (
              <span className="text-xs text-slate-500">{noLeidas} sin leer</span>
            )}
          </div>

          <div className="max-h-[400px] overflow-y-auto">
            {notificaciones.length === 0 ? (
              <div className="p-6 text-center text-slate-500 text-sm">
                No tienes notificaciones por ahora.
              </div>
            ) : (
              <div className="divide-y divide-slate-50">
                {notificaciones.map(notif => (
                  <div
                    key={notif.id}
                    className={`p-4 transition-colors ${notif.leida ? 'bg-white' : 'bg-blue-50/50'}`}
                  >
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 mt-1 text-lg">
                        {notif.tipo === 'nuevo_seguidor' ? '👋' : 
                         notif.tipo === 'like_stack' ? '❤️' : '🔔'}
                      </div>
                      <div>
                        <p className={`text-sm ${notif.leida ? 'text-slate-600' : 'text-slate-900 font-medium'}`}>
                          {notif.mensaje}
                        </p>
                        <p className="text-xs text-slate-400 mt-1">
                          {new Date(notif.fecha).toLocaleDateString('es-ES', {
                            day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
