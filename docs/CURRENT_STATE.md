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

## Hitos Recientes (V1 Release Candidate)

### 1. Modo Versus (Comparador Multi-tienda Premium)
- Tabla comparativa cara a cara de hasta 4 productos simultáneos.
- Mapeo dinámico e inteligente de características (ocultando filas vacías de forma automática).
- Acceso directo a la compra mediante enlaces de afiliado y botones de conversión limpios.
- Sincronización de estado en el cliente mediante Zustand, con soporte de toggle directo desde el catálogo (botón "VS" persistente).

### 2. Ecosistema Social y Gamificación (Backend & Frontend)
- Sistema de perfiles de usuario únicos (`@username`) con biografías y avatares.
- Red social de seguidores (capacidad de seguir y dejar de seguir a otros perfiles).
- Creación de *Stacks*: Listas públicas y compartibles con las rutinas personalizadas de suplementación de cada usuario.
- Sistema de gamificación integrado con *Check-in* diario, cálculo de rachas y asignación de puntos de experiencia (XP) con bonus semanales por constancia.

### 3. Motor NLP y Clasificación Quirúrgica
- Análisis léxico avanzado (Cerebro NLP) para la detección automática de formatos físicos (polvo, cápsulas, líquido, barritas, gominolas).
- Detección precisa de sabores mediante un diccionario gourmet ampliado, capaz de identificar neutros y variantes complejas.
- Etiquetado automático de alérgenos y porcentajes de proteína, operando en tiempo de ingesta sin requerir intervención humana.

### 4. Arquitectura Multi-Tienda y Orquestación (Fase 2)
- **Migración a Arquitectura Multi-Tienda:** El "Monolito Estable" plano ya no existe. El catálogo funciona bajo un modelo relacional (Producto 1:N Oferta). El comparador multi-tienda real ya opera en el núcleo de la base de datos.
- **Motor de Historial de Precios:** Desarrollado y operativo. La base de datos registra las variaciones en la tabla `precios_historicos` y la API (`schemas.py`) las expone cronológicamente anidadas en cada Oferta.
- **Orquestador de CRONs y Límites de API:** Se ha eliminado el obsoleto actualizador de precios. Ahora opera un `orquestador.py` inteligente mediante bloques de 6 horas, garantizando 4 actualizaciones diarias para HSN y 2 para TradeDoubler (Farma2Go y Sportlive) para evitar baneos HTTP 429.
- **Refactorización NLP y Doble Barrera:** Se ha purgado definitivamente la basura de cosmética/veterinaria implementando un Filtro de Doble Barrera (Lista Negra inicial y Lista Blanca restrictiva al título) en los ingestores.
- **Seguridad Parcheada:** Las vulnerabilidades de claves `SECRET_KEY` hardcodeadas y exposición de secretos han sido parcheadas; el sistema utiliza variables de entorno rotadas y seguras de forma estricta.

## Tareas Completadas (Checklist Reciente)
- [x] **[NUEVO] Refactorización DRY de Ingestores:** Lógica de clasificación (NLP, alérgenos, sellos) y cálculo de precio/kg centralizada de forma exclusiva en el cerebro `utils.py`. Los scripts `pharma2go.py`, `sportlive.py` y `hsn.py` ahora actúan como clientes limpios y robustos.
- [x] **[NUEVO] Upsert Masivo y Seguro:** Los ingestores detectan productos existentes, actualizan todos sus campos dinámicamente con el método seguro `.get()` y validaciones `bool()`, realizando un único `db.commit()` por lote para optimizar transacciones en PostgreSQL.
- [x] **[NUEVO] Sincronización Oficial de BD:** Despliegue de `backend/scripts/reprocesar_nlp.py` como herramienta oficial para re-etiquetar todo el catálogo rápidamente sin necesidad de re-scrapear la web, conservando datos críticos como tamaños (`presentacion`).
- [x] **[NUEVO] UI/UX Premium:** Eliminada la renderización visual de "precio por kilo" en la `ProductCard` principal y el modal Quick View, logrando un diseño visual mucho más limpio, manteniendo el dato intacto en el backend.
- [x] **[NUEVO] Infraestructura Vercel:** Aprobación explícita de `allowScripts` en `package.json` para garantizar la compilación correcta de dependencias de frontend como `sharp` (optimización de imágenes).
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
- [x] El bot de Telegram está desplegado con Strict CI/CD y 100% operativo en producción. Los CRON programados inyectan correctamente los Secrets (tokens) y los mensajes llegan al canal sin incidencias varias veces al día.
- [x] El bot de Telegram está desplegado con Strict CI/CD y 100% operativo en producción.
- [x] **[NUEVO] Endpoint Comparador:** Creación de `GET /api/productos/comparar` blindado (máx. 4 productos) para nutrir la nueva UI del "Modo Versus", manteniendo el orden exacto de peticiones y devolviendo el objeto estructurado.
- [x] **[NUEVO] Arquitectura Social en BD:** Despliegue de la Fase 1 del "IG de Suplementos" en Neon DB. Creación de las tablas puente e identidades: `perfiles`, `seguidores`, `stacks`, `resenas_sabores` y `checks_diarios`.
- [x] **[NUEVO] Motor Social API (Perfiles & Followers):** Endpoints para crear un `@username` único asociado 1:1 a la cuenta de usuario. Implementación de lógica de seguidores con protección anti-bucle (no seguirse a uno mismo).
- [x] **[NUEVO] Stacks (Rutinas):** Endpoints para agrupar productos (`ProductResponse` completo) en listas públicas compartibles, reutilizando la lógica del catálogo.
- [x] **[NUEVO] Motor de Gamificación:** Endpoint `POST /api/comunidad/checkin` que premia la constancia diaria mediante Rachas (Streaks) y puntos de Experiencia (XP), con sistema anti-trampas (un solo check por día).
- [x] **[NUEVO] Fix de Seguridad de Entorno:** Creación de la puerta trasera `/api/login/swagger` compatible con `OAuth2PasswordRequestForm` para permitir el testeo seguro de los endpoints sociales privados.

