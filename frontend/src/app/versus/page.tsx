'use client';

import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { useCompareStore } from '@/store/useCompareStore';
import { getWinnerMin, getWinnerMax } from '@/utils/compareHelpers';

export default function VersusPage() {
  const { compareIds, removeId } = useCompareStore();
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (compareIds.length === 0) {
      setProductos([]);
      return;
    }

    const fetchComparativa = async () => {
      setLoading(true);
      try {
        const idsParam = compareIds.join(',');
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/productos/comparar?ids=${idsParam}`);
        if (!res.ok) throw new Error('Error al cargar la comparativa');
        
        const data = await res.json();
        setProductos(data);
      } catch (error) {
        console.error("Error fetching compare data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchComparativa();
  }, [compareIds]);

  const bestPrice = useMemo(() => getWinnerMin(productos, 'precio_por_kg'), [productos]);
  const bestProtein = useMemo(() => getWinnerMax(productos, 'porcentaje_proteina'), [productos]);

  if (compareIds.length === 0) {
    return (
      <div className="min-h-[80vh] bg-gray-50 flex flex-col items-center justify-center p-6 text-center">
        <h1 className="text-4xl font-black text-gray-900 mb-4">Comparativa Cara a Cara ⚖️</h1>
        <p className="text-gray-500 mb-8 max-w-md">No has seleccionado ningún producto. Visita el catálogo y elige a los contendientes para ver quién es el ganador.</p>
        <Link className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/20" href="/catalogo">
          Explorar Catálogo
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8 lg:p-12">
      <div className="max-w-[1400px] mx-auto">
        <div className="mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-black text-gray-900">Comparativa Cara a Cara ⚖️</h1>
            <p className="text-gray-500 mt-2">Analiza objetivamente cuál es tu mejor opción.</p>
          </div>
          <Link className="text-sm font-bold text-blue-600 hover:text-blue-700 transition bg-blue-50 px-4 py-2 rounded-lg" href="/catalogo">
            ⬅️ Volver al catálogo
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-2xl shadow-sm border border-gray-100">
            <span className="animate-pulse text-lg font-bold text-gray-400">Preparando el cuadrilátero...</span>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-x-auto">
            <div className="min-w-[800px]">
              
              {/* CABECERA */}
              <div className="flex border-b border-gray-200 bg-gray-50/50">
                <div className="w-48 p-6 shrink-0 flex items-end">
                  <span className="font-bold text-gray-400 uppercase tracking-wider text-xs">Características</span>
                </div>
                {productos.map(prod => (
                  <div key={prod.id} className="flex-1 p-6 border-l border-gray-200 flex flex-col relative group">
                    <button 
                      onClick={() => removeId(prod.id)}
                      className="absolute top-4 right-4 text-gray-300 hover:text-red-500 transition font-black bg-white rounded-full w-8 h-8 flex items-center justify-center shadow-sm opacity-0 group-hover:opacity-100"
                      title="Eliminar de la comparativa"
                    >
                      ✕
                    </button>
                    <div className="h-32 w-full flex items-center justify-center mb-4 bg-white rounded-xl border border-gray-100 p-2">
                      <img src={prod.imagen_url} alt={prod.nombre} className="max-h-full max-w-full object-contain" />
                    </div>
                    <span className="text-[10px] text-blue-600 font-black tracking-widest uppercase mb-1">{prod.marca?.nombre || "HSN"}</span>
                    <h3 className="text-sm font-bold text-gray-900 leading-snug line-clamp-2 h-10">{prod.nombre}</h3>
                    <div className="mt-4 flex items-baseline gap-1">
                      <span className="text-2xl font-black text-gray-900">{prod.precio.toFixed(2)}</span>
                      <span className="text-gray-500 font-semibold">€</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* FILA: PRECIO POR KG */}
              <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <div className="w-48 p-4 shrink-0 border-r border-gray-100 flex items-center">
                  <span className="text-sm font-semibold text-gray-600">💰 Precio por Kg</span>
                </div>
                {productos.map(prod => {
                  const isWinner = prod.precio_por_kg === bestPrice;
                  return (
                    <div key={prod.id} className={`flex-1 p-4 border-r border-gray-100 flex items-center justify-center last:border-r-0 ${isWinner ? 'bg-blue-50/50' : ''}`}>
                      <span className={`text-sm ${isWinner ? 'font-black text-blue-700' : 'font-medium text-gray-600'}`}>
                        {isWinner && <span className="mr-1">✨</span>}
                        {prod.precio_por_kg ? `${prod.precio_por_kg.toFixed(2)} €` : '-'}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* FILA: PROTEÍNA */}
              <div className="flex border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <div className="w-48 p-4 shrink-0 border-r border-gray-100 flex items-center">
                  <span className="text-sm font-semibold text-gray-600">🥩 Proteína</span>
                </div>
                {productos.map(prod => {
                  const isWinner = prod.porcentaje_proteina === bestProtein && prod.porcentaje_proteina > 0;
                  return (
                    <div key={prod.id} className={`flex-1 p-4 border-r border-gray-100 flex items-center justify-center last:border-r-0 ${isWinner ? 'bg-blue-50/50' : ''}`}>
                      <span className={`text-sm ${isWinner ? 'font-black text-blue-700' : 'font-medium text-gray-600'}`}>
                        {isWinner && <span className="mr-1">✨</span>}
                        {prod.porcentaje_proteina ? `${prod.porcentaje_proteina}%` : '-'}
                      </span>
                    </div>
                  );
                })}
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}
