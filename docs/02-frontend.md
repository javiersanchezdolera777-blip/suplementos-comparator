# 3. FRONTEND

## Tecnologías Principales
*   **Framework Principal:** Next.js (App Router, versión 16.x).
*   **Lenguaje:** TypeScript / React 19.
*   **Estilos:** Tailwind CSS v4.
*   **Gestión de Estado Global:** Zustand (usado principalmente para el "Modo Versus" y perfiles).
*   **Gestión de Formularios:** React Hook Form / Formularios controlados estándar de React.
*   **Componentes UI adicionales:** React Hot Toast (notificaciones *toast*).
*   **Autenticación:** `@react-oauth/google` para inicio de sesión seguro en cliente.

## Estructura de Rutas (App Router)
El frontend utiliza el App Router (`frontend/src/app`). Actualmente la arquitectura de carpetas públicas parece estar altamente concentrada en el directorio raíz (`/`) donde se inicializan componentes reactivos.
Las rutas principales son:
*   `/`: Home, actúa como catálogo dinámico renderizando el componente `Catalog.tsx`.
*   *(Otras rutas se documentarán exhaustivamente en la sección de Rutas y SEO)*.

## Gestión de Peticiones API
No se detecta el uso de librerías avanzadas de fetching como SWR o React Query. Las peticiones a la API del backend se gestionan de manera nativa mediante `fetch` dentro de `useEffect` en Client Components (CSR).
*   **Endpoint Principal:** `GET /api/productos` para alimentar la paginación y el catálogo.

## Renderizado y SEO
El frontend de TusSuplementos utiliza una arquitectura de **Renderizado Híbrido** pero fuertemente inclinada hacia el **CSR (Client-Side Rendering)** para el catálogo principal.

*   `page.tsx` base: Es un Server Component genérico.
*   `Catalog.tsx`: Es un Client Component (`"use client"`) que maneja estado de búsqueda, paginación, filtros e invoca directamente a la API.

### Implementación SEO
*   **Metadata (Title/Description):** Generada estáticamente en el `layout.tsx` de la Home (`title: "Tus Suplementos | Comparador de Precios de Nutrición Deportiva"`).
*   **Canonical:** Declarada estáticamente hacia `https://www.tussuplementos.com`.
*   **Open Graph / Twitter Cards:** Implementadas y funcionales desde el `layout.tsx`.
*   **Carga de Imágenes:** Delega en el componente `<Image>` de Next.js, lo cual requiere `sharp` activo en el servidor (como se detalla en `package.json` con `allowScripts`).

### Riesgos SEO de la Arquitectura Actual
*   **Fuerte dependencia del CSR en el catálogo:** Como el grid de productos se renderiza en el cliente tras un `fetch` en el `useEffect` de `Catalog.tsx`, los bots de Googlebot deben ejecutar JavaScript para descubrir los productos de la página principal. Aunque Google es capaz de hacerlo, es ineficiente comparado con SSR/SSG.
*   **Páginas Dinámicas Ausentes:** Actualmente el catálogo filtra dinámicamente, pero esto no parece generar SSR pre-renderizado para landings de marca o categorías (ej. una URL `/marca/hsn` que devuelva un HTML plano con los productos ya inyectados).
*   **Datos Estructurados (Schema.org):** No se detectan inyecciones nativas de JSON-LD estructurado en las capas altas del layout para `WebSite` u `Organization`.

## Componentes Clave
1.  **`Catalog.tsx`:** El corazón del frontend. Escucha `URLSearchParams` para activar filtros como `?solo_ofertas=true` e invocar peticiones paginadas a FastAPI.
2.  **`ProductCard.tsx`:** Tarjeta individual de producto. Recientemente se pulió para un diseño minimalista, suprimiendo la etiqueta del precio/kg visiblemente pero manteniendo la jerarquía de precios (Precio actual VS Precio anterior).
3.  **`Navbar.tsx` & `FilterSidebar.tsx`:** Controles dinámicos. El Sidebar responde a métricas en tiempo real, ocultando opciones con 0 resultados si el backend así lo reporta.
4.  **`store.ts` (Zustand):** Orquesta el estado compartido para funcionalidades avanzadas tipo "Añadir al Versus", permitiendo que múltiples partes de la app reaccionen instantáneamente sin prop-drilling complejo.

## UI / UX
*   **Diseño Responsivo:** Soporte total Mobile-First mediante clases de Tailwind (ej. `sm:flex`, `md:hidden`).
*   **Loading States:** Implementación de `ProductCardSkeleton` nativo para evitar saltos de layout (CLS) durante las llamadas a la red.
*   **Tracking Externo:** Inyección de Google Analytics (`@next/third-parties/google`) y scripts de verificación de TradeTracker de forma segura (`afterInteractive`).
