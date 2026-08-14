# Roadmap del Proyecto

Planificación estructurada en Sprints para la evolución de "Tus Suplementos".

## Sprint 1 (Quick Wins & UI) - [COMPLETADO ✅]
- [x] Implementar un logo visible y optimizado para móvil (isotipo responsive y favicon oficial).
- [x] Fix de la barra de búsqueda y optimización del menú responsive con bloqueo de scroll.
- [x] Estandarización de interfaz en Modo Claro Oficial de Alto Contraste.
- [x] Añadir filtros de alérgenos (Sin Gluten, Sin Lactosa) en el frontend y backend.

## Sprint 2 (Buscador Inteligente & Automatización) - [EN PROGRESO 🟡]
- [x] Motor Fuzzy Search (pg_trgm + unaccent) en PostgreSQL para tolerancia a erratas y tildes.
- [x] Endpoint ligero `/api/productos/live-search` con ranking de relevancia.
- [x] SearchOmnibox interactivo en vivo con miniaturas, precios y debouncing.
- [ ] Pipeline de ejecución programada (CRON Scrapers) para actualización diaria de precios.
- [ ] Bot de Chollos de Telegram con alertas en tiempo real.

## Sprint 3 (Retención & Comunidad)
- [ ] Sistema de alertas de bajada de precio notificadas por email.
- [ ] Creación de perfiles de usuario públicos ("Stack habitual / Instagram de suplementos").
- [ ] Inyección dinámica de Schema.org JSON-LD para productos y categorías.
- [ ] Estrategia de SEO programático.

## Sprint 4 (Expansión Multi-Tienda)
- [ ] Ingesta del catálogo completo de **MyProtein** usando la arquitectura híbrida ETL.
- [ ] Ingesta del catálogo completo de **Prozis** usando la arquitectura híbrida ETL.
- [ ] Ingesta del catálogo de **ESN**.
- [ ] Desarrollo de algoritmo agregador multi-tienda (para productos idénticos vendidos en distintos e-commerces).
- [ ] Interfaz de comparador "Cara a Cara" de suplementos equivalentes.
