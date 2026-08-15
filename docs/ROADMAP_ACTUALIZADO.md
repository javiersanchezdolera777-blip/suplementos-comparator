# Roadmap Actualizado del Proyecto

*Fecha de Revisión: 15 de Agosto de 2026*

Este Roadmap refleja el progreso real de la plataforma "Tus Suplementos" y define los próximos pasos estratégicos basados en la auditoría de Deuda Técnica y "Mejoras Futuras".

---

## Sprint 1 (Quick Wins & UI) - [COMPLETADO ✅]
- [x] Implementar un logo visible y optimizado para móvil (isotipo responsive y favicon oficial).
- [x] Fix de la barra de búsqueda y optimización del menú responsive con bloqueo de scroll.
- [x] Estandarización de interfaz en Modo Claro Oficial de Alto Contraste.
- [x] Añadir filtros de alérgenos (Sin Gluten, Sin Lactosa, Vegano) en el frontend y backend.
- [x] Implementación de panel de Favoritos (Wishlist) y sistema de Autenticación con Google (JWT).

## Sprint 2 (Buscador Inteligente & Automatización) - [COMPLETADO ✅]
- [x] Motor Fuzzy Search (pg_trgm + unaccent) en PostgreSQL para tolerancia a erratas y tildes.
- [x] Endpoint ligero `/api/productos/live-search` con ranking de relevancia y normalización bidireccional de sinónimos.
- [x] SearchOmnibox interactivo en vivo con diseño premium de 4 resultados.
- [x] Pipeline de ejecución programada (CRON Scrapers / GitHub Actions) para actualización diaria de precios desatendida.
- [x] Bot de Chollos de Telegram desplegado con Strict CI/CD (Pendiente de verificación en el próximo CRON).

---

## Sprint 3 (Expansión de Catálogo y Retención) - [NUEVO SPRINT ACTIVO 🔵]
Este Sprint se centra en aportar el verdadero valor del comparador: múltiples tiendas y alertas directas al usuario.

- **[ ] 3.1 Integración de Nuevas Tiendas:**
  - Conectar y estabilizar los ingestores de **MyProtein** y **Prozis** al CRON diario de actualizaciones.
- **[ ] 3.2 Alertas de Favoritos por Email:**
  - Modificar el orquestador de precios para cruzar bajadas de precio con la tabla de `Favoritos`.
  - Configurar un proveedor de Email (SendGrid o Resend) para notificar al usuario cuando su suplemento favorito baja de precio.
- **[ ] 3.3 UI de Telegram en la Web:**
  - Añadir un banner o botón visible en el Frontend ("Únete al canal de Chollos en Telegram") para monetizar/fidelizar el tráfico.
- **[ ] 3.4 Deuda Técnica (Migraciones):**
  - Implementar **Alembic** para el control de versiones de la estructura de PostgreSQL (fundamental antes de que la base de usuarios crezca).

## Sprint 4 (SEO y Comunidad) - [PLANIFICADO ⚪]
- [ ] Creación de perfiles de usuario públicos ("Stack habitual / Instagram de suplementos").
- [ ] Inyección dinámica de Schema.org JSON-LD para productos y categorías.
- [ ] Estrategia de SEO programático (Landing pages automáticas por marca/categoría).
- [ ] Algoritmo agregador multi-tienda avanzado (para fusionar productos idénticos vendidos en distintos e-commerces bajo un comparador "Cara a Cara").
- [ ] Caché de servidor (Redis) para el endpoint principal de catálogo.
