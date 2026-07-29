# 🏛️ Documentación de Arquitectura y Estado de Proyecto: Tus Suplementos (Suparator)

> **Documento Fuente de Verdad para Inteligencia Artificial y Equipo Lead**  
> **Última Actualización:** 29 de Julio, 2026  
> **Dominio Oficial:** `https://tussuplementos.es` (`https://www.tussuplementos.es`) (comprado en DonDominio)
> **Infraestructura:** Next.js (Vercel) + FastAPI (Render) + PostgreSQL (Neon DB)

---

## 📊 Tabla Resumen del Estado de Desarrollo

| Módulo / Funcionalidad | Área | Estado | Detalle Técnico de Implementación |
| :--- | :--- | :---: | :--- |
| **Skeleton Loaders (Carga suave)** | Frontend | **COMPLETADO** | Componente `ProductCardSkeleton.tsx` integrado en `Catalog.tsx` (8 esqueletos animados). |
| **Empty State (Estado Vacío)** | Frontend | **COMPLETADO** | Componente `EmptyState.tsx` con ilustración, subtexto y botón "Restablecer filtros". |
| **Escudo de Fallback de Imágenes** | Frontend | **COMPLETADO** | Handler `onError` y estado `imageError` en `ProductCard.tsx` redirigiendo al logo oficial. |
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
