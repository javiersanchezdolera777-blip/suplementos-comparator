"use client";

import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function Catalog() {
  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

  const [totalResultados, setTotalResultados] = useState<number>(0);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const BATCH_SIZE = 36;

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Todas");
  const [selectedBrands, setSelectedBrands] = useState<string[]>([]);
  const [ordenPrecio, setOrdenPrecio] = useState("relevancia");

  const [selectedFormat, setSelectedFormat] = useState("Todos");
  const [selectedFlavor, setSelectedFlavor] = useState("Todos");
  const [selectedGoal, setSelectedGoal] = useState("Todos");
  const [selectedQualitySeal, setSelectedQualitySeal] = useState("Todos");
  const [selectedProteinType, setSelectedProteinType] = useState("Todos");
  const [selectedProteinPercentage, setSelectedProteinPercentage] = useState("Todos");
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

  const POPULAR_BRANDS = ["Optimum Nutrition", "Dymatize", "Sport Live", "MuscleTech", "Scitec", "MyProtein"];

  const [brandSearch, setBrandSearch] = useState("");

  const [openSections, setOpenSections] = useState<{ [key: string]: boolean }>({
    category: true,
    brand: true,
    subfilters: true,
    specs: false,
  });

  const toggleSection = (section: string) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

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
    if (selectedCategory !== "Proteínas") {
      setSelectedProteinType("Todos");
      setSelectedProteinPercentage("Todos");
    }
    if (selectedCategory !== "Creatinas") setSelectedCreatineType("Todos");
    if (selectedCategory !== "Vitaminas" && selectedCategory !== "Vitaminas y Minerales" && !selectedCategory.startsWith("Vitamina")) setSelectedVitaminType("Todos");
    if (selectedCategory !== "Aminoácidos") setSelectedAminoProfile("Todos");
  }, [selectedCategory]);

  const buildQueryParams = () => {
    const queryParams = new URLSearchParams();
    if (searchQuery) queryParams.append("busqueda", searchQuery);
    if (selectedCategory !== "Todas") queryParams.append("categoria", selectedCategory);
    if (selectedBrands.length > 0) queryParams.append("marcas", selectedBrands.join(","));
    
    if (ordenPrecio && ordenPrecio !== "relevancia") {
      queryParams.append("orden_precio", ordenPrecio);
    } else {
      queryParams.append("ordenar_por", "relevancia");
    }

    if (selectedFormat !== "Todos") queryParams.append("formato", selectedFormat);
    if (selectedFlavor !== "Todos") queryParams.append("sabor", selectedFlavor);
    if (selectedGoal !== "Todos") queryParams.append("objetivo", selectedGoal);
    if (selectedQualitySeal !== "Todos") queryParams.append("sello_calidad", selectedQualitySeal);
    if (isVegan === true) queryParams.append("es_vegano", "true");

    if (selectedCategory === "Proteínas") {
      if (selectedProteinType !== "Todos") queryParams.append("tipo_proteina", selectedProteinType);
      if (selectedProteinPercentage !== "Todos") queryParams.append("porcentaje_proteina", selectedProteinPercentage);
    }
    if (selectedCategory === "Creatinas" && selectedCreatineType !== "Todos") queryParams.append("tipo_creatina", selectedCreatineType);
    if ((selectedCategory === "Vitaminas" || selectedCategory === "Vitaminas y Minerales" || selectedCategory.startsWith("Vitamina")) && selectedVitaminType !== "Todos") queryParams.append("tipo_vitamina", selectedVitaminType);
    if (selectedCategory === "Aminoácidos" && selectedAminoProfile !== "Todos") queryParams.append("perfil_aminoacidos", selectedAminoProfile);
    
    return queryParams;
  };

  useEffect(() => {
    setLoading(true);

    const queryParams = buildQueryParams();
    queryParams.append("limit", BATCH_SIZE.toString());
    queryParams.append("skip", "0");

    fetch(`${apiUrl}/api/productos?${queryParams.toString()}`)
      .then((res) => res.json())
      .then((data) => {
        setProductos(Array.isArray(data) ? data : data.productos || []);
        setTotalResultados(Array.isArray(data) ? data.length : data.total_resultados || 0);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error conectando API:", error);
        setLoading(false);
      });
  }, [
    searchQuery, selectedCategory, selectedBrands, ordenPrecio,
    selectedFormat, selectedFlavor, selectedGoal, selectedQualitySeal,
    selectedProteinType, selectedProteinPercentage, selectedCreatineType, selectedVitaminType, selectedAminoProfile,
    isVegan, apiUrl
  ]);

  const cargarMasProductos = () => {
    if (loadingMore || productos.length >= totalResultados) return;
    setLoadingMore(true);

    const queryParams = buildQueryParams();
    queryParams.append("limit", BATCH_SIZE.toString());
    queryParams.append("skip", productos.length.toString());

    fetch(`${apiUrl}/api/productos?${queryParams.toString()}`)
      .then((res) => res.json())
      .then((data) => {
        const nuevosProductos = Array.isArray(data) ? data : data.productos || [];
        setProductos((prev) => [...prev, ...nuevosProductos]);
        if (!Array.isArray(data) && data.total_resultados !== undefined) {
          setTotalResultados(data.total_resultados);
        }
        setLoadingMore(false);
      })
      .catch((error) => {
        console.error("Error cargando más productos:", error);
        setLoadingMore(false);
      });
  };

  const limpiarFiltros = () => {
    setSearchQuery("");
    setSelectedCategory("Todas");
    setSelectedBrands([]);
    setOrdenPrecio("relevancia");
    setSelectedFormat("Todos");
    setSelectedFlavor("Todos");
    setSelectedGoal("Todos");
    setSelectedQualitySeal("Todos");
    setSelectedProteinType("Todos");
    setSelectedProteinPercentage("Todos");
    setSelectedCreatineType("Todos");
    setSelectedVitaminType("Todos");
    setSelectedAminoProfile("Todos");
    setIsVegan(null);
    setIsMobileFilterOpen(false);
  };

  const hasActiveFilters = selectedCategory !== "Todas" || selectedBrands.length > 0 || searchQuery !== "" || isVegan === true || selectedFormat !== "Todos" || selectedFlavor !== "Todos" || selectedProteinType !== "Todos" || selectedProteinPercentage !== "Todos" || selectedCreatineType !== "Todos" || selectedVitaminType !== "Todos" || selectedAminoProfile !== "Todos" || (ordenPrecio !== "" && ordenPrecio !== "relevancia");

  return (
    <div className="w-full flex flex-col gap-2 md:gap-4">

      {/* 🚀 FASE 2: HERO COMPACTADO */}
      <section className="w-full flex flex-col items-center text-center max-w-4xl mx-auto pt-2 md:pt-6 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">

        {/* Badge verde eliminado (Fase 1) */}
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-[1.1] mb-4">
          El mayor comparador de <br className="hidden sm:block" />
          <span className="text-blue-600">suplementos de España</span>
        </h1>

        <p className="text-base text-slate-600 max-w-2xl mx-auto mb-6 md:mb-8 leading-relaxed font-medium">
          Encuentra los mejores precios en proteínas, creatinas y vitaminas de tus marcas favoritas. Analizamos y comparamos en tiempo real para que tú ahorres.
        </p>

        {/* Barra de Búsqueda Protagonista */}
        <div className="w-full max-w-2xl mx-auto relative z-10 group mb-6">
          <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
            <svg className="h-6 w-6 text-slate-400 group-focus-within:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Busca por marca, producto o ingrediente..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white border border-slate-300 text-slate-900 rounded-2xl pl-14 pr-6 py-4 text-base md:text-lg outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-50 shadow-lg shadow-slate-200/50 transition-all placeholder:text-slate-400"
          />
        </div>

        {/* Trust Banner - Tiendas */}
        <div className="w-full max-w-3xl mx-auto mt-2">
          <p className="text-[10px] font-bold tracking-widest text-slate-400 uppercase mb-4">Integrado con el catálogo de</p>
          <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 opacity-50 hover:opacity-100 grayscale hover:grayscale-0 transition-all duration-700">
            <span className="text-lg sm:text-xl font-black tracking-tighter text-slate-800">MYPROTEIN</span>
            <span className="text-xl sm:text-2xl font-black text-slate-800 italic">HSN</span>
            <span className="text-lg sm:text-xl font-bold text-slate-800 tracking-widest">BULK</span>
            <span className="text-lg sm:text-xl font-extrabold text-slate-800 uppercase">Prozis</span>
          </div>
        </div>
      </section>

      {/* 🎛️ ZONA DE CATÁLOGO (Filtros y Resultados) - Peek Preview Effect */}
      <div id="catalogo" className="flex flex-col md:flex-row gap-8 items-start w-full relative z-10 pt-3 md:pt-5 animate-in fade-in duration-1000 delay-300 fill-mode-both ease-out">

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

        {/* SIDEBAR DE FILTROS CON SCROLL INDEPENDIENTE */}
        <aside className={`
          w-full md:w-[280px] flex-shrink-0 transition-all duration-300
          ${isMobileFilterOpen ? 'fixed inset-0 z-[100] bg-white p-6 overflow-y-auto block' : 'hidden md:block sticky top-24 max-h-[calc(100vh-110px)] overflow-y-auto pr-1 text-left'}
        `}>
          {/* Cabecera Móvil */}
          <div className="flex justify-between items-center mb-6 md:hidden">
            <h2 className="text-2xl font-black text-slate-900">Filtros</h2>
            <button onClick={() => setIsMobileFilterOpen(false)} className="p-2 bg-slate-100 rounded-full text-slate-600 hover:bg-slate-200 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>

          {/* Panel Estilizado de Filtros */}
          <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm flex flex-col gap-5">

            {/* 1. Acordeón Categoría */}
            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={() => toggleSection("category")}
                className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-700 uppercase tracking-wider py-1 hover:text-blue-600 transition-colors cursor-pointer"
              >
                <span>Categoría</span>
                <svg className={`w-4 h-4 transition-transform duration-200 ${openSections.category ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {openSections.category && (
                <div className="pt-1">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none cursor-pointer outline-none transition-all font-medium"
                  >
                    {categories.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              )}
            </div>

            <div className="h-px w-full bg-slate-100"></div>

            {/* 2. Acordeón Marca (Multiselección + Tags + Combobox) */}
            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={() => toggleSection("brand")}
                className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-700 uppercase tracking-wider py-1 hover:text-blue-600 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span>Marca</span>
                  {selectedBrands.length > 0 && (
                    <span className="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold lowercase">
                      {selectedBrands.length === 1 ? selectedBrands[0] : `${selectedBrands.length} selec.`}
                    </span>
                  )}
                </div>
                <svg className={`w-4 h-4 transition-transform duration-200 ${openSections.brand ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {openSections.brand && (
                <div className="flex flex-col gap-3 pt-1">
                  
                  {/* Etiquetas (Chips) de Marcas Seleccionadas */}
                  {selectedBrands.length > 0 && (
                    <div className="flex flex-col gap-1.5 p-2.5 bg-blue-50/70 border border-blue-100 rounded-xl">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider">
                          Seleccionadas ({selectedBrands.length})
                        </span>
                        <button
                          type="button"
                          onClick={() => setSelectedBrands([])}
                          className="text-[10px] font-bold text-slate-400 hover:text-blue-600 transition-colors cursor-pointer underline"
                        >
                          Limpiar marcas
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {selectedBrands.map((brand) => (
                          <span
                            key={brand}
                            className="inline-flex items-center gap-1 bg-white text-blue-700 border border-blue-200 text-xs font-bold px-2 py-0.5 rounded-lg shadow-sm"
                          >
                            <span>{brand}</span>
                            <button
                              type="button"
                              onClick={() => setSelectedBrands((prev) => prev.filter((b) => b !== brand))}
                              className="text-blue-400 hover:text-red-500 font-black ml-0.5 transition-colors cursor-pointer"
                              title={`Eliminar ${brand}`}
                            >
                              ✕
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Pills Gym-First (Acceso Rápido) */}
                  <div className="flex flex-col gap-1.5 mt-1.5">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Top Marcas</span>
                    <div className="flex flex-wrap gap-1.5">
                      {POPULAR_BRANDS.map((brand) => {
                        const isSelected = selectedBrands.includes(brand);
                        return (
                          <button
                            key={brand}
                            type="button"
                            onClick={() => {
                              setSelectedBrands((prev) =>
                                isSelected ? prev.filter((b) => b !== brand) : [...prev, brand]
                              );
                            }}
                            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer border ${
                              isSelected
                                ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                                : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900"
                            }`}
                          >
                            {brand}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Buscador de Marcas + Lista Inline Densa (max-h-[140px]) */}
                  <div className="flex flex-col gap-2 mt-2.5">
                    <div className="relative flex items-center">
                      <input
                        type="text"
                        placeholder="🔍 Buscar marca..."
                        value={brandSearch}
                        onChange={(e) => setBrandSearch(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl pl-3 pr-8 py-1.5 text-xs focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all placeholder:text-slate-400 font-medium"
                      />
                      {brandSearch && (
                        <button
                          type="button"
                          onClick={() => setBrandSearch("")}
                          className="absolute right-2 text-slate-400 hover:text-slate-600 p-1 rounded-full text-xs font-bold cursor-pointer"
                          title="Borrar búsqueda"
                        >
                          ✕
                        </button>
                      )}
                    </div>

                    {/* Lista Inline de Marcas Acotada a 140px */}
                    <div className="max-h-[140px] overflow-y-auto pr-1 flex flex-col gap-0.5 custom-scrollbar pt-0.5">
                      {brands
                        .filter((b) => b !== "Todas" && b.toLowerCase().includes(brandSearch.toLowerCase()))
                        .map((brand) => {
                          const isChecked = selectedBrands.includes(brand);
                          const isPopular = POPULAR_BRANDS.includes(brand);
                          return (
                            <label
                              key={brand}
                              className={`flex items-center justify-between px-2 py-1 rounded-md text-xs font-medium cursor-pointer transition-colors select-none ${
                                isChecked
                                  ? "bg-blue-50/90 text-blue-700 font-bold"
                                  : "hover:bg-slate-50 text-slate-700"
                              }`}
                            >
                              <div className="flex items-center gap-2 min-w-0">
                                <input
                                  type="checkbox"
                                  checked={isChecked}
                                  onChange={() => {
                                    setSelectedBrands((prev) =>
                                      isChecked ? prev.filter((b) => b !== brand) : [...prev, brand]
                                    );
                                  }}
                                  className="w-3.5 h-3.5 accent-blue-600 rounded cursor-pointer border-slate-300 focus:ring-blue-500"
                                />
                                <span className="truncate">{brand}</span>
                              </div>
                              {isPopular && (
                                <span className="text-[8px] font-black text-amber-600 bg-amber-50 border border-amber-200/60 px-1 py-0.2 rounded uppercase tracking-wider">
                                  ★ Top
                                </span>
                              )}
                            </label>
                          );
                        })}

                      {brands.filter((b) => b !== "Todas" && b.toLowerCase().includes(brandSearch.toLowerCase())).length === 0 && (
                        <div className="px-2 py-2 text-xs text-slate-400 text-center font-medium">
                          No se encontraron marcas
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Subfiltros Condicionales por Categoría */}
            {(selectedCategory === "Proteínas" || selectedCategory === "Creatinas" || selectedCategory === "Vitaminas" || selectedCategory === "Vitaminas y Minerales" || selectedCategory.startsWith("Vitamina") || selectedCategory === "Aminoácidos") && (
              <>
                <div className="h-px w-full bg-slate-100"></div>
                <div className="flex flex-col gap-2 p-3 bg-blue-50/50 border border-blue-100 rounded-2xl">
                  {selectedCategory === "Proteínas" && (
                    <>
                      <div className="flex flex-col gap-1">
                        <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Tipo de Proteína</label>
                        <select value={selectedProteinType} onChange={(e) => setSelectedProteinType(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                          {proteinTypes.map(p => <option key={p} value={p}>{p}</option>)}
                        </select>
                      </div>

                      <div className="flex flex-col gap-1 mt-1">
                        <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">% Proteína Mínimo</label>
                        <select value={selectedProteinPercentage} onChange={(e) => setSelectedProteinPercentage(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                          <option value="Todos">Todos los porcentajes</option>
                          <option value="90">&gt; 90% (Aislados / Pura Proteína)</option>
                          <option value="80">&gt; 80% (Whey Concentrado Premium)</option>
                          <option value="70">&gt; 70% (Estándar)</option>
                        </select>
                      </div>
                    </>
                  )}
                  {selectedCategory === "Creatinas" && (
                    <>
                      <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Tipo de Creatina</label>
                      <select value={selectedCreatineType} onChange={(e) => setSelectedCreatineType(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                        {creatineTypes.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                    </>
                  )}
                  {(selectedCategory === "Vitaminas" || selectedCategory === "Vitaminas y Minerales" || selectedCategory.startsWith("Vitamina")) && (
                    <>
                      <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Tipo de Vitamina / Mineral</label>
                      <select value={selectedVitaminType} onChange={(e) => setSelectedVitaminType(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                        {vitaminTypes.map(v => <option key={v} value={v}>{v}</option>)}
                      </select>
                    </>
                  )}
                  {selectedCategory === "Aminoácidos" && (
                    <>
                      <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Perfil de Aminoácidos</label>
                      <select value={selectedAminoProfile} onChange={(e) => setSelectedAminoProfile(e.target.value)} className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                        {aminoProfiles.map(a => <option key={a} value={a}>{a}</option>)}
                      </select>
                    </>
                  )}
                </div>
              </>
            )}

            <div className="h-px w-full bg-slate-100"></div>

            {/* 3. Acordeón Filtros Específicos */}
            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={() => toggleSection("specs")}
                className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-700 uppercase tracking-wider py-1 hover:text-blue-600 transition-colors cursor-pointer"
              >
                <span>Filtros Específicos</span>
                <svg className={`w-4 h-4 transition-transform duration-200 ${openSections.specs ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {openSections.specs && (
                <div className="flex flex-col gap-4 pt-1">
                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Formato</label>
                    <select value={selectedFormat} onChange={(e) => setSelectedFormat(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                      {formats.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                  </div>

                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Sabor</label>
                    <select value={selectedFlavor} onChange={(e) => setSelectedFlavor(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                      {flavors.map(fl => <option key={fl} value={fl}>{fl}</option>)}
                    </select>
                  </div>

                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Sello Calidad</label>
                    <select value={selectedQualitySeal} onChange={(e) => setSelectedQualitySeal(e.target.value)} className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-3 py-2.5 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium">
                      {qualitySeals.map(q => <option key={q} value={q}>{q}</option>)}
                    </select>
                  </div>

                  <label className="flex items-center gap-3 cursor-pointer p-3 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors mt-1">
                    <input
                      type="checkbox"
                      checked={isVegan === true}
                      onChange={(e) => setIsVegan(e.target.checked ? true : null)}
                      className="w-5 h-5 rounded border-slate-300 bg-white text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                    />
                    <span className="text-sm font-bold text-slate-700">Opción Vegana</span>
                  </label>
                </div>
              )}
            </div>

            {isMobileFilterOpen && (
              <button
                onClick={() => setIsMobileFilterOpen(false)}
                className="mt-4 w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl shadow-lg cursor-pointer"
              >
                Ver {productos.length} Resultados
              </button>
            )}

            {hasActiveFilters && (
              <button
                onClick={limpiarFiltros}
                className="mt-2 w-full bg-red-50 hover:bg-red-100 text-red-600 font-bold py-2.5 rounded-xl border border-red-200 transition-colors text-sm cursor-pointer"
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
              Mostrando <span className="text-slate-900 font-black text-base">{productos.length}</span> de <span className="text-slate-900 font-black text-base">{totalResultados}</span> suplementos
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider hidden sm:block">Ordenar por</label>
              <select
                value={ordenPrecio}
                onChange={(e) => setOrdenPrecio(e.target.value)}
                className="w-full sm:w-auto bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none cursor-pointer outline-none font-medium"
              >
                <option value="relevancia">Relevancia</option>
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
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {productos.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              {/* Botón Cargar Más Suplementos */}
              {productos.length < totalResultados && (
                <div className="flex flex-col items-center justify-center mt-10 mb-6 gap-3">
                  <button
                    onClick={cargarMasProductos}
                    disabled={loadingMore}
                    className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold text-base rounded-2xl shadow-lg shadow-blue-600/25 transition-all duration-200 active:scale-95 flex items-center gap-3 cursor-pointer"
                  >
                    {loadingMore ? (
                      <>
                        <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>Cargando más suplementos...</span>
                      </>
                    ) : (
                      <>
                        <span>Cargar más suplementos</span>
                        <span className="text-xs bg-blue-500/50 px-2.5 py-0.5 rounded-lg font-mono">
                          +{Math.min(BATCH_SIZE, totalResultados - productos.length)}
                        </span>
                      </>
                    )}
                  </button>
                  <span className="text-xs text-slate-400 font-medium">
                    Has visto {productos.length} de {totalResultados} suplementos
                  </span>
                </div>
              )}
            </>
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