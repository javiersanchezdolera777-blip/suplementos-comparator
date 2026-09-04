"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import ProductCard from "./ProductCard";
import ProductCardSkeleton from "./ProductCardSkeleton";
import EmptyState from "./EmptyState";
import FilterSidebar from "./FilterSidebar";
import Pagination from "./Pagination";

interface CatalogProps {
  initialProducts?: any[];
  initialTotal?: number;
  preselectedCategory?: string;
  preselectedBrand?: string;
}

export default function Catalog({
  initialProducts,
  initialTotal,
  preselectedCategory,
  preselectedBrand,
}: CatalogProps = {}) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const soloOfertas = searchParams ? searchParams.get("solo_ofertas") === "true" : false;

  const [productos, setProductos] = useState<any[]>(initialProducts || []);
  const [loading, setLoading] = useState(initialProducts ? false : true);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

  useEffect(() => {
    if (isMobileFilterOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isMobileFilterOpen]);

  const [totalResultados, setTotalResultados] = useState<number>(initialTotal || 0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const BATCH_SIZE = 36;

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState(preselectedCategory || "Todas");
  const [selectedBrands, setSelectedBrands] = useState<string[]>(preselectedBrand ? [preselectedBrand] : []);
  const isFirstRender = useRef(true);
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
  const [sinGluten, setSinGluten] = useState<boolean | null>(null);
  const [sinLactosa, setSinLactosa] = useState<boolean | null>(null);

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

  // --- 🔥 EL ARREGLO MÁGICO: ESCUCHAR LA URL PARA LOS STACKS ---
  useEffect(() => {
    const qFromUrl = searchParams ? (searchParams.get("busqueda") || searchParams.get("q")) : null;
    const newQuery = qFromUrl || "";
    if (newQuery !== searchQuery) {
      setSearchQuery(newQuery);
    }

    // 2. Sincronizar Categorías (El atajo de los Stacks)
    const catFromUrl = searchParams.get("categoria");
    if (catFromUrl) {
      let catFormateada = "Todas";
      // Traductor: pasamos el "id" de la URL al nombre real del catálogo de Javi
      if (catFromUrl === "proteina") catFormateada = "Proteínas";
      else if (catFromUrl === "creatina") catFormateada = "Creatinas";
      else if (catFromUrl === "vitaminas") catFormateada = "Vitaminas y Minerales";
      else if (catFromUrl === "aminoacidos") catFormateada = "Aminoácidos";
      else if (catFromUrl === "pre-entreno") catFormateada = "Pre-entrenos";
      else catFormateada = catFromUrl; // Por si algún día coincide exacto

      setSelectedCategory(catFormateada);
    }
  }, [searchParams, searchQuery]);
  // ---------------------------------------------------------------

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
    if (sinGluten === true) queryParams.append("sin_gluten", "true");
    if (sinLactosa === true) queryParams.append("sin_lactosa", "true");

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
    // Si tenemos initialProducts, omitimos la primera carga
    if (isFirstRender.current && initialProducts) {
      isFirstRender.current = false;
      return;
    }

    // 1. CREAMOS LA BANDERA MÁGICA
    let peticionActiva = true; 
    
    setLoading(true);

    const queryParams = buildQueryParams();
    queryParams.append("limit", BATCH_SIZE.toString());
    queryParams.append("page", currentPage.toString());

    fetch(`${apiUrl}/api/productos?${queryParams.toString()}`)
      .then((res) => res.json())
      .then((data) => {
        // 2. SI LA BANDERA ESTÁ BAJADA, IGNORAMOS ESTA RESPUESTA VIEJA
        if (!peticionActiva) return; 
        
        setProductos(Array.isArray(data) ? data : data.productos || []);
        setTotalResultados(Array.isArray(data) ? data.length : data.total_resultados || 0);
        setLoading(false);
      })
      .catch((error) => {
        if (!peticionActiva) return;
        console.error("Error conectando API:", error);
        setLoading(false);
      });

    // 3. FUNCIÓN DE LIMPIEZA: Si el usuario cambia de filtro antes de que termine, bajamos la bandera
    return () => {
      peticionActiva = false; 
    };
  }, [
    searchQuery, selectedCategory, selectedBrands, ordenPrecio,
    selectedFormat, selectedFlavor, selectedGoal, selectedQualitySeal,
    selectedProteinType, selectedProteinPercentage, selectedCreatineType, selectedVitaminType, selectedAminoProfile,
    isVegan, sinGluten, sinLactosa, soloOfertas, apiUrl, currentPage
  ]);

  // Reset page to 1 when any filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [
    searchQuery, selectedCategory, selectedBrands, ordenPrecio,
    selectedFormat, selectedFlavor, selectedGoal, selectedQualitySeal,
    selectedProteinType, selectedProteinPercentage, selectedCreatineType, selectedVitaminType, selectedAminoProfile,
    isVegan, sinGluten, sinLactosa, soloOfertas
  ]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
    setSinGluten(null);
    setSinLactosa(null);
    setIsMobileFilterOpen(false);

    // 🔥 ARREGLO: Limpiamos la URL para que el filtro de categoría no se quede atascado
    router.push("/#catalogo");
  };

  const hasActiveFilters = soloOfertas || selectedCategory !== "Todas" || selectedBrands.length > 0 || searchQuery !== "" || isVegan === true || sinGluten === true || sinLactosa === true || selectedFormat !== "Todos" || selectedFlavor !== "Todos" || selectedProteinType !== "Todos" || selectedProteinPercentage !== "Todos" || selectedCreatineType !== "Todos" || selectedVitaminType !== "Todos" || selectedAminoProfile !== "Todos" || (ordenPrecio !== "" && ordenPrecio !== "relevancia");

  // Filtrado de respaldo en cliente cuando soloOfertas está activo
  const productosFiltrados = soloOfertas
    ? productos.filter(p => (p.precio_anterior && p.precio_anterior > (p.precio_actual ?? p.price)))
    : productos;

  return (
    <div className="w-full flex flex-col gap-1 md:gap-4">

      {/* HERO BANNER — Comprimido en móvil, completo en desktop */}
      <section className="w-full flex flex-col items-center text-center max-w-4xl mx-auto pt-1 md:pt-2 pb-0 md:pb-2 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">
        {/* 1. Titular Principal H1 */}
        <h1 className="text-2xl md:text-[2.65rem] font-black text-slate-900 tracking-tight text-center max-w-4xl mx-auto leading-tight mb-3 md:mb-1.5">
          Compara precios y <span className="text-blue-600">ahorra</span> en tu suplementación
        </h1>

        {/* 2. Subtexto Claro (Oculto en móvil) */}
        <p className="hidden md:block text-base text-slate-600 text-center max-w-lg mx-auto mt-0.5 mb-2.5 font-normal leading-normal">
          Analizamos las mejores tiendas en tiempo real para que encuentres tu proteína, creatina o vitamina ideal al precio más bajo.
        </p>

        {/* 3. Trío de Pilares de Valor */}
        <div className="flex items-center justify-center gap-1.5 md:gap-5 text-xs text-slate-500 font-medium flex-wrap mb-4 md:mb-3">
          <div className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5 md:w-3.5 md:h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span><strong className="text-slate-700 font-semibold">Comparativa</strong> en tiempo real</span>
          </div>
          <div className="w-0.5 h-0.5 md:w-1 md:h-1 rounded-full bg-slate-300"></div>
          <div className="flex items-center gap-1">
            <span className="text-sm md:text-base leading-none">📦</span>
            <span><strong className="text-slate-700 font-semibold">+1500</strong> productos</span>
          </div>
          <div className="w-0.5 h-0.5 md:w-1 md:h-1 rounded-full bg-slate-300"></div>
          <div className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5 md:w-3.5 md:h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
            </svg>
            <span><strong className="text-slate-700 font-semibold">100% Gratis</strong></span>
          </div>
        </div>

        {/* 4. Bar de Tiendas Interactivas */}
        <div className="w-full max-w-3xl mx-auto mt-0.5 md:my-0">
          <p className="hidden md:block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 md:mb-1.5 text-center">
            INTEGRADO CON EL CATÁLOGO DE
          </p>
          <div className="flex flex-row justify-center items-center gap-3 md:gap-6">
            {[
              { name: "HSN", displayName: "HSN", style: "text-lg md:text-xl font-black italic uppercase" },
              { name: "NOW Foods", displayName: "NOW FOODS", style: "text-base md:text-lg font-bold uppercase tracking-wide" },
              { name: "Swanson", displayName: "SWANSON", style: "text-base md:text-lg font-semibold uppercase tracking-widest" },
              { name: "Drasanvi", displayName: "DRASANVI", style: "text-base md:text-lg font-black uppercase tracking-wider" },
            ].map((brand) => {
              const isSelected = selectedBrands.includes(brand.name);
              return (
                <Link
                  key={brand.name}
                  href={`/marca/${brand.name.toLowerCase().replace(/\s+/g, '-')}`}
                  className={`cursor-pointer transition-all duration-200 ${isSelected
                    ? "opacity-100 scale-105 text-blue-600 font-extrabold underline underline-offset-4"
                    : "opacity-60 hover:opacity-100 hover:scale-105 text-slate-800"
                    } ${brand.style}`}
                >
                  {brand.displayName}
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* ZONA DE CATÁLOGO (Filtros y Resultados) */}
      <div id="catalogo" className="scroll-mt-24 flex flex-col md:flex-row gap-8 items-start w-full relative z-10 pt-3 md:pt-5">

        {/* Botón Flotante para Móviles (FAB) */}
        <div className="md:hidden fixed bottom-20 left-1/2 transform -translate-x-1/2 z-50">
          <button
            onClick={() => setIsMobileFilterOpen(true)}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white py-2.5 px-5 rounded-full shadow-md shadow-blue-600/30 transition-all text-base font-semibold whitespace-nowrap"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
            Filtros
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
          sinGluten={sinGluten}
          setSinGluten={setSinGluten}
          sinLactosa={sinLactosa}
          setSinLactosa={setSinLactosa}
          limpiarFiltros={limpiarFiltros}
          hasActiveFilters={hasActiveFilters}
          productosCount={totalResultados}
          productosFiltrados={productosFiltrados}
        />

        {/* ESCAPARATE DE PRODUCTOS */}
        <div className="w-full md:flex-1 flex flex-col min-h-[500px]">

          {/* Banner de Añadir a Stack */}
          {searchParams?.get("add_to_stack") && (
            <div className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-4 flex items-start sm:items-center justify-between text-blue-900 shadow-sm animate-in fade-in slide-in-from-top-4">
              <div className="flex items-start sm:items-center gap-3">
                <div className="text-3xl hidden sm:block">✨</div>
                <div>
                   <h4 className="font-bold text-sm sm:text-base text-blue-950">¡Tu Stack está creado!</h4>
                   <p className="text-xs sm:text-sm text-blue-800/90 mt-0.5">Busca el suplemento que quieras y pulsa el botón (+) en su tarjeta para añadirlo.</p>
                </div>
              </div>
              <button 
                onClick={() => {
                  const params = new URLSearchParams(window.location.search);
                  params.delete("add_to_stack");
                  router.push(`/?${params.toString()}#catalogo`);
                }}
                className="text-xs font-bold text-blue-600 hover:text-blue-800 bg-white hover:bg-blue-100 border border-blue-200 px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap ml-4"
              >
                Terminar
              </button>
            </div>
          )}

          {/* Cabecera del Grid */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 md:mb-6 bg-white border border-slate-200 rounded-xl md:rounded-2xl p-2.5 md:p-4 shadow-sm gap-2 sm:gap-0">
            <div className="text-slate-600 text-xs md:text-sm">
              Mostrando <span className="font-semibold text-slate-900">
                {totalResultados > 0 ? (currentPage - 1) * BATCH_SIZE + 1 : 0}–{(currentPage - 1) * BATCH_SIZE + productosFiltrados.length}
              </span> de <span className="font-semibold text-slate-900">{totalResultados.toLocaleString('es-ES')}</span> productos
            </div>

            <div className="grid grid-cols-2 sm:flex items-center gap-2 w-full sm:w-auto">
              {/* Botón Ofertas Exclusivo Móvil - Estética Premium y Sobria */}
              <button
                onClick={() => {
                  const params = new URLSearchParams(window.location.search);
                  if (soloOfertas) {
                    params.delete("solo_ofertas");
                  } else {
                    params.set("solo_ofertas", "true");
                  }
                  router.push(`/?${params.toString()}#catalogo`);
                }}
                className={`md:hidden flex items-center justify-center gap-1 h-8 px-2.5 rounded-lg border text-[10px] font-bold uppercase tracking-widest transition-all ${
                  soloOfertas
                    ? "bg-slate-900 text-white border-slate-900 shadow-md"
                    : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
                }`}
              >
                <svg className="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                <span>Ofertas</span>
              </button>

              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider hidden sm:block ml-2">Ordenar por</label>
              
              {/* Selector Minimalista (Dropdown Nativo Optimizado) */}
              <div className="relative w-full sm:w-auto h-8 md:h-10">
                <select
                  value={ordenPrecio}
                  onChange={(e) => setOrdenPrecio(e.target.value)}
                  className="w-full h-full bg-white border border-slate-200 text-slate-700 rounded-lg pl-3 pr-8 text-[11px] font-bold uppercase tracking-widest focus:ring-1 focus:ring-slate-900 focus:border-slate-900 appearance-none cursor-pointer outline-none transition-colors"
                >
                  <option value="relevancia">Relevancia</option>
                  <option value="asc">Menor Precio</option>
                  <option value="desc">Mayor Precio</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-2.5 pointer-events-none text-slate-400">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Contenido (Skeleton, Grid o EmptyState) */}
          {loading ? (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-2 md:grid-cols-3 md:gap-4">
              {[...Array(8)].map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </div>
          ) : productosFiltrados.length > 0 ? (
            <>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-2 md:grid-cols-3 md:gap-4">
                {productosFiltrados.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              {/* Paginación */}
              {totalResultados > BATCH_SIZE && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={Math.ceil(totalResultados / BATCH_SIZE)}
                  onPageChange={handlePageChange}
                />
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