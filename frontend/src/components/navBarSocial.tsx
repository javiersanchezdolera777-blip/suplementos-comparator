"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function NavbarSocial() {
  const pathname = usePathname();

  // Función para saber si un botón está activo
  const isActive = (path: string) => {
    if (path === '/comunidad' && pathname.startsWith('/comunidad')) return true;
    if (path === '/mi-zona' && pathname.startsWith('/mi-zona')) return true;
    if (path === '/' && pathname === '/') return true;
    return false;
  };

  const navItems = [
    { name: 'Tienda', path: '/', icon: '🏪' },
    { name: 'Comunidad', path: '/comunidad', icon: '🌍' },
    { name: 'Mi Zona', path: '/mi-zona', icon: '👤' },
    // Dejo este preparado para cuando hagamos el Ranking:
    // { name: 'Ranking', path: '/comunidad/ranking', icon: '🏆' } 
  ];

  return (
    <div className="flex justify-center mb-8">
      <nav className="inline-flex bg-white border border-slate-200 rounded-full p-1.5 shadow-sm">
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <Link 
              key={item.name} 
              href={item.path}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold transition-all duration-200 ${
                active 
                  ? 'bg-slate-900 text-white shadow-md' 
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <span className="text-lg leading-none">{item.icon}</span>
              <span className="hidden sm:block">{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}