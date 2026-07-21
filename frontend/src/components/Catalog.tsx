"use client";

import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function Catalog() {
  // Estados para los productos traídos de la API
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Estados de interfaz
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Estados dinámicos de los filtros (Valores seleccionados)
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Todas");
  const [selectedBrand, setSelectedBrand] = useState("Todas");
  const [ordenPrecio, setOrdenPrecio] = useState("");
  
  const [selectedFormat, setSelectedFormat] = useState("Todos");
  const [selectedFlavor, setSelectedFlavor] = useState("Todos");
  const [selectedGoal, setSelectedGoal] = useState("Todos");
  const [selectedQualitySeal, setSelectedQualitySeal] = useState("Todos");
  const [selectedProteinType, setSelectedProteinType] = useState("Todos");
  const [selectedCreatineType, setSelectedCreatineType] = useState("Todos");
  const [selectedVitaminType, setSelectedVitaminType] = useState("Todos");
  const [selectedAminoProfile, setSelectedAminoProfile] = useState("Todos");
  const [isVegan, setIsVegan] = useState<boolean | null>(null);

  // Estados para rellenar los desplegables dinámicamente desde la API
  const [categories, setCategories] = useState<string[]>(["Todas"]);
  const [brands, setBrands] = useState<string[]>(["Todas"]);
  const [formats, setFormats] = useState<string[]>(["Todos"]);
  const [flavors, setFlavors] = useState<string[]>(["Todos"]);
  const [goals, setGoals] = useState<string[]>(["Todos"]);
  const [qualitySeals, setQualitySeals] = useState<string[]>(["Todos"]);
  const [proteinTypes, setProteinTypes] = useState<string[]>(["Todos"]);
  const [creatineTypes, setCreatineTypes] = useState<string[]>(["Todos"]);
  const [vitaminTypes, setVitaminTypes] = useState<string[]>(["Todos"]);
  const [aminoProfiles, setAminoProfiles] = useState<string[]>(["Todos"]);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // 1. CARGA DE FILTROS CONFIGURADOS
  useEffect(() => {
    fetch(`${apiUrl}/api/config/filtros`)
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        if (data.categories) setCategories(["Todas", ...data.categories]);
        if (data.brands) setBrands(["Todas", ...data.brands]);
        if (data.formats) setFormats(["Todos", ...data.formats]);
        if (data.flavors) setFlavors(["Todos", ...data.flavors]);
        if (data.goals) setGoals(["Todos", ...data.goals]);
        if (data.quality_seals) setQualitySeals(["Todos", ...data.quality_seals]);
        if (data.protein_types) setProteinTypes(["Todos", ...data.protein_types]);
        if (data.creatine_types) setCreatineTypes(["Todos", ...data.creatine_types]);
        if (data.vitamin_types) setVitaminTypes(["Todos", ...data.vitamin_types]);
        if (data.amino_profiles) setAminoProfiles(["Todos", ...data.amino_profiles]);
      })
      .catch((error) => console.error("Error cargando filtros:", error));
  }, [apiUrl]);

  // Cuando cambie la categoría, reseteamos los subfiltros que no aplican
  useEffect(() => {
    if (selectedCategory !== "Proteínas") setSelectedProteinType("Todos");
    if (selectedCategory !== "Creatinas") setSelectedCreatineType("Todos");
    if (selectedCategory !== "Vitaminas") setSelectedVitaminType("Todos");
    if (selectedCategory !== "Aminoácidos") setSelectedAminoProfile("Todos");
  }, [selectedCategory]);

  // 2. PETICIÓN DINÁMICA DE PRODUCTOS AL BACKEND
  useEffect(() => {
    setLoading(true);

    const queryParams = new URLSearchParams();
    if (searchQuery) queryParams.append("busqueda", searchQuery);
    if (selectedCategory !== "Todas") queryParams.append("categoria", selectedCategory);
    if (selectedBrand !== "Todas") queryParams.append("marca", selectedBrand);
    if (ordenPrecio) queryParams.append("orden_precio", ordenPrecio);
    
    // Subfiltros
    if (selectedFormat !== "Todos") queryParams.append("formato", selectedFormat);
    if (selectedFlavor !== "Todos") queryParams.append("sabor", selectedFlavor);
    if (selectedGoal !== "Todos") queryParams.append("objetivo", selectedGoal);
    if (selectedQualitySeal !== "Todos") queryParams.append("sello_calidad", selectedQualitySeal);
    if (isVegan === true) queryParams.append("es_vegano", "true");

    // Subfiltros condicionales
    if (selectedCategory === "Proteínas" && selectedProteinType !== "Todos") queryParams.append("tipo_proteina", selectedProteinType);
    if (selectedCategory === "Creatinas" && selectedCreatineType !== "Todos") queryParams.append("tipo_creatina", selectedCreatineType);
    if (selectedCategory === "Vitaminas" && selectedVitaminType !== "Todos") queryParams.append("tipo_vitamina", selectedVitaminType);
    if (selectedCategory === "Aminoácidos" && selectedAminoProfile !== "Todos") queryParams.append("perfil_aminoacidos", selectedAminoProfile);

    fetch(`${apiUrl}/api/productos?${queryParams.toString()}`)
      .then((res) => res.json())
      .then((data) => {
        setProductos(Array.isArray(data) ? data : data.productos || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error conectando API:", error);
        setLoading(false);
      });
  }, [
    searchQuery, selectedCategory, selectedBrand, ordenPrecio,
    selectedFormat, selectedFlavor, selectedGoal, selectedQualitySeal,
    selectedProteinType, selectedCreatineType, selectedVitaminType, selectedAminoProfile,
    isVegan, apiUrl
  ]);

  const limpiarFiltros = () => {
    setSearchQuery("");
    setSelectedCategory("Todas");
    setSelectedBrand("Todas");
    setOrdenPrecio("");
    setSelectedFormat("Todos");
    setSelectedFlavor("Todos");
    setSelectedGoal("Todos");
    setSelectedQualitySeal("Todos");
    setIsVegan(null);
  };

  return (
    <div className="w-full">
      {/* Contenedor Principal de Filtros */}
      <div className="bg-[#0f172a]/60 border border-white/10 rounded-3xl p-4 sm:p-5 mb-12 backdrop-blur-2xl flex flex-col gap-4 shadow-2xl ring-1 ring-white/5 relative z-20">
        
        {/* Fila Superior: Búsqueda y Filtros Principales */}
        <div className="flex flex-col md:flex-row gap-5 items-center justify-between">
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
              className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-12 pr-4 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all placeholder:text-slate-400 font-medium"
            />
          </div>

          <div className="flex flex-col sm:flex-row w-full md:w-auto gap-4 flex-wrap justify-end">
            <div className="flex flex-col flex-1 sm:flex-none">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Categoría</span>
              <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 appearance-none min-w-[140px] cursor-pointer">
                {categories.map(c => <option key={c} value={c} className="bg-slate-900">{c}</option>)}
              </select>
            </div>
            <div className="flex flex-col flex-1 sm:flex-none">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Marca</span>
              <select value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)} className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 appearance-none min-w-[140px] cursor-pointer">
                {brands.map(b => <option key={b} value={b} className="bg-slate-900">{b}</option>)}
              </select>
            </div>
            <div className="flex flex-col flex-1 sm:flex-none">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Precio</span>
              <select value={ordenPrecio} onChange={(e) => setOrdenPrecio(e.target.value)} className="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 appearance-none min-w-[140px] cursor-pointer">
                <option value="" className="bg-slate-900">Relevancia</option>
                <option value="asc" className="bg-slate-900">Menor a Mayor</option>
                <option value="desc" className="bg-slate-900">Mayor a Menor</option>
              </select>
            </div>
            
            {/* Botón Filtros Avanzados */}
            <div className="flex items-end">
              <button 
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className={`px-4 py-3 rounded-xl border flex items-center gap-2 font-bold transition-all text-sm ${showAdvancedFilters ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20' : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'}`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
                Filtros Extra
              </button>
            </div>
          </div>
        </div>

        {/* Panel de Filtros Avanzados (Colapsable) */}
        {showAdvancedFilters && (
          <div className="mt-4 pt-6 border-t border-white/5 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in slide-in-from-top-4 duration-300">
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Formato</span>
              <select value={selectedFormat} onChange={(e) => setSelectedFormat(e.target.value)} className="w-full bg-black/40 border border-white/10 text-slate-300 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                {formats.map(f => <option key={f} value={f} className="bg-slate-900">{f}</option>)}
              </select>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Objetivo</span>
              <select value={selectedGoal} onChange={(e) => setSelectedGoal(e.target.value)} className="w-full bg-black/40 border border-white/10 text-slate-300 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                {goals.map(g => <option key={g} value={g} className="bg-slate-900">{g}</option>)}
              </select>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Sabor</span>
              <select value={selectedFlavor} onChange={(e) => setSelectedFlavor(e.target.value)} className="w-full bg-black/40 border border-white/10 text-slate-300 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                {flavors.map(f => <option key={f} value={f} className="bg-slate-900">{f}</option>)}
              </select>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-400 mb-1 font-bold uppercase tracking-wider">Sello Calidad</span>
              <select value={selectedQualitySeal} onChange={(e) => setSelectedQualitySeal(e.target.value)} className="w-full bg-black/40 border border-white/10 text-slate-300 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                {qualitySeals.map(q => <option key={q} value={q} className="bg-slate-900">{q}</option>)}
              </select>
            </div>

            {/* Subfiltros Condicionales por Categoría */}
            {selectedCategory === "Proteínas" && (
              <div className="flex flex-col">
                <span className="text-[10px] text-blue-400 mb-1 font-bold uppercase tracking-wider">Tipo de Proteína</span>
                <select value={selectedProteinType} onChange={(e) => setSelectedProteinType(e.target.value)} className="w-full bg-blue-900/20 border border-blue-500/30 text-blue-100 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                  {proteinTypes.map(p => <option key={p} value={p} className="bg-slate-900">{p}</option>)}
                </select>
              </div>
            )}
            
            {selectedCategory === "Creatinas" && (
              <div className="flex flex-col">
                <span className="text-[10px] text-blue-400 mb-1 font-bold uppercase tracking-wider">Tipo de Creatina</span>
                <select value={selectedCreatineType} onChange={(e) => setSelectedCreatineType(e.target.value)} className="w-full bg-blue-900/20 border border-blue-500/30 text-blue-100 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                  {creatineTypes.map(c => <option key={c} value={c} className="bg-slate-900">{c}</option>)}
                </select>
              </div>
            )}

            {/* Vegano Checkbox */}
            <div className="flex flex-col justify-end">
              <label className="flex items-center gap-2 cursor-pointer p-2 rounded-xl hover:bg-white/5 transition-colors">
                <input 
                  type="checkbox" 
                  checked={isVegan === true} 
                  onChange={(e) => setIsVegan(e.target.checked ? true : null)}
                  className="w-5 h-5 rounded border-white/20 bg-black/40 text-emerald-500 focus:ring-emerald-500 focus:ring-offset-slate-900" 
                />
                <span className="text-sm font-bold text-slate-300">100% Vegano</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Skeleton Loader */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="flex flex-col bg-[#0a0f1d]/50 border border-white/5 rounded-3xl overflow-hidden h-[420px] animate-pulse">
              <div className="h-[220px] bg-white/5"></div>
              <div className="p-6 flex flex-col flex-grow">
                <div className="h-3 w-1/4 bg-white/5 rounded mb-3"></div>
                <div className="h-6 w-3/4 bg-white/10 rounded mb-4"></div>
                <div className="h-4 w-full bg-white/5 rounded mb-2"></div>
                <div className="h-4 w-5/6 bg-white/5 rounded mb-8"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="mb-6 text-slate-400 text-sm flex justify-between items-center">
            <span>Mostrando <span className="text-white font-semibold">{productos.length}</span> productos</span>
            {(selectedCategory !== "Todas" || selectedBrand !== "Todas" || searchQuery || isVegan) && (
               <button onClick={limpiarFiltros} className="text-xs text-blue-400 hover:text-blue-300 font-bold underline decoration-blue-500/30 underline-offset-4">Limpiar filtros</button>
            )}
          </div>

          {productos.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {productos.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 bg-white/5 border border-white/10 rounded-3xl">
              <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                 <svg className="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">No se encontraron productos</h3>
              <p className="text-slate-400 mb-6">Prueba a usar otros filtros o cambiar tu búsqueda.</p>
              <button onClick={limpiarFiltros} className="px-6 py-2.5 bg-white text-black font-bold rounded-xl transition-all shadow-lg hover:bg-slate-200">
                Limpiar filtros
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}