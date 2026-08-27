# 9. MAPA DE URLs Y SEO ACTUAL

## Inventario de Rutas Públicas Actuales (Next.js App Router)

La arquitectura de Next.js (`src/app`) define las siguientes rutas accesibles para el usuario y los bots:

| URL o patrón | Tipo de página | Fuente de datos | Renderizado | Indexable | Observaciones SEO |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | Home / Catálogo maestro | API (`/api/productos`) | CSR (Client) | Sí (Teórico) | La inyección de productos es vía fetch en cliente (`useEffect`). Googlebot renderiza JS, pero la indexación masiva será lenta. |
| `/?categoria=X&marca=Y` | Filtros del catálogo | API (`/api/productos`) | CSR (Client) | No | Los parámetros dinámicos no alteran el HTML renderizado desde el servidor. |
| `/producto/[slug]` | Ficha de Producto | API (`/api/productos/{slug}`) | Híbrido (SSR/CSR) | Sí | Es la página con mayor potencial SEO transaccional. Debe asegurar SSR completo para el título y descripción. |
| `/versus` | Modo Versus | API | CSR | Sí / No | Su valor SEO es bajo a menos que se creen URLs estáticas como `/versus/proteina-a-vs-proteina-b`. |
| `/favoritos` | Wishlist Privada | LocalStorage / API | CSR | No (Privado)| No debe indexarse (requiere autenticación o cookie de sesión). |
| `/about`, `/contact` | Páginas estáticas corporativas | Texto hardcodeado | SSG (Static) | Sí | Aportan confianza (E-E-A-T) al sitio. |
| `/legal`, `/privacy`, `/cookies` | Textos Legales obligatorios | Texto hardcodeado | SSG (Static) | Sí (Opcional) | Necesarias para programas de afiliados y compliance GDPR. |

## SEO y Renderizado (Diagnóstico Técnico)

### 1. Datos Estructurados (Schema.org)
**Estado Actual:** Ausente o deficiente.
El análisis de los archivos base (`layout.tsx`, `page.tsx`) revela que no se están inyectando metadatos estructurados en formato JSON-LD, lo cual es crítico para un e-commerce o comparador.
*   **Faltan:** `Organization` / `WebSite` en la Home.
*   **Falta:** `Product` / `Offer` en `/producto/[slug]`. Esto es gravísimo, ya que Google no podrá extraer el precio, la moneda o el estado del stock para pintarlo en los Rich Snippets de los resultados de búsqueda.
*   **Falta:** `BreadcrumbList` para mejorar la navegación del bot.

### 2. Sitemaps y Robots.txt
El proyecto cuenta con `sitemap.ts` y `robots.ts` en la raíz de `app/`.
*   Esto es correcto y permite la generación dinámica del sitemap en Next.js. Es fundamental que el sitemap esté conectado al backend para pintar las URLs `/producto/[slug]` a medida que se insertan.

### 3. Etiquetas HTML Base
*   El `layout.tsx` principal inyecta los `title`, `description`, `canonical` y OpenGraph universales.
*   **Riesgo Detectado:** Si las vistas internas como `/producto/[slug]` no sobreescriben la propiedad `metadata` exportando la función `generateMetadata({ params })` de Next.js, Google indexará miles de páginas de producto con el título y descripción de la Home.

## Riesgos y Problemas SEO Críticos

1.  **Páginas Dinámicas Inexistentes (Falta de Landings):**
    Actualmente el usuario filtra por categorías usando querystrings (`/?categoria=proteinas`). Desde el punto de vista SEO, esto es un agujero negro. No existe una ruta física `/categoria/proteinas` o `/marca/hsn` renderizada en el servidor con un `<h1>` optimizado, texto introductorio y catálogo pre-inyectado. Si no se crean estas Landings SSG/ISR, será imposible posicionar *keywords* transaccionales *Mid-Tail* (ej. "Comprar Proteína Whey Barata").
2.  **Renderizado en Cliente (CSR) de la Home:**
    La página principal delega la carga del catálogo a un componente React (`Catalog.tsx`). Aunque soluciona la interactividad rápida, priva al HTML inicial del servidor del enlazado interno.
3.  **Falta de JSON-LD:**
    Sin marcado `Product`, se pierden los Rich Snippets.
4.  **Canibalización de Filtros:**
    Si el archivo `robots.ts` no bloquea explícitamente parámetros de ordenación (`?orden=precio_asc` o `?solo_ofertas=true`), Google podría rastrear miles de combinaciones de la Home y diluir el "Crawl Budget".

## Recomendaciones Inmediatas (Roadmap SEO)
*   **Añadir JSON-LD:** En `/producto/[slug]` inyectar `<script type="application/ld+json">` con la estructura estandarizada de Google para `Product` (Nombre, Imágen, Marca) y `Offer` (Precio, Moneda, URL de afiliado).
*   **Rutas Estáticas de Categoria:** Migrar la lógica de filtros genéricos en la Home a rutas App Router dinámicas como `src/app/categoria/[slug]/page.tsx` para permitir SSR (Server-Side Rendering) y meta tags únicos por categoría.
