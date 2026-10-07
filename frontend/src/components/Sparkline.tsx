import React from 'react';

interface PricePoint {
  precio: number;
  fecha: string;
}

interface SparklineProps {
  data: PricePoint[];
  width?: number;
  height?: number;
  color?: string;
}

export default function Sparkline({ data, width = 100, height = 30, color = "#2563eb" }: SparklineProps) {
  if (!data || data.length < 2) return null;

  const minPrice = Math.min(...data.map(d => d.precio));
  const maxPrice = Math.max(...data.map(d => d.precio));
  const rangeY = maxPrice - minPrice || 1;

  const paddedMinPrice = minPrice - rangeY * 0.1;
  const paddedMaxPrice = maxPrice + rangeY * 0.1;
  const paddedRangeY = paddedMaxPrice - paddedMinPrice;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((d.precio - paddedMinPrice) / paddedRangeY) * height;
    return `${x},${y}`;
  }).join(' ');

  const lastPointY = height - ((data[data.length - 1].precio - paddedMinPrice) / paddedRangeY) * height;

  return (
    <div className="flex flex-col items-center sm:items-end justify-center">
      <svg width={width} height={height} className="overflow-visible drop-shadow-sm">
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        <circle
          cx={width}
          cy={lastPointY}
          r="3"
          fill={color}
          className="animate-pulse"
        />
      </svg>
      <span className="text-[9px] text-slate-400 mt-1 uppercase tracking-widest font-bold hidden sm:block">Historial</span>
    </div>
  );
}
