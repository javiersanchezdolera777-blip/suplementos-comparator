"use client";

import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function Catalog() {
  // Estados para los productos traídos de la API
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Estados dinámicos de los filtros
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Todas");
  const [selectedBrand, setSelectedBrand] = useState("Todas");
  const [ordenPrecio, setOrdenPrecio] = useState(""); // Nuevo filtro: 'asc' o 'desc'

  // Estados para rellenar los desplegables dinámicamente desde la API de Diego
  const [categories, setCategories] = useState<string[]>(["Todas"]);
  const [brands, setBrands] = useState<string[]>(["Todas"]);

  // URL base controlada. Si estás en local sin .env, apunta a tu puerto por defecto
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // 1. CARGA DE FILTROS CONFIGURADOS (Solo se ejecuta una vez al montar la página)
  useEffect(() => {
    fetch(`${apiUrl}/api/config/filtros`)
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        // Asumiendo que Diego devuelve las listas de nombres en un diccionario
        if (data.categories) {
          setCategories(["Todas", ...data.categories]);
        }
        
        if (data.brands) {
          setBrands(["Todas", ...data.brands]);
        }
      })
      .catch((error) => {
        console.error("Error cargando los diccionarios de filtros:", error);
      });
  }, [apiUrl]);

  // 2. PETICIÓN DINÁMICA DE PRODUCTOS AL BACKEND (Se ejecuta cuando cambia cualquier filtro)
  useEffect(() => {
    setLoading(true);

    // Construimos los parámetros de la URL para la API de Diego
    const queryParams = new URLSearchParams();
    if (searchQuery) queryParams.append("busqueda", searchQuery);
    if (selectedCategory !== "Todas") queryParams.append("categoria", selectedCategory);
    if (selectedBrand !== "Todas") queryParams.append("marca", selectedBrand);
    if (ordenPrecio) queryParams.append("orden_precio", ordenPrecio);

    fetch(`${apiUrl}/api/productos?${queryParams.toString()}`)
      .then((res) => {
        if (!res.ok) throw new Error("Error en la respuesta del servidor");
        return res.json();
      })
      .then((data) => {
        // Mantenemos tu control de flujo por si el backend devuelve array o objeto con .productos
        setProductos(Array.isArray(data) ? data : data.productos || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error conectando con la API de Suparator:", error);
        setLoading(false);
      });

    // Añadimos un pequeño debounce nativo a la búsqueda de texto para no saturar a Render en cada letra
    // (Opcional, pero recomendado si notas latencia en el backend gratuito)
  }, [searchQuery, selectedCategory, selectedBrand, ordenPrecio, apiUrl]);


  return (
    <div className="w-full">
      {/* Barra de Búsqueda y Filtros */}
      <div className="bg-[#0f172a]/60 border border-white/10 rounded-3xl p-4 sm:p-5 mb-12 backdrop-blur-2xl flex flex-col md:flex-row gap-5 items-center justify-between shadow-2xl shadow-black/50 ring-1 ring-white/5 relative z-20">

        {/* Input de Búsqueda */}
        <div className="relative w-full md:w-1/3 group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-400">
            <svg className="h-5 w-5 text-slate-400 group-focus-within:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Busca proteínas, creatinas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-12 pr-4 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white/10 transition-all placeholder:text-slate-400 font-medium text-base hover:bg-white/[0.07]"
          />
        </div>

        {/* Filtros Dropdown */}
        <div className="flex flex-col sm:flex-row w-full md:w-auto gap-4 flex-wrap justify-end">

          {/* Filtro Categoría */}
          <div className="flex flex-col flex-1 sm:flex-none">
            <span className="text-xs text-slate-400 mb-1.5 ml-1 font-semibold uppercase tracking-wider">Categoría</span>
            <div className="relative group">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-4 pr-10 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none min-w-[150px] cursor-pointer font-medium text-base hover:bg-white/[0.07] transition-all"
              >
                {categories.map(c => <option key={c} value={c} className="bg-slate-900">{c}</option>)}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-slate-400 group-hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
          </div>

          {/* Filtro Marca */}
          <div className="flex flex-col flex-1 sm:flex-none">
            <span className="text-xs text-slate-400 mb-1.5 ml-1 font-semibold uppercase tracking-wider">Marca</span>
            <div className="relative group">
              <select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-4 pr-10 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none min-w-[150px] cursor-pointer font-medium text-base hover:bg-white/[0.07] transition-all"
              >
                {brands.map(b => <option key={b} value={b} className="bg-slate-900">{b}</option>)}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-slate-400 group-hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
          </div>

          {/* NUEVO: Ordenación por Precio */}
          <div className="flex flex-col flex-1 sm:flex-none">
            <span className="text-xs text-slate-400 mb-1.5 ml-1 font-semibold uppercase tracking-wider">Precio</span>
            <div className="relative group">
              <select
                value={ordenPrecio}
                onChange={(e) => setOrdenPrecio(e.target.value)}
                className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-4 pr-10 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none min-w-[160px] cursor-pointer font-medium text-base hover:bg-white/[0.07] transition-all"
              >
                <option value="" className="bg-slate-900">Relevancia</option>
                <option value="asc" className="bg-slate-900">Menor a Mayor</option>
                <option value="desc" className="bg-slate-900">Mayor a Menor</option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-slate-400 group-hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Nuevo Skeleton Loader Premium */}
      {loading ? (
        <div className="w-full mt-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex flex-col bg-[#0a0f1d]/50 border border-white/5 rounded-3xl overflow-hidden h-[420px] animate-pulse">
                <div className="h-[220px] bg-white/5"></div>
                <div className="p-6 flex flex-col flex-grow">
                  <div className="h-3 w-1/4 bg-white/5 rounded mb-3"></div>
                  <div className="h-6 w-3/4 bg-white/10 rounded mb-4"></div>
                  <div className="h-4 w-full bg-white/5 rounded mb-2"></div>
                  <div className="h-4 w-5/6 bg-white/5 rounded mb-8"></div>
                  <div className="mt-auto flex justify-between items-end">
                    <div className="h-8 w-20 bg-white/5 rounded"></div>
                    <div className="h-10 w-28 bg-white/10 rounded-xl"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {/* Resultados de la búsqueda */}
          <div className="mb-6 text-slate-400 text-sm">
            Mostrando <span className="text-white font-semibold">{productos.length}</span> productos
          </div>

          {/* Grid de Productos */}
          {productos.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {productos.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 bg-white/5 border border-white/10 rounded-2xl">
              <h3 className="text-2xl font-bold text-white mb-2">No se encontraron productos</h3>
              <p className="text-slate-400">Prueba a usar otros filtros o cambiar tu búsqueda.</p>
              <button
                onClick={() => { setSearchQuery(""); setSelectedCategory("Todas"); setSelectedBrand("Todas"); setOrdenPrecio(""); }}
                className="mt-6 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all shadow-lg shadow-blue-500/20 font-medium"
              >
                Limpiar filtros
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}