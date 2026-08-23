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
      <h3 className="text-xl font-bold text-slate-800 mb-2">Tu Progreso Físico</h3>
      
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