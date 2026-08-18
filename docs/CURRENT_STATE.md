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
- [x] Rediseño UI del SearchOmnibox a 4 resultados premium con tipografía elegante y mayor legibilidad.
- [x] Búsqueda predictiva y catálogo sincronizados con expansión de sinónimos multilingüe y soporte nativo de tildes.
- [x] Pipeline maestro de actualización de precios (Python) y automatización programada diaria vía GitHub Actions (CRON 05:00 UTC).
- [x] Corrección de la ordenación por precio (`orden_precio`) y unificación de criterios en nulos con `nulls_last`.
- [x] Ocultación de las categorías "Accesorios" y "Otros" del endpoint `/api/config/filtros`.
- [x] Corrección de mapeo NLP: Productos de Drasanvi movidos de "Otros" a "Salud y Bienestar".
- [x] Extracción y soporte real de los flags `sin_gluten` y `sin_lactosa` tanto en HSN como Farma2Go (evaluación de arrays en memoria).
- [x] Implementada la "Doble Barrera" NLP para excluir con precisión productos de mascotas/veterinaria en `utils.py` y `pharma2go.py` y purgada la BBDD (+30 items eliminados).
- [x] Limpieza de la raíz del backend migrando herramientas de testing/cron a la subcarpeta `/scripts`.
- [⏳ PENDIENTE DE VERIFICACIÓN] El bot de Telegram está desplegado con Strict CI/CD. Queda confirmar que el CRON programado inyecta correctamente los Secrets en modo desatendido (verificación a la espera de la próxima ventana horaria).

## Sprint 3: Monolito Estable Restaurado
- **Estado Actual:** El "Monolito Estable" se ha consolidado en producción con ~1736 productos tras arreglar el scraper de HSN (DOM Hyvä Theme).
- El catálogo funciona en una estructura plana (un Producto incluye su precio y url de afiliado directamente).
- El sistema de Telegram (chollos) y el recolector de emails (Newsletter) operan perfectamente bajo este esquema.

## Bugs Críticos y UI (A corto plazo)
- Investigar error `failed to fetch` (posible CORS) en el formulario de la Newsletter al introducir un email.

## Backlog / Roadmap Técnico Pendiente
- **Migración a Multi-Tienda (Sprint 4):** Acometer en el futuro usando exclusivamente **Alembic** para gestionar las migraciones de base de datos de forma segura. El intento previo desestabilizó la base de datos local y la UI (Agotado masivo).
- **Algoritmo Antimonopolio:** Modificar la ordenación por defecto de `/api/productos` para evitar que HSN monopolice las primeras páginas del catálogo, fomentando la diversidad de marcas.

## Backlog de Negocio
- **Capado de Ofertas:** Implementar un umbral (ej. > 20% descuento) para que un producto se considere "Oferta". Los que no lo superen, se mostrarán en el catálogo normal con el precio actualizado, evitando que HSN sature la sección de chollos. Para Farma2Go, usar temporalmente solo el precio final como precio base.
- **Alternativa al Precio/Kg:** Dado que el parseo de Precio/Kg es inconsistente por el formato de las tiendas, priorizar mostrar el "Formato" (ej. "3,50€ - 50g" vs "63€ - 3kg") como fallback confiable.
