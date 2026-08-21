# Estado Actual del Proyecto

## Dominio y Entorno Operativo
*   **Dominio Oficial Activo (Canónico):** [https://www.tussuplementos.com](https://www.tussuplementos.com) (con redirección desde .es)
*   **Backend URL:** Desplegado en Render (o similar configurado).
*   **Frontend URL:** Desplegado en Vercel.

## Estado de la Base de Datos
*   **Motor:** PostgreSQL (Neon DB).
*   **Catálogo Actual:** HSN 100% integrado y purgado. El gran logro reciente ha sido aislar con éxito y precisión las marcas externas que vende HSN (ej. 142 productos de Swanson, 90 de NOW Foods, 19 de Vitaminalia) gracias al nuevo motor de extracción, lo que diversifica enormemente el catálogo.
*   **Volumen:** Más de 800 productos clasificados e ingestados correctamente.
*   **NLP:** Catálogo de HSN 100% re-etiquetado con flags de alérgenos (Sin Gluten / Sin Lactosa) y categorías NLP en cascada.
*   **Limpieza:** Las marcas huérfanas de pruebas anteriores han sido purgadas de la tabla maestra de `marcas`. La normalización agrupa todas las gamas de HSN bajo el paraguas de HSN y aísla las marcas externas reales.
*   **Entornos Segregados:** Uso activo de Neon DB con ramas separadas (Producción frente a la nueva rama `dev-ofertas` para staging), protegiendo la integridad de los datos reales durante el desarrollo de nuevas lógicas de precios.

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
- [x] Implementación de un embudo de 4 Fases (JSON-LD, URL, HTML, Regex en nombre/title) para la extracción infalible de marcas de terceros en el scraper de HSN.
- [x] Corrección crítica de la lógica de guardado (Upsert / `db.commit()`) para garantizar que las actualizaciones y nuevos productos se persisten correctamente en Neon DB.
- [x] Ampliación del diccionario del Cerebro Central NLP (`utils.py`) para rescatar productos atrapados en categorías fantasma (Otros/Accesorios), integrando nuevas reglas para "gainer", vitaminas (B-Complex, coenzimas) y depurativos.
- [x] Arreglo del scraper de HSN (DOM Hyvä Theme), certificando que el Monolito Estable es totalmente robusto.
- [x] Preparación y estabilización total de la rama `fix-bugs-ui`, dejándola lista para su paso a producción (`main`).
- [x] Implementación de umbrales dinámicos de ofertas en HSN (30% Proteínas/Creatinas, 40% Aminoácidos, 50% resto) para regular el sistema antimonopolio.
- [x] Centralización de la lógica de alérgenos (`es_vegano`, `sin_gluten`, `sin_lactosa`) en el Cerebro NLP (`utils.py`).
- [x] Diagnóstico completado del feed de Tradedoubler (Farma2Go) y mapeo de limitaciones de precios base.
- [⏳ PENDIENTE DE VERIFICACIÓN] El bot de Telegram está desplegado con Strict CI/CD. Queda confirmar que el CRON programado inyecta correctamente los Secrets en modo desatendido.

## Sprint 3: Monolito Estable Restaurado
- **Estado Actual:** El "Monolito Estable" se ha consolidado en producción de manera impecable.
- El catálogo funciona en una estructura plana (un Producto incluye su precio y url de afiliado directamente).
- El sistema de Telegram (chollos), el motor de retargeting y el recolector de emails (Newsletter) operan perfectamente bajo este esquema.

## Bugs Críticos y UI (A corto plazo)
- Investigar error `failed to fetch` (posible CORS) en el formulario de la Newsletter al introducir un email.

## Backlog / Roadmap Técnico Pendiente
- **Migración a Multi-Tienda (Sprint 4):** Acometer en el futuro usando exclusivamente **Alembic** para gestionar las migraciones de base de datos de forma segura. El intento previo desestabilizó la base de datos local y la UI (Agotado masivo).
- **Algoritmo Antimonopolio:** Modificar la ordenación por defecto de `/api/productos` para evitar que HSN monopolice las primeras páginas del catálogo, fomentando la diversidad de marcas.

## Backlog de Negocio
- **Motor de Historial de Precios Propio:** Desarrollar un sistema para registrar el histórico de precios independiente de los feeds de afiliados. Esto es imperativo para compensar la falta de precio base (MSRP) fiable en plataformas como Tradedoubler (Farma2Go) y garantizar el cálculo real de ofertas a largo plazo.
- **Capado de Ofertas (Farma2Go):** Hasta que exista el Motor de Historial, se ha decidido utilizar temporalmente solo el precio final como precio base, evitando inyectar falsos chollos al sistema.
- **Alternativa al Precio/Kg:** Dado que el parseo de Precio/Kg es inconsistente por el formato de las tiendas, priorizar mostrar el "Formato" (ej. "3,50€ - 50g" vs "63€ - 3kg") como fallback confiable en la UI.
