# 1. RESUMEN EJECUTIVO DEL PROYECTO

## ¿Qué es TusSuplementos?
TusSuplementos (tussuplementos.com) es una plataforma inteligente y comparador multitienda especializado en nutrición deportiva. A diferencia de un e-commerce tradicional, no cuenta con inventario propio ni gestiona envíos; opera como un orquestador y curador de catálogo que agrega, estandariza y compara ofertas de múltiples proveedores (como HSN, Farma2Go, SportLive, etc.).

## ¿Qué problema intenta resolver?
El mercado de la suplementación deportiva sufre de alta fragmentación y falta de transparencia:
1. **Dificultad de comparación:** Cada tienda presenta sus precios, formatos y envases de manera distinta (ej. precio por envase vs precio por 100g).
2. **Caos semántico:** Las marcas y categorías no están estandarizadas (ej. "Whey Protein" vs "Proteína de Suero").
3. **Falta de historial:** Los usuarios no pueden saber si una oferta actual es realmente un chollo o un precio inflado artificialmente.
4. **Alérgenos ocultos:** Es difícil para usuarios con restricciones dietéticas filtrar un catálogo cruzado de múltiples tiendas con seguridad.

## Usuario Objetivo
*   **Atletas recurrentes:** Usuarios de gimnasio y deportistas que consumen proteínas, creatina, pre-entrenos y vitaminas de manera habitual y buscan maximizar el ahorro en productos de consumo continuo.
*   **Usuarios con restricciones:** Personas que buscan estrictamente suplementación vegana, sin gluten o sin lactosa sin tener que leer etiquetas en cada web.
*   **Cazadores de ofertas:** Usuarios muy sensibles al precio que esperan que la plataforma les avise automáticamente de caídas de precio reales (chollos).

## Propuesta de Valor
1. **Unificación y Limpieza (NLP):** Un catálogo perfecto donde las descripciones sucias de docenas de tiendas se convierten en fichas estandarizadas.
2. **"Modo Versus" (Comparador Real):** Capacidad técnica de enfrentar métricas exactas (ej. precio por kg, % de proteína) entre hasta 4 productos a la vez.
3. **Filtro Antimonopolio:** Una IA en el backend (Umbrales Dinámicos) que determina si un descuento es real (ej. >30% en Proteínas) antes de notificar al usuario, filtrando el ruido.
4. **Comunidad y Gamificación:** "El Instagram de los suplementos", donde los usuarios tienen un `@username`, pueden compartir sus "Stacks" (rutinas) e interactuar ganando puntos por constancia (Check-ins).

## Funcionamiento Actual (User Journey)
1. **Descubrimiento:** El usuario llega por SEO, por un enlace de Telegram/Email o navegación directa.
2. **Búsqueda/Navegación:** Usa el Omnibox predictivo o los filtros avanzados (con soporte multilingüe, de tildes y typos) para localizar productos.
3. **Análisis:** Observa el precio estandarizado, lee el histórico/ofertas y puede meter el producto en el "Modo Versus".
4. **Interacción:** El usuario se loguea (vía Google OAuth), guarda el producto en "Favoritos", hace check-in diario o crea un Stack público.
5. **Conversión:** Al hacer clic en "Ver Oferta", es redirigido a la tienda final a través de un enlace traqueado de afiliación.

## Modelo de Monetización
*   **Actual:** Marketing de afiliación CPA (Costo por Adquisición) y Revenue Share. Cuando un usuario clica en el botón de compra, se le inyecta una cookie a través de plataformas como Awin, Tradedoubler o nativas (HSN). TusSuplementos se lleva una comisión de la venta final.
*   **Previsto/Futuro:** Códigos de descuento exclusivos (influencers), publicidad directa (sponsors de marcas en banners destacados), features premium para usuarios (ej. alertas de precio personalizadas extremas).

## Ventajas Competitivas Potenciales
*   **Cerebro NLP Estricto:** La robustez de la categorización semántica impide que la web parezca un "volcado de CSVs barato" como muchos competidores.
*   **Comunidad Gamificada:** Retener al usuario con perfiles, check-ins y *stacks* compartibles crea un foso defensivo (moat) frente a comparadores genéricos tipo KuantoKusta o Google Shopping.
*   **Notificaciones Híbridas (Push):** La conexión omnicanal del backend que avisa de los chollos nativamente por Telegram y Email (Resend) con imágenes dinámicas, eludiendo la ceguera de banners.

---

## Estado Actual del Proyecto

Clasificación de las funcionalidades a fecha de auditoría:

*   **Completamente Implementado:**
    *   Arquitectura Backend (FastAPI + Neon DB) y API REST.
    *   Arquitectura Frontend (Next.js 16 + Tailwind V4 + Vercel).
    *   Scraping/Ingestores robustos (BaseIngestor, HSN, Farma2Go, SportLive).
    *   Autenticación (Google OAuth 2.0 -> JWT propio).
    *   Motor NLP Centralizado de clasificación, sabores y alérgenos (`utils.py`).
    *   Búsqueda predictiva avanzada (trigramas, unaccent).
    *   Sistemas de persistencia asíncrona (Telegram, Newsletter, Upsert por lotes).
    *   Flujos de gamificación (Check-ins, Rachas, XP).
    *   Catálogo unificado y ordenación por "ratio de oro" y relevancia.

*   **Implementado Parcialmente:**
    *   "Modo Versus" (UI y estado local en Zustand completados; requiere iteración en la presentación de macros detallados según disponibilidad de las tiendas).
    *   Gestión de Redirecciones de Afiliación (operativo, pero latencias con intermediarios como Tradedoubler son mejorables).
    *   SEO (Sitemaps y metadatos básicos en pie, pero falta estrategia profunda de pages dinámicas y schema markup granular).

*   **En Desarrollo:**
    *   Afinamiento continuo de los diccionarios NLP para nuevas marcas internacionales.
    *   Refactorizaciones puramente estéticas (paso a diseño de controles minimalista).

*   **Planificado para el Futuro:**
    *   Migración a esquema relacional Multi-Tienda (Tabla abstracta de Producto + Tabla hija de Precios/Ofertas por Tienda). Esto requerirá migraciones complejas con Alembic.
    *   **Motor de Histórico de Precios Propio (Price History Engine):** Crítico para comparar el precio actual con la media de los últimos 30 días independientemente del MSRP reportado por el feed.
    *   Integración de nuevas tiendas (Aminha Farmacia, Bulk).

*   **Pendiente de Decisión:**
    *   Estrategia exacta de visualización de precios base (MSRP) de tiendas que ocultan dicho valor o manipulan feeds (Capado de ofertas actual en Farma2Go).
    *   Gestión de precios en formatos no estandarizados cuando no se puede calcular un precio/kg exacto.
