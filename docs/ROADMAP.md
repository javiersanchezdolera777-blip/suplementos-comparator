# Roadmap del Proyecto

Planificación estructurada en Sprints para la evolución de "Tus Suplementos".

## Sprint 1 (Quick Wins & UI) - [COMPLETADO ✅]
- [x] Implementar un logo visible y optimizado para móvil (isotipo responsive y favicon oficial).
- [x] Fix de la barra de búsqueda y optimización del menú responsive con bloqueo de scroll.
- [x] Estandarización de interfaz en Modo Claro Oficial de Alto Contraste.
- [x] Añadir filtros de alérgenos (Sin Gluten, Sin Lactosa) en el frontend y backend.

## Sprint 2 (Buscador & Automatización)
- [ ] Integrar Fuzzy Search en PostgreSQL mediante la extensión `pg_trgm`.
- [ ] Implementar Omnibox en vivo (búsqueda predictiva) en el frontend.
- [ ] Desarrollo e integración del endpoint `POST /api/click` para capturar la interacción de los usuarios.
- [ ] Configuración de CRON Jobs diarios para ingesta automática de datos.
- [ ] Corrección y despliegue del Bot de Telegram (ofertas automatizadas).

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