## Sprint 3: Monolito Estable Restaurado (Legado)
- **Estado Histórico:** El "Monolito Estable" se consolidó exitosamente, sirviendo de base para la posterior migración a la Fase 2 (Multi-Tienda).

## Backlog / Roadmap Técnico Pendiente
- **Frontend - UI Historial de Precios:** Consumir el array `historial_precios` desde Next.js para renderizar componentes visuales (gráficas interactivas) en la ficha de cada producto.
- **Arquitectura SEO y Rutas Dinámicas:** Migrar la dependencia actual de parámetros de búsqueda (`/?categoria=proteinas`) hacia páginas SSR/ISR reales (`/proteinas/whey`, `/marcas/hsn`, `/comparar/hsn-vs-myprotein`) para potenciar el indexado en Google.
- **Sistema de Medición y Analytics (Funnel):** Implementar tracking avanzado en Next.js conectado a GA4 para trazar el flujo completo del usuario (desde la vista de categoría hasta el clic de afiliado `CLICK_AFFILIATE`).
- **Algoritmo de Ranking Antimonopolio:** Refinar la ordenación de `/api/productos` creando un SCORE combinado (relevancia + calidad + precio + clics) para evitar que una sola tienda monopolice las primeras páginas.

## Backlog de Negocio
- **Alternativa al Precio/Kg:** Dado que el parseo de Precio/Kg es inconsistente por el formato de las tiendas, priorizar mostrar el "Formato" (ej. "3,50€ - 50g" vs "63€ - 3kg") como fallback confiable en la UI.
## Historial de Actualizaciones / Anexos

### Anexo: Hito de Alérgenos y Estabilidad NLP

#### 1. Mejora en el Sistema de Ingestión (Farma2Go y Sportlive)
Se ha implementado una capa de detección avanzada de alérgenos sin alterar la estructura central del pipeline.
- **Parche Quirúrgico:** Se ha inyectado lógica de escaneo en las funciones locales `clasificar_producto` de los módulos `pharma2go.py` y `sportlive.py`. Esta lógica habilita la identificación precisa de los flags `sin_gluten` y `sin_lactosa`.
- **Motor de Variaciones Léxicas:** La detección evalúa el texto completo extraído del proveedor contra un array exhaustivo de variaciones semánticas y comerciales (ej. *"gluten free"*, *"0% lactosa"*, *"libre de..."*, *"zero lactose"*), garantizando una cobertura total frente a nomenclaturas inconsistentes de terceros.

#### 2. Mantenimiento Estratégico de la Arquitectura Híbrida
Se ha dictaminado una política de contención arquitectónica respecto al Cerebro Central NLP (`utils.py`).
- **Aislamiento de Riesgos:** Para evitar desestabilizar el catálogo actual en producción, se ha optado por mantener operativos los clasificadores locales independientes de Farma2Go y Sportlive, posponiendo una migración completa al clasificador centralizado.
- **Garantía de Estabilidad:** Esta decisión técnica garantiza **cero colisiones** en la asignación de categorías base (Proteínas, Aminoácidos, etc.) procedentes de estas tiendas y salvaguarda de forma estricta la integridad de los filtros de navegación del frontend.
