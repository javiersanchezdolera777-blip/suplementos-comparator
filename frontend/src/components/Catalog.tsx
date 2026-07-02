"use client";

import { useState, useMemo, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function Catalog() {
  // Ahora usamos el estado para guardar los productos de la API
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Todas");
  const [selectedBrand, setSelectedBrand] = useState("Todas");

  // Al cargar la página, hacemos la petición real a FastAPI
  useEffect(() => {
    fetch("http://localhost:8000/api/productos")
      .then((res) => res.json())
      .then((data) => {
        setProductos(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error conectando con la API:", error);
        setLoading(false);
      });
  }, []);

  // Leemos las propiedades en ESPAÑOL (categoria.nombre, marca.nombre)
  const categories = ["Todas", ...Array.from(new Set(productos.map((p) => p.categoria?.nombre || "")))].filter(Boolean);
  const brands = ["Todas", ...Array.from(new Set(productos.map((p) => p.marca?.nombre || "")))].filter(Boolean);

  const filteredProducts = useMemo(() => {
    return productos.filter((product) => {
      const matchesSearch = product.nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.descripcion.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === "Todas" || product.categoria?.nombre === selectedCategory;
      const matchesBrand = selectedBrand === "Todas" || product.marca?.nombre === selectedBrand;

      return matchesSearch && matchesCategory && matchesBrand;
    });
  }, [searchQuery, selectedCategory, selectedBrand, productos]);

  // Pantalla de carga profesional
  if (loading) {
    return (
      <div className="w-full flex justify-center py-20">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }


  return (
    <div className="w-full">
      {/* Barra de Búsqueda y Filtros */}
      <div className="bg-[#0f172a]/60 border border-white/10 rounded-3xl p-4 sm:p-5 mb-12 backdrop-blur-2xl flex flex-col md:flex-row gap-5 items-center justify-between shadow-2xl shadow-black/50 ring-1 ring-white/5 relative z-20">

        {/* Input de Búsqueda */}
        <div className="relative w-full md:w-1/2 group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-400">
            <svg className="h-5 w-5 text-slate-400 group-focus-within:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Busca proteínas, creatinas, marcas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-12 pr-4 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white/10 transition-all placeholder:text-slate-400 font-medium text-base hover:bg-white/[0.07]"
          />
        </div>

        {/* Filtros Dropdown */}
        <div className="flex flex-col sm:flex-row w-full md:w-auto gap-4">
          <div className="flex flex-col">
            <span className="text-xs text-slate-400 mb-1.5 ml-1 font-semibold uppercase tracking-wider">Categoría</span>
            <div className="relative group">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-4 pr-10 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none min-w-[140px] cursor-pointer font-medium text-base hover:bg-white/[0.07] transition-all"
              >
                {categories.map(c => <option key={c} value={c} className="bg-slate-900">{c}</option>)}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-slate-400 group-hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
          </div>

          <div className="flex flex-col">
            <span className="text-xs text-slate-400 mb-1.5 ml-1 font-semibold uppercase tracking-wider">Marca</span>
            <div className="relative group">
              <select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-4 pr-10 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none min-w-[140px] cursor-pointer font-medium text-base hover:bg-white/[0.07] transition-all"
              >
                {brands.map(b => <option key={b} value={b} className="bg-slate-900">{b}</option>)}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-slate-400 group-hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Resultados de la búsqueda */}
      <div className="mb-6 text-slate-400 text-sm">
        Mostrando <span className="text-white font-semibold">{filteredProducts.length}</span> productos
      </div>

      {/* Grid de Productos */}
      {filteredProducts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-white/5 border border-white/10 rounded-2xl">
          <h3 className="text-2xl font-bold text-white mb-2">No se encontraron productos</h3>
          <p className="text-slate-400">Prueba a usar otros filtros o cambiar tu búsqueda.</p>
          <button
            onClick={() => { setSearchQuery(""); setSelectedCategory("Todas"); setSelectedBrand("Todas"); }}
            className="mt-6 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all shadow-lg shadow-blue-500/20 font-medium"
          >
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}
