"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ProductCard from "./ProductCard";
import ProductCardSkeleton from "./ProductCardSkeleton";
import EmptyState from "./EmptyState";
import FilterSidebar from "./FilterSidebar";

export default function Catalog() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const soloOfertas = searchParams ? searchParams.get("solo_ofertas") === "true" : false;

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

  const POPULAR_BRANDS = ["HSN", "Optimum Nutrition", "MyProtein", "Dymatize", "MuscleTech", "Scitec"];

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
    if (soloOfertas) queryParams.append("solo_ofertas", "true");
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
    isVegan, soloOfertas, apiUrl
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

    if (soloOfertas) {
      router.push("/#catalogo");
    }
  };

  const hasActiveFilters = soloOfertas || selectedCategory !== "Todas" || selectedBrands.length > 0 || searchQuery !== "" || isVegan === true || selectedFormat !== "Todos" || selectedFlavor !== "Todos" || selectedProteinType !== "Todos" || selectedProteinPercentage !== "Todos" || selectedCreatineType !== "Todos" || selectedVitaminType !== "Todos" || selectedAminoProfile !== "Todos" || (ordenPrecio !== "" && ordenPrecio !== "relevancia");

  // Filtrado de respaldo en cliente cuando soloOfertas está activo
  const productosFiltrados = soloOfertas
    ? productos.filter(p => (p.precio_anterior && p.precio_anterior > (p.precio_actual ?? p.price)))
    : productos;

  return (
    <div className="w-full flex flex-col gap-2 md:gap-4">

      {/* HERO COMPACTADO */}
      <section className="w-full flex flex-col items-center text-center max-w-4xl mx-auto pt-2 md:pt-6 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">
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

      {/* ZONA DE CATÁLOGO (Filtros y Resultados) */}
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

        {/* SIDEBAR DE FILTROS MODULAR */}
        <FilterSidebar
          isMobileFilterOpen={isMobileFilterOpen}
          setIsMobileFilterOpen={setIsMobileFilterOpen}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          categories={categories}
          selectedBrands={selectedBrands}
          setSelectedBrands={setSelectedBrands}
          brands={brands}
          popularBrands={POPULAR_BRANDS}
          brandSearch={brandSearch}
          setBrandSearch={setBrandSearch}
          openSections={openSections}
          toggleSection={toggleSection}
          selectedFormat={selectedFormat}
          setSelectedFormat={setSelectedFormat}
          formats={formats}
          selectedFlavor={selectedFlavor}
          setSelectedFlavor={setSelectedFlavor}
          flavors={flavors}
          selectedQualitySeal={selectedQualitySeal}
          setSelectedQualitySeal={setSelectedQualitySeal}
          qualitySeals={qualitySeals}
          selectedProteinType={selectedProteinType}
          setSelectedProteinType={setSelectedProteinType}
          proteinTypes={proteinTypes}
          selectedProteinPercentage={selectedProteinPercentage}
          setSelectedProteinPercentage={setSelectedProteinPercentage}
          selectedCreatineType={selectedCreatineType}
          setSelectedCreatineType={setSelectedCreatineType}
          creatineTypes={creatineTypes}
          selectedVitaminType={selectedVitaminType}
          setSelectedVitaminType={setSelectedVitaminType}
          vitaminTypes={vitaminTypes}
          selectedAminoProfile={selectedAminoProfile}
          setSelectedAminoProfile={setSelectedAminoProfile}
          aminoProfiles={aminoProfiles}
          isVegan={isVegan}
          setIsVegan={setIsVegan}
          limpiarFiltros={limpiarFiltros}
          hasActiveFilters={hasActiveFilters}
          productosCount={productosFiltrados.length}
        />

        {/* ESCAPARATE DE PRODUCTOS */}
        <div className="w-full md:flex-1 flex flex-col min-h-[500px]">

          {/* Banner de Estado "Top Ofertas" */}
          {soloOfertas && (
            <div className="w-full bg-gradient-to-r from-red-600 via-rose-600 to-red-500 text-white p-4 sm:p-5 rounded-2xl mb-6 shadow-lg shadow-red-500/10 flex items-center justify-between flex-wrap gap-4 animate-in fade-in slide-in-from-top-4 duration-300">
              <div className="flex items-center gap-3.5">
                <span className="text-2xl bg-white/20 p-2.5 rounded-xl backdrop-blur-md">🔥</span>
                <div>
                  <h3 className="font-extrabold text-base sm:text-lg leading-tight">Viendo solo ofertas y chollos destacados</h3>
                  <p className="text-xs text-red-100 font-medium">Mostrando únicamente suplementos con precio rebajado sobre su tarifa original.</p>
                </div>
              </div>
              <button
                onClick={() => router.push("/#catalogo")}
                className="bg-white hover:bg-slate-100 text-red-600 font-bold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm cursor-pointer whitespace-nowrap"
              >
                Ver todo el catálogo
              </button>
            </div>
          )}

          {/* Cabecera del Grid */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm gap-4 sm:gap-0">
            <div className="text-slate-500 text-sm">
              Mostrando <span className="text-slate-900 font-black text-base">{productosFiltrados.length}</span> de <span className="text-slate-900 font-black text-base">{soloOfertas ? productosFiltrados.length : totalResultados}</span> suplementos
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

          {/* Contenido (Skeleton, Grid o EmptyState) */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(8)].map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </div>
          ) : productosFiltrados.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {productosFiltrados.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              {/* Botón Cargar Más Suplementos */}
              {!soloOfertas && productos.length < totalResultados && (
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
            <EmptyState resetFilters={limpiarFiltros} />
          )}
        </div>
      </div>
    </div>
  );
}