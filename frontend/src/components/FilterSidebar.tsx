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
            ? "fixed inset-0 z-[100] bg-white p-6 overflow-y-auto block"
            : "hidden md:block sticky top-24 max-h-[calc(100vh-110px)] overflow-y-auto pr-1 text-left"
        }
      `}
    >
      {/* Cabecera Móvil */}
      <div className="flex justify-between items-center mb-6 md:hidden">
        <h2 className="text-2xl font-black text-slate-900">Filtros</h2>
        <button
          onClick={() => setIsMobileFilterOpen(false)}
          className="p-2 bg-slate-100 rounded-full text-slate-600 hover:bg-slate-200 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Panel Estilizado de Filtros */}
      <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm flex flex-col gap-5">
        
        {/* 1. Categoría Principal */}
        <div className="flex flex-col gap-2">
          <button
            type="button"
            onClick={() => toggleSection("category")}
            className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-700 uppercase tracking-wider py-1 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <span>Categoría Principal</span>
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${
                openSections.category ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
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

        {/* 2. Subfiltros y Formato (Bloque Contextual) */}
        <div className="flex flex-col gap-2">
          <button
            type="button"
            onClick={() => toggleSection("subfilters")}
            className="flex items-center justify-between w-full text-left font-bold text-xs text-slate-700 uppercase tracking-wider py-1 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <span>Formato y Especificaciones</span>
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${
                openSections.subfilters !== false ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openSections.subfilters !== false && (
            <div className="bg-slate-50 border border-slate-200/80 p-3.5 rounded-xl space-y-3 mt-1">
              {/* Selector de Formato */}
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                  Formato
                </label>
                <select
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
                >
                  {formats.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </div>

              {/* Subfiltros dinámicos según categoría */}
              {selectedCategory === "Proteínas" && (
                <>
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">
                      Tipo de Proteína
                    </label>
                    <select
                      value={selectedProteinType}
                      onChange={(e) => setSelectedProteinType(e.target.value)}
                      className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
                    >
                      {proteinTypes.map((p) => (
                        <option key={p} value={p}>
                          {p}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">
                      % Proteína Mínimo
                    </label>
                    <select
                      value={selectedProteinPercentage}
                      onChange={(e) => setSelectedProteinPercentage(e.target.value)}
                      className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
                    >
                      <option value="Todos">Todos los porcentajes</option>
                      <option value="90">&gt; 90% (Aislados / Pura Proteína)</option>
                      <option value="80">&gt; 80% (Whey Concentrado Premium)</option>
                      <option value="70">&gt; 70% (Estándar)</option>
                    </select>
                  </div>
                </>
              )}

              {selectedCategory === "Creatinas" && (
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">
                    Tipo de Creatina
                  </label>
                  <select
                    value={selectedCreatineType}
                    onChange={(e) => setSelectedCreatineType(e.target.value)}
                    className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
                  >
                    {creatineTypes.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {(selectedCategory === "Vitaminas" ||
                selectedCategory === "Vitaminas y Minerales" ||
                selectedCategory.startsWith("Vitamina")) && (
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">
                    Tipo de Vitamina / Mineral
                  </label>
                  <select
                    value={selectedVitaminType}
                    onChange={(e) => setSelectedVitaminType(e.target.value)}
                    className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
                  >
                    {vitaminTypes.map((v) => (
                      <option key={v} value={v}>
                        {v}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {selectedCategory === "Aminoácidos" && (
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">
                    Perfil de Aminoácidos
                  </label>
                  <select
                    value={selectedAminoProfile}
                    onChange={(e) => setSelectedAminoProfile(e.target.value)}
                    className="w-full bg-white border border-blue-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
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
                <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                  Sabor
                </label>
                <select
                  value={selectedFlavor}
                  onChange={(e) => setSelectedFlavor(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
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
                <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                  Sello Calidad
                </label>
                <select
                  value={selectedQualitySeal}
                  onChange={(e) => setSelectedQualitySeal(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-900 rounded-xl px-3 py-2 text-sm appearance-none cursor-pointer outline-none focus:border-blue-500 font-medium"
                >
                  {qualitySeals.map((q) => (
                    <option key={q} value={q}>
                      {q}
                    </option>
                  ))}
                </select>
              </div>

              {/* Checkbox Vegano */}
              <label className="flex items-center gap-2.5 cursor-pointer p-2.5 rounded-lg bg-white border border-slate-200/90 hover:bg-slate-100/60 transition-colors">
                <input
                  type="checkbox"
                  checked={isVegan === true}
                  onChange={(e) => setIsVegan(e.target.checked ? true : null)}
                  className="w-4 h-4 rounded border-slate-300 bg-white text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                />
                <span className="text-xs font-bold text-slate-700">Opción Vegana</span>
              </label>
            </div>
          )}
        </div>

        <div className="h-px w-full bg-slate-100"></div>

        {/* 3. Marca (Multiselección) */}
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
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${
                openSections.brand ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openSections.brand && (
            <div className="flex flex-col gap-3 pt-1">
              {/* Chips de Marcas Seleccionadas */}
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
              <div className="flex flex-col gap-1.5 mt-0.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Top Marcas
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {popularBrands.map((brand) => {
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

              {/* Buscador de Marcas + Lista Inline Densa */}
              <div className="flex flex-col gap-2 mt-1">
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

                {/* Lista Inline de Marcas Acotada */}
                <div className="max-h-[140px] overflow-y-auto pr-1 flex flex-col gap-0.5 custom-scrollbar pt-0.5">
                  {brands
                    .filter((b) => b !== "Todas" && b.toLowerCase().includes(brandSearch.toLowerCase()))
                    .map((brand) => {
                      const isChecked = selectedBrands.includes(brand);
                      const isPopular = popularBrands.includes(brand);
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

                  {brands.filter((b) => b !== "Todas" && b.toLowerCase().includes(brandSearch.toLowerCase()))
                    .length === 0 && (
                    <div className="px-2 py-2 text-xs text-slate-400 text-center font-medium">
                      No se encontraron marcas
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Acciones del filtro móvil o reseteo */}
        {isMobileFilterOpen && (
          <button
            onClick={() => setIsMobileFilterOpen(false)}
            className="mt-4 w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl shadow-lg cursor-pointer"
          >
            Ver {productosCount} Resultados
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
  );
}
