"use client";

import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function Catalog() {
  // Estados para los productos traídos de la API
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Estados de interfaz
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

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
    setIsMobileFilterOpen(false); // Cerramos en móvil al limpiar
  };

  const hasActiveFilters = selectedCategory !== "Todas" || selectedBrand !== "Todas" || searchQuery !== "" || isVegan === true || selectedFormat !== "Todos";

  return (
    <div className="flex flex-col md:flex-row gap-8 items-start w-full relative z-10">
      
      {/* 📱 Botón Flotante para Móviles (Abre el Drawer) */}
      <div className="md:hidden w-full sticky top-24 z-20 mb-4">
        <button 
          onClick={() => setIsMobileFilterOpen(true)}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-xl shadow-xl shadow-blue-900/20 backdrop-blur-md transition-all border border-blue-400/30"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
          Filtrar Catálogo
        </button>
      </div>

      {/* 🎛️ COLUMNA IZQUIERDA: SIDEBAR DE FILTROS */}
      <aside className={`
        w-full md:w-1/4 flex-shrink-0 transition-all duration-300
        ${isMobileFilterOpen ? 'fixed inset-0 z-[100] bg-[#030712]/95 backdrop-blur-2xl p-6 overflow-y-auto block' : 'hidden md:block sticky top-28'}
      `}>
        {/* Cabecera Móvil */}
        <div className="flex justify-between items-center mb-6 md:hidden">
          <h2 className="text-2xl font-black text-white">Filtros</h2>
          <button onClick={() => setIsMobileFilterOpen(false)} className="p-2 bg-white/10 rounded-full text-white hover:bg-white/20 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        {/* Panel Estilizado de Filtros */}
        <div className="bg-[#0f172a]/60 backdrop-blur-xl border border-white/10 rounded-3xl p-5 shadow-2xl flex flex-col gap-6">
          
          {/* Buscador */}
          <div className="flex flex-col gap-2">
            <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Búsqueda</label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-400">
                <svg className="h-4 w-4 text-slate-400 group-focus-within:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Proteína, pre-entreno..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-black/40 border border-white/10 text-white rounded-xl pl-9 pr-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 transition-all placeholder:text-slate-500 font-medium"
              />
            </div>
          </div>

          <div className="h-px w-full bg-white/5"></div>

          {/* Categoría y Marca */}
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Categoría</label>
              <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="w-full bg-black/40 border border-white/10 text-white rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer">
                {categories.map(c => <option key={c} value={c} className="bg-slate-900">{c}</option>)}
              </select>
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Marca</label>
              <select value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)} className="w-full bg-black/40 border border-white/10 text-white rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer">
                {brands.map(b => <option key={b} value={b} className="bg-slate-900">{b}</option>)}
              </select>
            </div>
          </div>

          {/* Subfiltros Condicionales por Categoría */}
          {(selectedCategory === "Proteínas" || selectedCategory === "Creatinas" || selectedCategory === "Vitaminas" || selectedCategory === "Aminoácidos") && (
            <>
              <div className="h-px w-full bg-white/5"></div>
              <div className="flex flex-col gap-2 p-3 bg-blue-900/10 border border-blue-500/20 rounded-2xl">
                {selectedCategory === "Proteínas" && (
                  <>
                    <label className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">Tipo de Proteína</label>
                    <select value={selectedProteinType} onChange={(e) => setSelectedProteinType(e.target.value)} className="w-full bg-black/40 border border-white/10 text-white rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                      {proteinTypes.map(p => <option key={p} value={p} className="bg-slate-900">{p}</option>)}
                    </select>
                  </>
                )}
                {selectedCategory === "Creatinas" && (
                  <>
                    <label className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">Tipo de Creatina</label>
                    <select value={selectedCreatineType} onChange={(e) => setSelectedCreatineType(e.target.value)} className="w-full bg-black/40 border border-white/10 text-white rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer">
                      {creatineTypes.map(c => <option key={c} value={c} className="bg-slate-900">{c}</option>)}
                    </select>
                  </>
                )}
              </div>
            </>
          )}

          <div className="h-px w-full bg-white/5"></div>

          {/* Otros Subfiltros */}
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Formato</label>
              <select value={selectedFormat} onChange={(e) => setSelectedFormat(e.target.value)} className="w-full bg-black/40 border border-white/10 text-slate-300 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer">
                {formats.map(f => <option key={f} value={f} className="bg-slate-900">{f}</option>)}
              </select>
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Sello Calidad</label>
              <select value={selectedQualitySeal} onChange={(e) => setSelectedQualitySeal(e.target.value)} className="w-full bg-black/40 border border-white/10 text-slate-300 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer">
                {qualitySeals.map(q => <option key={q} value={q} className="bg-slate-900">{q}</option>)}
              </select>
            </div>

            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-xl bg-black/20 hover:bg-black/40 border border-white/5 transition-colors mt-2">
              <input 
                type="checkbox" 
                checked={isVegan === true} 
                onChange={(e) => setIsVegan(e.target.checked ? true : null)}
                className="w-5 h-5 rounded border-white/20 bg-black/40 text-emerald-500 focus:ring-emerald-500 focus:ring-offset-slate-900" 
              />
              <span className="text-sm font-bold text-slate-300">Opción Vegana</span>
            </label>
          </div>

          {/* Botón Aplicar en móvil */}
          {isMobileFilterOpen && (
            <button 
              onClick={() => setIsMobileFilterOpen(false)}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl shadow-lg"
            >
              Ver {productos.length} Resultados
            </button>
          )}

          {/* Botón Limpiar Filtros */}
          {hasActiveFilters && (
            <button 
              onClick={limpiarFiltros}
              className="mt-2 w-full bg-red-500/10 hover:bg-red-500/20 text-red-400 font-bold py-2.5 rounded-xl border border-red-500/20 transition-colors text-sm"
            >
              Borrar todos los filtros
            </button>
          )}
        </div>
      </aside>

      {/* 🛍️ COLUMNA DERECHA: ESCAPARATE DE PRODUCTOS */}
      <div className="w-full md:w-3/4 flex flex-col min-h-[500px]">
        
        {/* Cabecera del Grid */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-sm gap-4 sm:gap-0">
          <div className="text-slate-300 text-sm">
            Mostrando <span className="text-white font-black text-base">{productos.length}</span> suplementos
          </div>
          
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider hidden sm:block">Ordenar por</label>
            <select 
              value={ordenPrecio} 
              onChange={(e) => setOrdenPrecio(e.target.value)} 
              className="w-full sm:w-auto bg-black/40 border border-white/10 text-white rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
            >
              <option value="" className="bg-slate-900">Relevancia</option>
              <option value="asc" className="bg-slate-900">Precio: Menor a Mayor</option>
              <option value="desc" className="bg-slate-900">Precio: Mayor a Menor</option>
            </select>
          </div>
        </div>

        {/* Contenido (Skeleton o Grid) */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="flex flex-col bg-[#0a0f1d]/50 border border-white/5 rounded-3xl overflow-hidden h-[420px] animate-pulse">
                <div className="h-[220px] bg-white/5"></div>
                <div className="p-6 flex flex-col flex-grow">
                  <div className="h-3 w-1/4 bg-white/5 rounded mb-3"></div>
                  <div className="h-6 w-3/4 bg-white/10 rounded mb-4"></div>
                  <div className="h-4 w-full bg-white/5 rounded mb-2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : productos.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {productos.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 bg-white/5 border border-white/10 rounded-3xl text-center px-4">
            <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mb-6">
               <svg className="w-10 h-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Sin resultados</h3>
            <p className="text-slate-400 mb-6 max-w-md">No hemos encontrado suplementos con esta combinación de filtros. Prueba a ser menos específico.</p>
            <button onClick={limpiarFiltros} className="px-6 py-3 bg-white text-black font-bold rounded-xl shadow-lg hover:bg-slate-200 transition-colors">
              Borrar todos los filtros
            </button>
          </div>
        )}
      </div>
    </div>
  );
}