"use client";

import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function Catalog() {
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

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

  useEffect(() => {
    if (selectedCategory !== "Proteínas") setSelectedProteinType("Todos");
    if (selectedCategory !== "Creatinas") setSelectedCreatineType("Todos");
    if (selectedCategory !== "Vitaminas") setSelectedVitaminType("Todos");
    if (selectedCategory !== "Aminoácidos") setSelectedAminoProfile("Todos");
  }, [selectedCategory]);

  useEffect(() => {
    setLoading(true);

    const queryParams = new URLSearchParams();
    if (searchQuery) queryParams.append("busqueda", searchQuery);
    if (selectedCategory !== "Todas") queryParams.append("categoria", selectedCategory);
    if (selectedBrand !== "Todas") queryParams.append("marca", selectedBrand);
    if (ordenPrecio) queryParams.append("orden_precio", ordenPrecio);
    
    if (selectedFormat !== "Todos") queryParams.append("formato", selectedFormat);
    if (selectedFlavor !== "Todos") queryParams.append("sabor", selectedFlavor);
    if (selectedGoal !== "Todos") queryParams.append("objetivo", selectedGoal);
    if (selectedQualitySeal !== "Todos") queryParams.append("sello_calidad", selectedQualitySeal);
    if (isVegan === true) queryParams.append("es_vegano", "true");

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
    setIsMobileFilterOpen(false);
  };

  const hasActiveFilters = selectedCategory !== "Todas" || selectedBrand !== "Todas" || searchQuery !== "" || isVegan === true || selectedFormat !== "Todos";

  return (
    <div className="w-full flex flex-col gap-16">
      
      {/* 🚀 FASE 3: HERO DIVIDIDO */}
      <section className="w-full grid md:grid-cols-2 gap-10 lg:gap-16 items-center animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">
        
        {/* Columna Izquierda: Copys y Buscador */}
        <div className="flex flex-col items-start text-left order-last md:order-first mt-4 md:mt-0">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-700 mb-6 shadow-sm transition-transform hover:scale-105 cursor-default">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Comparando precios en tiempo real</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tighter leading-[1.1] mb-5 text-slate-900">
            El mayor comparador de <br className="hidden lg:block" />
            <span className="text-blue-600">suplementos de España</span>
          </h1>

          <p className="text-base text-slate-600 max-w-lg mb-10 leading-relaxed font-medium">
            Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. <span className="text-slate-900 font-bold">Analizamos y comparamos en tiempo real</span> para que tú ahorres.
          </p>

          {/* Barra de Búsqueda Integrada al Hero */}
          <div className="w-full relative z-20 group mb-10">
            <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Busca por marca, producto o ingrediente..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-slate-200 text-slate-900 rounded-2xl pl-14 pr-6 py-4 text-base outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-50 shadow-md transition-all placeholder:text-slate-400"
            />
          </div>

          {/* Partner Grid */}
          <div className="w-full border-t border-slate-200 pt-6">
            <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase mb-4">Comparamos el catálogo de</p>
            <div className="flex flex-wrap items-center gap-6 lg:gap-8 opacity-60 grayscale hover:grayscale-0 transition-all duration-700">
              <span className="text-xl font-black tracking-tighter text-slate-800">MYPROTEIN</span>
              <span className="text-2xl font-black text-slate-800 italic">HSN</span>
              <span className="text-xl font-bold text-slate-800 tracking-widest">BULK</span>
              <span className="text-xl font-extrabold text-slate-800 uppercase">Prozis</span>
            </div>
          </div>
        </div>

        {/* Columna Derecha: Imagen Lifestyle Unsplash */}
        <div className="w-full relative aspect-[4/3] lg:aspect-square xl:aspect-[4/3] rounded-3xl overflow-hidden shadow-xl shadow-slate-200/50 border border-slate-100 group order-first md:order-last mb-8 md:mb-0">
          <img 
            src="https://images.unsplash.com/photo-1593079831268-3381b0c1239b?q=80&w=2069&auto=format&fit=crop" 
            alt="Atleta entrenando y consumiendo suplementos" 
            className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
          />
          <div className="absolute inset-0 bg-gradient-to-tr from-slate-900/10 to-transparent pointer-events-none"></div>
        </div>

      </section>

      {/* 🎛️ ZONA DE CATÁLOGO (Filtros y Resultados) */}
      <div id="catalogo" className="flex flex-col md:flex-row gap-8 items-start w-full relative z-10 pt-8 border-t border-slate-200 animate-in fade-in duration-1000 delay-300 fill-mode-both ease-out">
      
      {/* Botón Flotante para Móviles */}
      <div className="md:hidden w-full sticky top-24 z-20 mb-4">
        <button 
          onClick={() => setIsMobileFilterOpen(true)}
          className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-6 rounded-xl shadow-lg shadow-slate-900/20 transition-all"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
          Filtrar Catálogo
        </button>
      </div>

      {/* SIDEBAR DE FILTROS */}
      <aside className={`
        w-full md:w-[260px] flex-shrink-0 transition-all duration-300
        ${isMobileFilterOpen ? 'fixed inset-0 z-[100] bg-white p-6 overflow-y-auto block' : 'hidden md:block sticky top-28'}
      `}>
        {/* Cabecera Móvil */}
        <div className="flex justify-between items-center mb-6 md:hidden">
          <h2 className="text-2xl font-black text-slate-900">Filtros</h2>
          <button onClick={() => setIsMobileFilterOpen(false)} className="p-2 bg-slate-100 rounded-full text-slate-600 hover:bg-slate-200 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        {/* Panel Estilizado de Filtros */}
        <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm flex flex-col gap-6">
          
          {/* Categoría y Marca */}
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Categoría</label>
              <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none cursor-pointer outline-none transition-all">
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Marca</label>
              <select value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none cursor-pointer outline-none transition-all">
                {brands.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          </div>

          {/* Subfiltros Condicionales por Categoría */}
          {(selectedCategory === "Proteínas" || selectedCategory === "Creatinas" || selectedCategory === "Vitaminas" || selectedCategory === "Aminoácidos") && (
            <>
              <div className="h-px w-full bg-slate-100"></div>
              <div className="flex flex-col gap-2 p-3 bg-blue-50/50 border border-blue-100 rounded-2xl">
                {selectedCategory === "Proteínas" && (
                  <>
                    <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Tipo de Proteína</label>
                    <select value={selectedProteinType} onChange={(e) => setSelectedProteinType(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500">
                      {proteinTypes.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </>
                )}
                {selectedCategory === "Creatinas" && (
                  <>
                    <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Tipo de Creatina</label>
                    <select value={selectedCreatineType} onChange={(e) => setSelectedCreatineType(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500">
                      {creatineTypes.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </>
                )}
              </div>
            </>
          )}

          <div className="h-px w-full bg-slate-100"></div>

          {/* Otros Subfiltros */}
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Formato</label>
              <select value={selectedFormat} onChange={(e) => setSelectedFormat(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500">
                {formats.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Sello Calidad</label>
              <select value={selectedQualitySeal} onChange={(e) => setSelectedQualitySeal(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500">
                {qualitySeals.map(q => <option key={q} value={q}>{q}</option>)}
              </select>
            </div>

            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors mt-2">
              <input 
                type="checkbox" 
                checked={isVegan === true} 
                onChange={(e) => setIsVegan(e.target.checked ? true : null)}
                className="w-5 h-5 rounded border-slate-300 bg-white text-emerald-500 focus:ring-emerald-500" 
              />
              <span className="text-sm font-bold text-slate-700">Opción Vegana</span>
            </label>
          </div>

          {isMobileFilterOpen && (
            <button 
              onClick={() => setIsMobileFilterOpen(false)}
              className="mt-4 w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl shadow-lg"
            >
              Ver {productos.length} Resultados
            </button>
          )}

          {hasActiveFilters && (
            <button 
              onClick={limpiarFiltros}
              className="mt-2 w-full bg-red-50 hover:bg-red-100 text-red-600 font-bold py-2.5 rounded-xl border border-red-200 transition-colors text-sm"
            >
              Borrar todos los filtros
            </button>
          )}
        </div>
      </aside>

      {/* ESCAPARATE DE PRODUCTOS */}
      <div className="w-full md:flex-1 flex flex-col min-h-[500px]">
        
        {/* Cabecera del Grid */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm gap-4 sm:gap-0">
          <div className="text-slate-500 text-sm">
            Mostrando <span className="text-slate-900 font-black text-base">{productos.length}</span> suplementos
          </div>
          
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider hidden sm:block">Ordenar por</label>
            <select 
              value={ordenPrecio} 
              onChange={(e) => setOrdenPrecio(e.target.value)} 
              className="w-full sm:w-auto bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none cursor-pointer outline-none"
            >
              <option value="">Relevancia</option>
              <option value="asc">Precio: Menor a Mayor</option>
              <option value="desc">Precio: Mayor a Menor</option>
            </select>
          </div>
        </div>

        {/* Contenido (Skeleton o Grid) */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="flex flex-col bg-white border border-slate-200 rounded-3xl overflow-hidden h-[420px] animate-pulse">
                <div className="h-[220px] bg-slate-100"></div>
                <div className="p-6 flex flex-col flex-grow">
                  <div className="h-3 w-1/4 bg-slate-200 rounded mb-3"></div>
                  <div className="h-6 w-3/4 bg-slate-200 rounded mb-4"></div>
                  <div className="h-4 w-full bg-slate-100 rounded mb-2"></div>
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
          <div className="flex flex-col items-center justify-center py-20 bg-white border border-slate-200 rounded-3xl text-center px-4 shadow-sm">
            <div className="w-20 h-20 bg-slate-50 border border-slate-200 rounded-full flex items-center justify-center mb-6">
               <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-2">Sin resultados</h3>
            <p className="text-slate-500 mb-6 max-w-md">No hemos encontrado suplementos con esta combinación de filtros. Prueba a ser menos específico.</p>
            <button onClick={limpiarFiltros} className="px-6 py-3 bg-slate-900 text-white font-bold rounded-xl shadow-lg hover:bg-slate-800 transition-colors">
              Borrar todos los filtros
            </button>
          </div>
        )}
      </div>
      </div>
    </div>
  );
}