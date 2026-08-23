"use client";

import { Dispatch, SetStateAction } from "react";

interface FilterSidebarProps {
  isMobileFilterOpen: boolean;
  setIsMobileFilterOpen: (open: boolean) => void;
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  categories: string[];
  selectedBrands: string[];
  setSelectedBrands: Dispatch<SetStateAction<string[]>>;
  brands: string[];
  popularBrands: string[];
  brandSearch: string;
  setBrandSearch: (search: string) => void;
  openSections: { [key: string]: boolean };
  toggleSection: (section: string) => void;
  selectedFormat: string;
  setSelectedFormat: (format: string) => void;
  formats: string[];
  selectedFlavor: string;
  setSelectedFlavor: (flavor: string) => void;
  flavors: string[];
  selectedQualitySeal: string;
  setSelectedQualitySeal: (seal: string) => void;
  qualitySeals: string[];
  selectedProteinType: string;
  setSelectedProteinType: (type: string) => void;
  proteinTypes: string[];
  selectedProteinPercentage: string;
  setSelectedProteinPercentage: (percentage: string) => void;
  selectedCreatineType: string;
  setSelectedCreatineType: (type: string) => void;
  creatineTypes: string[];
  selectedVitaminType: string;
  setSelectedVitaminType: (type: string) => void;
  vitaminTypes: string[];
  selectedAminoProfile: string;
  setSelectedAminoProfile: (profile: string) => void;
  aminoProfiles: string[];
  isVegan: boolean | null;
  setIsVegan: (vegan: boolean | null) => void;
  sinGluten: boolean | null;
  setSinGluten: (gluten: boolean | null) => void;
  sinLactosa: boolean | null;
  setSinLactosa: (lactosa: boolean | null) => void;
  limpiarFiltros: () => void;
  hasActiveFilters: boolean;
  productosCount: number;
}

