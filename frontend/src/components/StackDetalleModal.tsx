"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Props {
  stack: any;
  isOpen: boolean;
  onClose: () => void;
  esMio: boolean; // Para saber si mostramos los botones de añadir
}

export default function StackDetalleModal({ stack, isOpen, onClose, esMio }: Props) {
  const router = useRouter();
  const [mostrarCategorias, setMostrarCategorias] = useState(false);

  if (!isOpen || !stack) return null;

  // Categorías de ejemplo de tu BBDD
  const categorias = [
    { id: 'proteina', nombre: '🥩 Proteína', color: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200' },
    { id: 'creatina', nombre: '⚡ Creatina', color: 'bg-purple-50 text-purple-700 hover:bg-purple-100 border-purple-200' },
    { id: 'pre-entreno', nombre: '🔥 Pre-Entreno', color: 'bg-orange-50 text-orange-700 hover:bg-orange-100 border-orange-200' },
    { id: 'vitaminas', nombre: '💊 Vitaminas', color: 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200' },
    { id: 'aminoacidos', nombre: '🧬 Aminoácidos', color: 'bg-teal-50 text-teal-700 hover:bg-teal-100 border-teal-200' },
  ];

  const irACatalogoFiltrado = (categoriaId: string) => {
    // Te lleva a la página principal (donde está el catálogo de Javi) con el filtro y anclado al catálogo
    router.push(`/?categoria=${categoriaId}#catalogo`);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-fade-in-up max-h-[90vh] flex flex-col">
        
        {/* Cabecera */}
        <div className="bg-slate-50 p-5 border-b border-gray-100 flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-black text-slate-800">{stack.nombre}</h2>
            {stack.descripcion && <p className="text-gray-500 mt-1 text-sm">{stack.descripcion}</p>}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-slate-800 text-3xl leading-none">&times;</button>
        </div>

        {/* Lista de Productos (El contenido escroleable) */}
        <div className="p-5 flex-1 overflow-y-auto bg-white">
          <h3 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
            📦 Productos en esta rutina
            <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-xs">{stack.productos?.length || 0}</span>
          </h3>

          {!stack.productos || stack.productos.length === 0 ? (
            <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
              <span className="text-4xl mb-3 block">📭</span>
              <p className="text-gray-500 font-medium">Esta rutina está vacía.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {stack.productos.map((prod: any, index: number) => (
                <div key={index} className="flex items-center gap-4 p-3 border border-gray-100 rounded-xl hover:shadow-sm transition-shadow">
                  {/* Aquí iría la imagen del producto, ponemos un placeholder de momento */}
                  <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                    🧴
                  </div>
                  <div>
                    <p className="font-bold text-slate-800">{prod.nombre}</p>
                    <p className="text-sm text-gray-500">{prod.marca || 'Marca Desconocida'}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer de Acciones (SOLO SI ES TU PERFIL) */}
        {esMio && (
          <div className="p-5 border-t border-gray-100 bg-slate-50">
            {!mostrarCategorias ? (
              <button 
                onClick={() => setMostrarCategorias(true)}
                className="w-full bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2"
              >
                <span>➕</span> Añadir producto a este Stack
              </button>
            ) : (
              <div className="animate-fade-in-up">
                <div className="flex justify-between items-center mb-3">
                  <p className="text-sm font-bold text-slate-700">¿Qué estás buscando?</p>
                  <button onClick={() => setMostrarCategorias(false)} className="text-xs text-gray-500 hover:text-red-500 font-medium">Cancelar</button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {categorias.map(cat => (
                    <button
                      key={cat.id}
                      onClick={() => irACatalogoFiltrado(cat.id)}
                      className={`px-3 py-2 rounded-lg border text-sm font-bold transition-all transform hover:-translate-y-0.5 ${cat.color}`}
                    >
                      {cat.nombre}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}