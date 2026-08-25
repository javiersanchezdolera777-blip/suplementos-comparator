import React from 'react';
import Image from 'next/image';

// Le decimos a React qué datos va a recibir este componente desde el backend
interface Props {
  xpTotales: number;
  objetivo: string; // "Volumen" o "Definición"
}

export default function GymMascota({ xpTotales, objetivo }: Props) {
  // 1. Calculamos el Nivel basado en los XP
  let nivel = 1;
  if (xpTotales >= 1000) nivel = 3;
  else if (xpTotales >= 200) nivel = 2;

  // 2. Elegimos la imagen correcta según el objetivo y el nivel
  let imagenSrc = '/mascotas/flaco.png';
  
  if (objetivo === 'Volumen') {
    if (nivel === 1) imagenSrc = '/mascotas/flaco.png';
    if (nivel === 2) imagenSrc = '/mascotas/atletico.png';
    if (nivel === 3) imagenSrc = '/mascotas/monstruo.png';
  } else if (objetivo === 'Definición') {
    if (nivel === 1) imagenSrc = '/mascotas/gordito.png';
    if (nivel === 2) imagenSrc = '/mascotas/atletico.png';
    if (nivel === 3) imagenSrc = '/mascotas/monstruo.png';
  }

  // 3. Calculamos el porcentaje para la barra de progreso (máximo 1000 XP)
  const porcentaje = Math.min((xpTotales / 1000) * 100, 100);

  // 4. Renderizamos el diseño en pantalla
  return (
    <div className="flex flex-col items-center p-6 bg-white border border-gray-200 rounded-2xl shadow-sm w-full max-w-sm">
      {/* Título de la Mascota y el Icono de Información */}
      <div className="flex items-center justify-center gap-2 mb-4">
        <h3 className="text-xl font-bold text-slate-800">
          Tu Progreso Físico
        </h3>
        
        {/* --- EL TOOLTIP MÁGICO --- */}
        <div className="group relative inline-flex items-center justify-center cursor-help">
          <span className="text-gray-400 hover:text-blue-500 transition-colors">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </span>
          
          {/* La cajita negra que aparece al hacer hover */}
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-slate-900 text-white text-xs text-center rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 shadow-xl z-50 pointer-events-none">
            Completa checks diarios para obtener experiencia y que tu personaje evolucione hasta alcanzar el Olympia. 🏆
            {/* Flechita hacia abajo */}
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900"></div>
          </div>
        </div>
        {/* --------------------------- */}
      </div>
      
      {/* Contenedor de la Imagen */}
      <div className="relative w-32 h-32 mb-4">
        <Image 
          src={imagenSrc} 
          alt="Tu mascota del gym" 
          fill
          style={{ objectFit: 'contain' }}
        />
      </div>

      <p className="text-lg font-semibold text-blue-600">Nivel {nivel}</p>

      {/* Barra de Progreso */}
      <div className="w-full bg-gray-200 rounded-full h-3 mt-3">
        <div 
          className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out" 
          style={{ width: `${porcentaje}%` }}
        ></div>
      </div>
      
      <p className="text-sm text-gray-500 mt-2 font-medium">
        {xpTotales} / 1000 XP
      </p>
    </div>
  );
}