export default function FilterSidebar({
  isMobileFilterOpen,
  setIsMobileFilterOpen,
  selectedCategory,
  setSelectedCategory,
  categories,
  selectedBrands,
  setSelectedBrands,
  brands,
  popularBrands,
  brandSearch,
  setBrandSearch,
  openSections,
  toggleSection,
  selectedFormat,
  setSelectedFormat,
  formats,
  selectedFlavor,
  setSelectedFlavor,
  flavors,
  selectedQualitySeal,
  setSelectedQualitySeal,
  qualitySeals,
  selectedProteinType,
  setSelectedProteinType,
  proteinTypes,
  selectedProteinPercentage,
  setSelectedProteinPercentage,
  selectedCreatineType,
  setSelectedCreatineType,
  creatineTypes,
  selectedVitaminType,
  setSelectedVitaminType,
  vitaminTypes,
  selectedAminoProfile,
  setSelectedAminoProfile,
  aminoProfiles,
  isVegan,
  setIsVegan,
  sinGluten,
  setSinGluten,
  sinLactosa,
  setSinLactosa,
  limpiarFiltros,
  hasActiveFilters,
  productosCount,
}: FilterSidebarProps) {
  return (
    <aside
      className={`
        w-full md:w-[280px] flex-shrink-0 transition-all duration-300
        ${
          isMobileFilterOpen
            ? "fixed inset-0 z-[100] bg-white p-5 overflow-y-auto block"
            : "hidden md:block sticky top-20 w-full max-h-[calc(100vh-6rem)] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-200 text-left"
        }
      `}
    >
      {/* Cabecera Móvil */}
      <div className="flex justify-between items-center mb-4 md:hidden">
        <h2 className="text-xl font-black text-slate-900">Filtros</h2>
        <button
          onClick={() => setIsMobileFilterOpen(false)}
          className="p-1.5 bg-slate-100 rounded-full text-slate-600 hover:bg-slate-200 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Panel Estilizado Ultra-Compacto */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col gap-3.5">
        
        {/* 1. CATEGORÍA PRINCIPAL */}
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            onClick={() => toggleSection("category")}
            className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-800 uppercase tracking-wider py-0.5 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <span>Categoría Principal</span>
            <svg
              className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                openSections.category !== false ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {openSections.category !== false && (
            <div className="pt-0.5">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none cursor-pointer outline-none transition-all font-semibold"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="h-px w-full bg-slate-100"></div>

        {/* 2. FORMATO Y ESPECIFICACIONES AVANZADAS */}
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            onClick={() => toggleSection("subfilters")}
            className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-800 uppercase tracking-wider py-0.5 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <span>Formato y Especificaciones</span>
            <svg
              className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                openSections.subfilters !== false ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openSections.subfilters !== false && (
            <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl space-y-2.5 mt-0.5">
              {/* Formato */}
              <div className="flex flex-col gap-1">
                <label className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">
                  Formato
                </label>
                <select
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                >
                  {formats.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </div>

              {/* Subfiltros dinámicos según categoría: Proteínas */}
              {selectedCategory === "Proteínas" && (
                <>
                  <div className="flex flex-col gap-1">
                    <label className="text-[9px] text-blue-600 font-bold uppercase tracking-wider">
                      Tipo de Proteína
                    </label>
                    <select
                      value={selectedProteinType}
                      onChange={(e) => setSelectedProteinType(e.target.value)}
                      className="w-full bg-white border border-blue-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                    >
                      {proteinTypes.map((p) => (
                        <option key={p} value={p}>
                          {p}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[9px] text-blue-600 font-bold uppercase tracking-wider">
                      % Proteína Mínimo
                    </label>
                    <select
                      value={selectedProteinPercentage}
                      onChange={(e) => setSelectedProteinPercentage(e.target.value)}
                      className="w-full bg-white border border-blue-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                    >
                      <option value="Todos">Todos los porcentajes</option>
                      <option value="90">&gt; 90% (Aislados / Pura Proteína)</option>
                      <option value="80">&gt; 80% (Whey Concentrado Premium)</option>
                      <option value="70">&gt; 70% (Estándar)</option>
                    </select>
                  </div>
                </>
              )}

              {/* Subfiltros dinámicos según categoría: Creatinas */}
              {selectedCategory === "Creatinas" && (
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] text-blue-600 font-bold uppercase tracking-wider">
                    Tipo de Creatina
                  </label>
                  <select
                    value={selectedCreatineType}
                    onChange={(e) => setSelectedCreatineType(e.target.value)}
                    className="w-full bg-white border border-blue-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                  >
                    {creatineTypes.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Subfiltros dinámicos según categoría: Vitaminas */}
              {(selectedCategory === "Vitaminas" ||
                selectedCategory === "Vitaminas y Minerales" ||
                selectedCategory.startsWith("Vitamina")) && (
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] text-blue-600 font-bold uppercase tracking-wider">
                    Tipo de Vitamina / Mineral
                  </label>
                  <select
                    value={selectedVitaminType}
                    onChange={(e) => setSelectedVitaminType(e.target.value)}
                    className="w-full bg-white border border-blue-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                  >
                    {vitaminTypes.map((v) => (
                      <option key={v} value={v}>
                        {v}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Subfiltros dinámicos según categoría: Aminoácidos */}
              {selectedCategory === "Aminoácidos" && (
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] text-blue-600 font-bold uppercase tracking-wider">
                    Perfil de Aminoácidos
                  </label>
                  <select
                    value={selectedAminoProfile}
                    onChange={(e) => setSelectedAminoProfile(e.target.value)}
                    className="w-full bg-white border border-blue-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                  >
                    {aminoProfiles.map((a) => (
                      <option key={a} value={a}>
                        {a}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Sabor */}
              <div className="flex flex-col gap-1">
                <label className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">
                  Sabor
                </label>
                <select
                  value={selectedFlavor}
                  onChange={(e) => setSelectedFlavor(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                >
                  {flavors.map((fl) => (
                    <option key={fl} value={fl}>
                      {fl}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sello de Calidad */}
              <div className="flex flex-col gap-1">
                <label className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">
                  Sello Calidad
                </label>
                <select
                  value={selectedQualitySeal}
                  onChange={(e) => setSelectedQualitySeal(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-900 rounded-lg px-2 py-1 text-xs appearance-none cursor-pointer outline-none focus:border-blue-500 font-semibold"
                >
                  {qualitySeals.map((q) => (
                    <option key={q} value={q}>
                      {q}
                    </option>
                  ))}
                </select>
              </div>

              {/* Checkbox Sin Gluten */}
              <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 transition-colors">
                <input
                  type="checkbox"
                  checked={sinGluten === true}
                  onChange={(e) => setSinGluten(e.target.checked ? true : null)}
                  className="w-3.5 h-3.5 rounded border-slate-300 bg-white text-orange-500 focus:ring-orange-500 cursor-pointer"
                />
                <span className="text-[11px] font-bold text-slate-700">Sin Gluten</span>
              </label>

              {/* Checkbox Sin Lactosa */}
              <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 transition-colors">
                <input
                  type="checkbox"
                  checked={sinLactosa === true}
                  onChange={(e) => setSinLactosa(e.target.checked ? true : null)}
                  className="w-3.5 h-3.5 rounded border-slate-300 bg-white text-blue-500 focus:ring-blue-500 cursor-pointer"
                />
                <span className="text-[11px] font-bold text-slate-700">Sin Lactosa</span>
              </label>

              {/* Checkbox Vegano */}
              <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 transition-colors">
                <input
                  type="checkbox"
                  checked={isVegan === true}
                  onChange={(e) => setIsVegan(e.target.checked ? true : null)}
                  className="w-3.5 h-3.5 rounded border-slate-300 bg-white text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                />
                <span className="text-[11px] font-bold text-slate-700">Opción Vegana</span>
              </label>
            </div>
          )}
        </div>

        <div className="h-px w-full bg-slate-100"></div>

        {/* 3. MARCA (BLOQUE INFERIOR) */}
        <div className="flex flex-col gap-2">
          <button
            type="button"
            onClick={() => toggleSection("brand")}
            className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-800 uppercase tracking-wider py-0.5 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-1.5">
              <span>Marca</span>
              {selectedBrands.length > 0 && (
                <span className="bg-blue-100 text-blue-700 text-[10px] px-1.5 py-0.2 rounded-md font-extrabold">
                  {selectedBrands.length}
                </span>
              )}
            </div>
            <svg
              className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                openSections.brand !== false ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openSections.brand !== false && (
            <div className="flex flex-col gap-2 pt-0.5">
              {/* Chips de Marcas Seleccionadas */}
              {selectedBrands.length > 0 && (
                <div className="flex flex-col gap-1 p-2 bg-blue-50/80 border border-blue-100 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-[9px] font-bold text-blue-600 uppercase tracking-wider">
                      Seleccionadas ({selectedBrands.length})
                    </span>
                    <button
                      type="button"
                      onClick={() => setSelectedBrands([])}
                      className="text-[9px] font-bold text-slate-400 hover:text-blue-600 transition-colors cursor-pointer underline"
                    >
                      Limpiar
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1 pt-0.5">
                    {selectedBrands.map((brand) => (
                      <span
                        key={brand}
                        className="inline-flex items-center gap-1 bg-white text-blue-700 border border-blue-200 text-[10px] font-bold px-1.5 py-0.5 rounded-md shadow-2xs"
                      >
                        <span>{brand}</span>
                        <button
                          type="button"
                          onClick={() => setSelectedBrands((prev) => prev.filter((b) => b !== brand))}
                          className="text-blue-400 hover:text-red-500 font-black transition-colors cursor-pointer"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}



              {/* Input Buscador de Marcas */}
              <div className="relative flex items-center mt-0.5">
                <input
                  type="text"
                  placeholder="🔍 Buscar marca..."
                  value={brandSearch}
                  onChange={(e) => setBrandSearch(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-lg pl-2.5 pr-7 py-1 text-[11px] focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all placeholder:text-slate-400 font-medium"
                />
                {brandSearch && (
                  <button
                    type="button"
                    onClick={() => setBrandSearch("")}
                    className="absolute right-1.5 text-slate-400 hover:text-slate-600 p-0.5 rounded-full text-[10px] font-bold cursor-pointer"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* Lista de Checkboxes de Marcas (115px fijo) */}
              <div className="h-[115px] max-h-[115px] overflow-y-auto pr-1 flex flex-col gap-0.5 custom-scrollbar border border-slate-100 rounded-lg p-1 bg-slate-50">
                {brands
                  .filter((b) => b !== "Todas" && b.toLowerCase().includes(brandSearch.toLowerCase()))
                  .map((brand) => {
                    const isChecked = selectedBrands.includes(brand);
                    const isPopular = popularBrands.includes(brand);
                    return (
                      <label
                        key={brand}
                        className={`flex items-center justify-between px-1.5 py-0.5 rounded text-[11px] font-medium cursor-pointer transition-colors select-none ${
                          isChecked
                            ? "bg-blue-50 text-blue-700 font-bold"
                            : "hover:bg-slate-100 text-slate-700"
                        }`}
                      >
                        <div className="flex items-center gap-1.5 min-w-0">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {
                              setSelectedBrands((prev) =>
                                isChecked ? prev.filter((b) => b !== brand) : [...prev, brand]
                              );
                            }}
                            className="w-3 h-3 accent-blue-600 rounded cursor-pointer border-slate-300 focus:ring-blue-500"
                          />
                          <span className="truncate">{brand}</span>
                        </div>
                        {isPopular && (
                          <span className="text-[8px] font-black text-amber-600 bg-amber-50 px-1 rounded uppercase">
                            ★
                          </span>
                        )}
                      </label>
                    );
                  })}

                {brands.filter((b) => b !== "Todas" && b.toLowerCase().includes(brandSearch.toLowerCase()))
                  .length === 0 && (
                  <div className="px-2 py-1.5 text-[10px] text-slate-400 text-center font-medium">
                    Sin marcas encontradas
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Acciones de filtro móvil o reseteo */}
        {isMobileFilterOpen && (
          <button
            onClick={() => setIsMobileFilterOpen(false)}
            className="mt-3 w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-2.5 rounded-xl text-xs shadow-md cursor-pointer"
          >
            Ver {productosCount} Resultados
          </button>
        )}

        {hasActiveFilters && (
          <button
            onClick={limpiarFiltros}
            className="mt-1 w-full bg-red-50 hover:bg-red-100 text-red-600 font-bold py-2 rounded-lg border border-red-200 transition-colors text-xs cursor-pointer"
          >
            Borrar todos los filtros
          </button>
        )}
      </div>
    </aside>
  );
}
