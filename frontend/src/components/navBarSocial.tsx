"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import NotificacionesDropdown from './NotificacionesDropdown';

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
    {
      name: 'Catálogo',
      path: '/',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      )
    },
    {
      name: 'Buscar Atletas',
      path: '/comunidad',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )
    },
    {
      name: 'Mi Perfil',
      path: '/mi-zona',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      )
    },
  ];

  return (
    <div className="flex justify-center mb-8 relative z-50">
      <nav className="inline-flex bg-white/80 backdrop-blur-md border border-slate-200/60 rounded-2xl p-1.5 shadow-sm">
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <Link
              key={item.name}
              href={item.path}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${active
                  ? 'bg-slate-900 text-white shadow-md shadow-slate-900/20'
                  : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100/50'
                }`}
            >
              <span className={`${active ? 'text-white' : 'text-slate-400'}`}>{item.icon}</span>
              <span className="hidden sm:block">{item.name}</span>
            </Link>
          );
        })}

        <div className="flex items-center ml-2 pl-2 border-l border-slate-200">
          <NotificacionesDropdown />
        </div>
      </nav>
    </div>
  );
}