# 🏛️ Documentación de Arquitectura y Estado de Proyecto: Tus Suplementos (Suparator)

> **Documento Fuente de Verdad para Inteligencia Artificial y Equipo Lead**  
<<<<<<< HEAD
> **Última Actualización:** 29 de Julio, 2026  
> **Dominio Oficial:** `https://tussuplementos.es` (`https://www.tussuplementos.es`) (comprado en DonDominio)
=======
> **Última Actualización:** 28 de Julio, 2026  
> **Dominio Oficial:** `https://tussuplementos.es` (`https://www.tussuplementos.es`)  
>>>>>>> origin/main
> **Infraestructura:** Next.js (Vercel) + FastAPI (Render) + PostgreSQL (Neon DB)

---

<<<<<<< HEAD
## 📊 Tabla Resumen del Estado de Desarrollo

| Módulo / Funcionalidad | Área | Estado | Detalle Técnico de Implementación |
| :--- | :--- | :---: | :--- |
| **Skeleton Loaders (Carga suave)** | Frontend | **COMPLETADO** | Componente `ProductCardSkeleton.tsx` integrado en `Catalog.tsx` (8 esqueletos animados). |
| **Empty State (Estado Vacío)** | Frontend | **COMPLETADO** | Componente `EmptyState.tsx` con ilustración, subtexto y botón "Restablecer filtros". |
| **Micro-Compresión Vertical Hero (Above the Fold Perfect)** | Frontend | **COMPLETADO** | Ultra-compactado: `pt-2 sm:pt-4 pb-2 sm:pb-3`, H1 a `text-[2.65rem]`, subtexto en `text-sm sm:text-base`, buscador `p-1.5` y marcas a `text-base sm:text-lg`. Tarjetas de productos visibles al cargar. |
| **Multiselección de Marcas/Categorías** | Backend | **COMPLETADO** | Parámetros plurales `marcas`, `categorias`, `sabores`, `formatos` con operador `IN` en SQLAlchemy. |
| **Filtro % Proteína & Orden Relevancia** | Backend | **COMPLETADO** | Filtro `>= porcentaje_proteina` y ordenación compuesta por marcas top y categorías principales. |
| **Ingesta Masiva de HSN (119 ítems)** | Backend | **COMPLETADO** | Pipeline `ingestores/hsn.py` procesando catálogo oficial e insertando en Neon DB (1.784 productos). |
| **Diseño Card Premium & Badges** | Frontend | **COMPLETADO** | `ProductCard.tsx` con badge de descuento `-XX%`, precio tachado, precio actual y píldora `€/kg`. |
| **Módulo y Filtro "Top Ofertas"** | Frontend | **COMPLETADO** | Botón activo en `Navbar.tsx` con badge `ACTIVO`, `?solo_ofertas=true` y banner de estado en `Catalog.tsx`. |
| **Componente `FilterSidebar.tsx`** | Frontend | **COMPLETADO** | Sidebar ultra-compacto, sticky Viewport-Fit (`top-20 max-h-[calc(100vh-6rem)]`), jerarquía (Categorías → Formato/Especificaciones → Marcas) y marcas a 115px. |
| **Deep Linking (Filtros en URL)** | Frontend | **COMPLETADO** | Sincronización en tiempo real de filtros con `useSearchParams` y `window.history.pushState`. |
| **Rutas Dinámicas SEO (`/producto/[slug]`)** | Frontend | **COMPLETADO** | Página SSR indexable en `app/producto/[slug]/page.tsx` con `generateMetadata` dinámico. |
| **Lista de Favoritos & Sync API/Local** | Frontend | **COMPLETADO** | Contexto global `AuthContext.tsx` con respaldo local y sincronización con endpoint `/api/favoritos`. |
| **Configuración CRON Job Ingesta** | Backend | **EN PROGRESO** | Scripts de ingesta listos (`hsn.py`, `sportlive.py`); pendiente programar tarea en Render. |
| **Omnibox / Buscador Global Live** | Frontend | **PENDIENTE** | Desplegable de búsqueda instantánea en el header con sugerencias visuales. |
| **Badge de Tienda Origen** | Frontend | **PENDIENTE** | Etiqueta distintiva ("Disponible en HSN", "Disponible en Farma2go") en la tarjeta/modal. |
| **Tracking de Clics (`POST /api/click`)** | Backend | **PENDIENTE** | Endpoint para registrar métricas de conversión y clics salientes en enlaces de afiliados. |
=======
## 📌 1. Visión General e Infraestructura Activa

