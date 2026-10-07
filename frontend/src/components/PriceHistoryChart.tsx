"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

type HistorialPrecio = {
  fecha: string;
  precio: number;
};

type Oferta = {
  tienda?: string;
  activo?: boolean;
  precio?: number;
  historial_precios?: HistorialPrecio[];
};

interface Props {
  ofertas: Oferta[];
  compact?: boolean;
}

const COLORS = [
  "#3b82f6", // blue-500
  "#ef4444", // red-500
  "#10b981", // emerald-500
  "#f59e0b", // amber-500
  "#8b5cf6", // violet-500
  "#ec4899", // pink-500
  "#14b8a6", // teal-500
];

export default function PriceHistoryChart({ ofertas, compact = false }: Props) {
  const [mounted, setMounted] = useState(false);
  const [range, setRange] = useState<"3m" | "1y">("3m");

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, percentageChange } = useMemo(() => {
    // Collect all unique dates and sort them
    const now = new Date();
    const startDate = new Date();
    if (range === "3m") {
      startDate.setMonth(now.getMonth() - 3);
    } else {
      startDate.setFullYear(now.getFullYear() - 1);
    }

    const dateMap = new Map<string, any>();
    const storesSet = new Set<string>();

    ofertas.forEach((oferta) => {
      if (!oferta.historial_precios || oferta.historial_precios.length === 0 || !oferta.tienda) return;
      
      const tienda = oferta.tienda;
      storesSet.add(tienda);
      
      oferta.historial_precios.forEach((hp) => {
        const d = new Date(hp.fecha);
        if (d >= startDate && d <= now) {
          // Format date as YYYY-MM-DD
          const dateStr = d.toISOString().split("T")[0];
          
          if (!dateMap.has(dateStr)) {
            dateMap.set(dateStr, { name: dateStr, timestamp: d.getTime() });
          }
          const entry = dateMap.get(dateStr);
          // If multiple points in a day for the same store, keep the lowest
          if (entry[tienda] === undefined || hp.precio < entry[tienda]) {
            entry[tienda] = hp.precio;
          }
        }
      });
    });

    // If a store is missing a price for a specific date, we want to forward-fill it 
    // or just let Recharts connect the nulls (connectNulls={true})
    const sortedData = Array.from(dateMap.values()).sort((a, b) => a.timestamp - b.timestamp);

    // Calculate percentage change based on the lowest available price at the start vs end
    let pctChange = null;
    if (sortedData.length >= 2) {
      const firstEntry = sortedData[0];
      const lastEntry = sortedData[sortedData.length - 1];

      const getMinPrice = (entry: any) => {
        let min = Infinity;
        storesSet.forEach(store => {
          if (entry[store] !== undefined && entry[store] < min) {
            min = entry[store];
          }
        });
        return min === Infinity ? null : min;
      };

      const p1 = getMinPrice(firstEntry);
      const p2 = getMinPrice(lastEntry);

      if (p1 !== null && p2 !== null && p1 > 0) {
        pctChange = ((p2 - p1) / p1) * 100;
      }
    }

    // Format dates for display based on range
    const displayData = sortedData.map(d => {
      const dateObj = new Date(d.timestamp);
      // For 1 year, we might want just "Jan 25", for 3 months "15 Jan"
      const formattedName = dateObj.toLocaleDateString('es-ES', { 
        day: range === '3m' ? 'numeric' : undefined,
        month: 'short', 
        year: range === '1y' ? '2-digit' : undefined 
      });
      return { ...d, displayDate: formattedName };
    });

    return { 
      data: displayData, 
      stores: Array.from(storesSet),
      percentageChange: pctChange 
    };
  }, [ofertas, range]);

  if (!data || data.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-400 h-64">
        <svg className="w-8 h-8 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
        <p className="font-medium">No hay suficientes datos de historial</p>
      </div>
    );
  }

  if (!mounted) {
    return <div className={`w-full animate-pulse ${compact ? 'h-32 bg-transparent' : 'h-72 bg-white border border-slate-200 rounded-3xl'}`}></div>;
  }

  return (
    <div className={`${compact ? 'bg-transparent p-0' : 'bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm'}`} id="historial-precios">
      <div className={`flex justify-between items-center ${compact ? 'mb-1' : 'mb-8 flex-col sm:flex-row items-start sm:items-center gap-4'}`}>
        {!compact && (
          <div>
            <h3 className="text-xl font-black text-slate-900 tracking-tight">Historial de precios</h3>
            {percentageChange !== null && (
              <div className="mt-1 flex items-center gap-2">
                <span className={`text-sm font-bold px-2.5 py-1 rounded-lg ${percentageChange > 0 ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600'}`}>
                  {percentageChange > 0 ? '+' : ''}{percentageChange.toFixed(1)}%
                </span>
                <span className="text-sm font-medium text-slate-500">
                  rendimiento en este periodo
                </span>
              </div>
            )}
          </div>
        )}
        
        <div className={`flex bg-slate-100 p-1 rounded-xl ${compact ? 'mx-auto' : ''}`}>
          <button
            onClick={() => setRange("3m")}
            className={`px-3 py-1 ${compact ? 'text-xs' : 'text-sm'} font-bold rounded-lg transition-all ${
              range === "3m" 
                ? "bg-white text-slate-900 shadow-sm" 
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            3 Meses
          </button>
          <button
            onClick={() => setRange("1y")}
            className={`px-3 py-1 ${compact ? 'text-xs' : 'text-sm'} font-bold rounded-lg transition-all ${
              range === "1y" 
                ? "bg-white text-slate-900 shadow-sm" 
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            1 Año
          </button>
        </div>
      </div>

      <div className={`${compact ? 'h-32' : 'h-72'} w-full`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis 
              dataKey="displayDate" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: '#64748b' }}
              dy={10}
              minTickGap={30}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickFormatter={(value) => `${value}€`}
              domain={['auto', 'auto']}
            />
            <Tooltip 
              contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              itemStyle={{ fontWeight: 600 }}
              labelStyle={{ color: '#64748b', marginBottom: '4px', fontWeight: 500 }}
            />
            <Legend 
              iconType="circle"
              wrapperStyle={{ paddingTop: compact ? '0px' : '20px', fontSize: compact ? '10px' : '12px' }}
            />
            {data && data.length > 0 && Object.keys(data[0]).filter(k => k !== 'name' && k !== 'timestamp' && k !== 'displayDate').map((store, index) => (
              <Line
                key={store}
                type="monotone"
                dataKey={store}
                name={store}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={compact ? 2 : 3}
                dot={{ r: compact ? 2 : 4, strokeWidth: compact ? 1 : 2, fill: '#fff' }}
                activeDot={{ r: compact ? 4 : 6, strokeWidth: 0 }}
                connectNulls={true}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
