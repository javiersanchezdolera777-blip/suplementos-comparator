"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Image from "next/image";
import ProductCard from "./ProductCard";
import ProductCardSkeleton from "./ProductCardSkeleton";
import EmptyState from "./EmptyState";
import FilterSidebar from "./FilterSidebar";
import Pagination from "./Pagination";

export default function Catalog() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const soloOfertas = searchParams ? searchParams.get("solo_ofertas") === "true" : false;

  const [productos, setProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
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

  const [totalResultados, setTotalResultados] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
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

  useEffect(() => {
    const qFromUrl = searchParams ? (searchParams.get("busqueda") || searchParams.get("q")) : null;
    if (qFromUrl !== null && qFromUrl !== searchQuery) {
      setSearchQuery(qFromUrl);
    }
  }, [searchParams]);

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
    setLoading(true);

    const queryParams = buildQueryParams();
    queryParams.append("limit", BATCH_SIZE.toString());
    queryParams.append("page", currentPage.toString());

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

    if (soloOfertas) {
      router.push("/#catalogo");
    }
  };

  const hasActiveFilters = soloOfertas || selectedCategory !== "Todas" || selectedBrands.length > 0 || searchQuery !== "" || isVegan === true || sinGluten === true || sinLactosa === true || selectedFormat !== "Todos" || selectedFlavor !== "Todos" || selectedProteinType !== "Todos" || selectedProteinPercentage !== "Todos" || selectedCreatineType !== "Todos" || selectedVitaminType !== "Todos" || selectedAminoProfile !== "Todos" || (ordenPrecio !== "" && ordenPrecio !== "relevancia");

  // Filtrado de respaldo en cliente cuando soloOfertas está activo
  const productosFiltrados = soloOfertas
    ? productos.filter(p => (p.precio_anterior && p.precio_anterior > (p.precio_actual ?? p.price)))
    : productos;

  return (
    <div className="w-full flex flex-col gap-2 md:gap-4">

      {/* HERO BANNER PREMUM ULTRA-COMPACTO SOBRIO */}
      <section className="w-full flex flex-col items-center text-center max-w-4xl mx-auto pt-1 sm:pt-2 pb-1 sm:pb-2 animate-in fade-in slide-in-from-bottom-8 duration-1000 ease-out">
        {/* 1. Titular Principal H1 con Acento Tipográfico Elegante */}
        <h1 className="text-3xl sm:text-4xl md:text-[2.65rem] font-black text-slate-900 tracking-tight text-center max-w-4xl mx-auto leading-tight mb-1.5">
          Compara precios y <span className="text-blue-600">ahorra</span> en tu suplementación
        </h1>

        {/* 2. Subtexto Claro */}
        <p className="text-sm sm:text-base text-slate-600 text-center max-w-lg mx-auto mt-0.5 mb-2.5 font-normal leading-normal">
          Analizamos las mejores tiendas en tiempo real para que encuentres tu proteína, creatina o vitamina ideal al precio más bajo.
        </p>

        {/* 3. Trío de Pilares de Valor (Texto Fino Sobrio) */}
        <div className="flex items-center justify-center gap-5 text-xs text-slate-500 font-medium flex-wrap mt-1 mb-3">
          <div className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span><strong className="text-slate-700 font-semibold">Comparativa</strong> en tiempo real</span>
          </div>
          <div className="w-1 h-1 rounded-full bg-slate-300 hidden sm:block"></div>
          <div className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span><strong className="text-slate-700 font-semibold">Transparencia</strong> €/kg</span>
          </div>
          <div className="w-1 h-1 rounded-full bg-slate-300 hidden sm:block"></div>
          <div className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
            </svg>
            <span><strong className="text-slate-700 font-semibold">100% Gratuito</strong> sin costes extra</span>
          </div>
        </div>

        {/* 5. Bar de Tiendas Interactivas (Clicables con Scroll) */}
        <div className="w-full max-w-3xl mx-auto">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 text-center">
            INTEGRADO CON EL CATÁLOGO DE
          </p>
          <div className="flex flex-wrap justify-center items-center gap-4 sm:gap-6">
            {[
              { name: "MyProtein", displayName: "MYPROTEIN", style: "text-base sm:text-lg font-black tracking-tighter" },
              { name: "HSN", displayName: "HSN", style: "text-lg sm:text-xl font-black italic" },
              { name: "Bulk", displayName: "BULK", style: "text-base sm:text-lg font-bold tracking-widest" },
              { name: "Prozis", displayName: "Prozis", style: "text-base sm:text-lg font-extrabold uppercase" },
            ].map((brand) => {
              const isSelected = selectedBrands.includes(brand.name);
              return (
                <button
                  key={brand.name}
                  onClick={() => {
                    if (isSelected) {
                      setSelectedBrands(selectedBrands.filter((b) => b !== brand.name));
                    } else {
                      setSelectedBrands([brand.name]);
                    }
                    document.getElementById("catalogo")?.scrollIntoView({ behavior: "smooth" });
                  }}
                  className={`cursor-pointer transition-all duration-200 ${isSelected
                    ? "opacity-100 scale-105 text-blue-600 font-extrabold underline underline-offset-4"
                    : "opacity-60 hover:opacity-100 hover:scale-105 text-slate-800"
                    } ${brand.style}`}
                >
                  {brand.displayName}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* ZONA DE CATÁLOGO (Filtros y Resultados) */}
      <div id="catalogo" className="scroll-mt-24 flex flex-col md:flex-row gap-8 items-start w-full relative z-10 pt-3 md:pt-5 animate-in fade-in duration-1000 delay-300 fill-mode-both ease-out">

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
          sinGluten={sinGluten}
          setSinGluten={setSinGluten}
          sinLactosa={sinLactosa}
          setSinLactosa={setSinLactosa}
          limpiarFiltros={limpiarFiltros}
          hasActiveFilters={hasActiveFilters}
          productosCount={totalResultados}
        />

        {/* ESCAPARATE DE PRODUCTOS */}
        <div className="w-full md:flex-1 flex flex-col min-h-[500px]">

          {/* Cabecera del Grid */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm gap-4 sm:gap-0">
            <div className="text-slate-600 text-sm">
              Mostrando <span className="font-semibold text-slate-900">
                {totalResultados > 0 ? (currentPage - 1) * BATCH_SIZE + 1 : 0}–{(currentPage - 1) * BATCH_SIZE + productosFiltrados.length}
              </span> de <span className="font-semibold text-slate-900">{totalResultados.toLocaleString('es-ES')}</span> productos
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