**Tus Suplementos** es la plataforma comparadora de suplementación deportiva de referencia en España. Modela y clasifica ofertas de tiendas oficiales (Awin, TradeDoubler, HSN, Farma2go, etc.), permitiendo filtrado por especificaciones técnicas avanzadas (tipo de proteína, sellos de calidad como Creapure, opciones veganas, formato, sabores, % de proteína) y redirigiendo a los e-commerces con enlaces de afiliado.

### 🌐 Mapa de Infraestructura y Producción

| Capa | Entorno Producción | Entorno Local | Descripción / Notas |
| :--- | :--- | :--- | :--- |
| **Dominio Principal** | `https://tussuplementos.es` | `http://localhost:3000` | Vinculado en Vercel con certificado SSL activo. Redirección activa desde `.com`. |
| **Frontend (Next.js)** | Vercel (`suplementos-comparator.vercel.app`) | `http://localhost:3000` | React 19, Tailwind CSS, TypeScript, App Router. API URL configurada via `NEXT_PUBLIC_API_URL`. |
| **Backend (FastAPI)** | Render (`suplementos-comparator.onrender.com`) | `http://localhost:8000` | Python 3.11+, SQLAlchemy, Pydantic v2, CORSMiddleware configurado para `tussuplementos.es`. |
| **Base de Datos** | **Neon DB** (Cloud PostgreSQL) | SQLite (`suplementos.db`) | Contiene **1.784 productos reales**, con ingesta masiva de **119 productos oficiales de HSN**. |

---

## 🗂️ 2. Modelo de Datos y Esquemas API

### 2.1. Modelo `Producto` (`backend/models.py`)
- `id`: Integer Primary Key.
- `nombre`: String (Indexado).
- `descripcion`: String (Text / Sanitizado).
- `precio` / `precio_actual`: Float (Precio final de oferta/compra).
- `precio_anterior`: Float (Opcional - PVP recomendado / RRP para cálculo de % de oferta).
- `imagen_url`: String (Con fallback a placeholder interno).
- `afiliado_url`: String (Enlace tracking de afiliado).
- `slug`: String (Indexado) — Ruta dinámica SEO (`/producto/[slug]`).
- `peso_gramos`: Integer (Opcional) — Peso neto en gramos.
- `precio_por_kg`: Float (Opcional) — Métrica calculada automáticamente (€/kg).
- `categoria_id` / `marca_id`: Foreign Keys relacionales.
- `objetivo`: String (Volumen Muscular, Pérdida de Peso, Rendimiento, Salud).
- `sabor`: JSON / Array — Soporta **múltiples sabores por producto** (`["Vainilla", "Chocolate"]`).
- `formato`: String (Polvo, Cápsulas, Líquido, Barrita).
- `es_vegano`: Boolean.
- `sello_calidad`: String (Creapure, Lacprodan, Kyowa, Isolac, Optipep).
- `tipo_proteina` / `porcentaje_proteina` / `tipo_creatina` / `perfil_aminoacidos` / `tipo_vitamina`: Sub-filtros específicos.

---

## 📊 3. Auditoría del Backlog y Estado de Desarrollo

