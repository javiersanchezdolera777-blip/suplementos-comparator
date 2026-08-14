# Estado Actual del Proyecto

## Dominio y Entorno Operativo
*   **Dominio Oficial Activo (Canónico):** [https://www.tussuplementos.com](https://www.tussuplementos.com) (con redirección desde .es)
*   **Backend URL:** Desplegado en Render (o similar configurado).
*   **Frontend URL:** Desplegado en Vercel.

## Estado de la Base de Datos
*   **Motor:** PostgreSQL (Neon DB).
*   **Catálogo Actual:** HSN completamente integrado.
*   **Volumen:** Más de 800 productos clasificados e ingestados correctamente.
*   **NLP:** Catálogo de HSN 100% re-etiquetado con flags de alérgenos (Sin Gluten / Sin Lactosa) y categorías NLP en cascada.
*   **Limpieza:** Las marcas huérfanas de pruebas anteriores han sido purgadas de la tabla maestra de `marcas`. La normalización agrupa todas las gamas de HSN bajo el paraguas de HSN y aísla las marcas externas reales (ej. *NOW Foods*, *Swanson*).

## Tareas Completadas (Checklist Reciente)
- [x] Refactorización masiva del `utils.py` (Cerebro NLP de catalogación).
- [x] Actualización del bloque de extracción de precios y marcas dinámicas en `hsn.py` (JSON-LD prioritario y Fallback HTML).
- [x] Configuración estricta de borrado y reinicio (`tienda == "HSN"`) en el script de ingestión.
- [x] Resolución de colisiones NLP graves ("espiNACa", "Colágeno Hidrolizado" vs "Proteínas").
- [x] Purgado de marcas huérfanas y filtro en `GET /api/marcas` para no mostrar marcas con stock nulo.
- [x] Despliegue de los cambios críticos a la rama `main` en GitHub (Pull Request #59).
- [x] Soporte Full-Stack para filtrado de alérgenos (Sin Gluten, Sin Lactosa y Vegano).
- [x] Branding y Favicon: Reemplazado favicon por defecto de Vercel por icon.png, apple-icon.png y versionado ?v=2 contra caché móvil.
- [x] Búsqueda predictiva tolerante a erratas (pg_trgm trigrams + Live Search dropdown en tiempo real).
- [x] Soporte de búsqueda insensible a acentos/tildes con extensión PostgreSQL unaccent.
- [x] Algoritmo de ranking por word_similarity para términos cortos en títulos largos.
- [x] SearchOmnibox reactivo con temporizador debounced de 200ms y conexión Fetch/XHR fluida.

## Tareas Pendientes Inmediatas (Next Steps)
- [ ] Ejecutar ingestores pendientes para MyProtein y Prozis.