| Módulo / Funcionalidad | Área | Estado | Detalle Técnico de Implementación |
| :--- | :--- | :---: | :--- |
| **Multiselección de Marcas/Categorías** | Backend | **COMPLETADO** | Parámetros plurales `marcas`, `categorias`, `sabores`, `formatos` con operador `IN` en SQLAlchemy (`main.py`). |
| **Filtro % Proteína & Orden Relevancia** | Backend | **COMPLETADO** | Filtro `>= porcentaje_proteina` y ordenación compuesta por marcas top y categorías principales. |
| **Parser Fixes (RegEx & Normalización)** | Backend | **COMPLETADO** | Cálculo automático de `precio_por_kg` y normalización de marcas (`Sport Live`, `Drasanvi`, `HSN`). |
| **Ingesta Masiva de HSN (119 ítems)** | Backend | **COMPLETADO** | Pipeline `ingestores/hsn.py` procesando catálogo oficial e insertando en Neon DB. |
| **Extracción `precio_anterior` (PVP)** | Backend | **COMPLETADO** | Soporte en modelo, Pydantic Schemas y base de datos para almacenar el precio previo RRP. |
| **Configuración CRON Job Ingesta** | Backend | **EN PROGRESO** | Scripts de ingesta listos (`hsn.py`, `sportlive.py`); pendiente programar tarea periódica en servidor. |
| **Tracking de Clics (`POST /api/click`)** | Backend | **PENDIENTE** | Endpoint para registrar métricas de conversión y clics salientes en enlaces de afiliados. |
| **Fuzzy Search (Búsqueda tolerante)** | Backend | **PENDIENTE** | Búsqueda insensible a acentos/erratas mediante PostgreSQL `pg_trgm` o ilike avanzado. |
| **Algoritmo Agregador Multi-tienda** | Backend | **PENDIENTE** | Módulo de agrupación de ofertas idénticas por EAN/GTIN/Nombre. |
| **Diseño Card Premium & Badges** | Frontend | **COMPLETADO** | `ProductCard.tsx` con badge de descuento `-XX%`, precio tachado, precio actual y píldora `€/kg`. |
| **Fórmula Matemática de Descuento** | Frontend | **COMPLETADO** | `Math.round(((precio_anterior - precio_actual) / precio_anterior) * 100)` con badge rojo dinámico. |
| **Módulo y Filtro "Top Ofertas"** | Frontend | **COMPLETADO** | Botón activo en `Navbar.tsx` con badge `ACTIVO`, `?solo_ofertas=true` y banner de estado en `Catalog.tsx`. |
| **Componente `FilterSidebar.tsx`** | Frontend | **COMPLETADO** | Componente modular jerárquico (chips de marca, acordiones, categorías y sub-filtros). |
| **Deep Linking (Filtros en URL)** | Frontend | **COMPLETADO** | Sincronización en tiempo real de filtros con `useSearchParams` y `window.history.pushState`. |
| **Rutas Dinámicas SEO (`/producto/[slug]`)** | Frontend | **COMPLETADO** | Página SSR indexable en `app/producto/[slug]/page.tsx` con `generateMetadata` dinámico. |
| **Lista de Favoritos & Sync API/Local** | Frontend | **COMPLETADO** | Contexto global `AuthContext.tsx` con respaldo local y sincronización con endpoint `/api/favoritos`. |
| **Gestión de Fallback de Imágenes** | Frontend | **COMPLETADO** | Renderizado condicional con estado seguro `hasImage` y placeholder tipográfico oficial. |
| **Skeleton Loaders (Carga suave)** | Frontend | **PENDIENTE** | Reemplazar indicadores de carga por esqueletos animados (`animate-pulse`) en el grid. |
| **Omnibox / Buscador Global Live** | Frontend | **PENDIENTE** | Desplegable de búsqueda instantánea en el header con sugerencias visuales. |
| **Badge de Tienda Origen** | Frontend | **PENDIENTE** | Etiqueta distintiva ("Disponible en HSN", "Disponible en Farma2go") en la tarjeta/modal. |
| **Logo Vectorizado SVG & Favicon** | Design | **EN PROGRESO** | Definición final del branding en modo claro y oscuro. |
| **Meta-Tags OpenGraph / Social Media** | Frontend | **EN PROGRESO** | Configuración de previsualización para compartir en WhatsApp, Twitter y LinkedIn. |
| **Vista Comparativa Multi-tienda** | Frontend | **PENDIENTE** | Tabla comparativa de precios entre tiendas para un mismo suplemento. |

---

## 🎯 4. Hoja de Ruta Prioritaria (Próximos Pasos)

1. **Sprint 1 (Frontend UX):** Implementar **Skeleton Loaders** en `Catalog.tsx` para mejorar la experiencia de carga percibida.
2. **Sprint 2 (Tracking & Analytics):** Crear el endpoint `POST /api/click` en FastAPI e integrarlo en los botones "Ver oferta" del Frontend.
3. **Sprint 3 (Branding & OpenGraph):** Finalizar el Favicon/Logo SVG y la configuración de `metadata` OpenGraph en Next.js App Router para compartir enlaces.
4. **Sprint 4 (Automatización Ingesta):** Configurar tarea programada (Cron Job) para ejecutar periódicamente `hsn.py` y `sportlive.py` actualizando Neon DB.

---

> **Nota para la IA y Desarrolladores:** Este documento debe actualizarse tras cada hito o PR aprobada en `main`.
>>>>>>> origin/main
