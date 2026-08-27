# 16. RENDIMIENTO Y ESCALABILIDAD

TusSuplementos maneja actualmente un catálogo aproximado de ~800 a 1000 productos. En esta escala, el rendimiento es excepcional. Sin embargo, al proyectar un crecimiento hacia decenas de miles de referencias y alto tráfico concurrente, surgen varios cuellos de botella que deben mitigarse.

## Cuellos de Botella Identificados

### 1. Búsqueda y "pg_trgm" (Trigramas)
**Nivel de Gravedad:** 🟠 Importante
**Descripción:** El sistema utiliza la extensión `pg_trgm` de PostgreSQL y la función `unaccent` para permitir búsquedas con tolerancia a erratas (typos) en el endpoint `/api/productos/live-search`.
```python
text_score = func.similarity(models.Producto.nombre, q).label("text_score")
query.order_by(text_score.desc())
```
**El problema:** Calcular el *similarity score* contra todas las filas de la tabla `productos` realiza un *Secuencial Scan* intensivo en CPU si no existe un índice GIN (Generalized Inverted Index) o GiST específico en la columna `nombre`. A partir de los 10,000 productos, la búsqueda en vivo (Live Search) experimentará una latencia inaceptable (>500ms).
**Recomendación:** Crear un índice GIN explícito para trigramas en PostgreSQL. Si la escala supera los 100K productos, migrar la búsqueda a un motor dedicado como **Meilisearch** o **ElasticSearch**.

### 2. Paginación Profunda (Offset/Limit)
**Nivel de Gravedad:** 🟡 Mejorable
**Descripción:** El catálogo usa paginación clásica basada en `limit` y `offset` (implícito por página).
**El problema:** En bases de datos SQL, `OFFSET 50000 LIMIT 100` obliga al motor a leer y descartar 50,000 filas antes de devolver las 100 solicitadas, destruyendo el rendimiento.
**Recomendación:** Implementar "Keyset Pagination" (Paginación por cursor) utilizando el `id` o la columna `precio` como punto de anclaje para la siguiente página.

### 3. Modelo de Datos "Plano" y Duplicidad
**Nivel de Gravedad:** 🔴 Crítico (Para la UX)
**Descripción:** Actualmente 1 Fila en `productos` = 1 SKU en 1 Tienda. Si HSN, Farma2Go y SportLive venden la misma proteína "Optimum Nutrition 100% Gold Standard", se crearán 3 filas distintas.
**El problema:** El usuario verá el mismo producto 3 veces repetido en el grid del catálogo, saturando la interfaz e impidiendo una comparación agrupada (ej. un botón "Comparar precios en 3 tiendas").
**Recomendación:** Acelerar el roadmap de la **V2 Multi-tienda**. Refactorizar la DB con Alembic para que `Producto` sea una entidad abstracta única, vinculada a una tabla `Ofertas` donde residan los precios de cada tienda.

### 4. Sistema de Ingestión Síncrono (Scraping)
**Nivel de Gravedad:** 🟠 Importante
**Descripción:** El actualizador de precios (`actualizador_precios.py`) raspa HSN y descarga feeds XML en serie de manera síncrona dentro del Runner de GitHub Actions.
**El problema:** Si HSN tarda en responder, o si se añaden 10 tiendas nuevas, el proceso excederá los tiempos máximos de ejecución y será frágil.
**Recomendación:** Desacoplar la ingesta mediante Colas de Mensajería (Celery + Redis). Un Worker dedicado descarga los feeds, otro Worker scrapea HSN (con IPs rotativas para evitar baneos), y ambos empujan los datos crudos a una base de datos temporal (Staging) antes del Upsert maestro.

### 5. Renderizado Frontend (React Hydration)
**Nivel de Gravedad:** 🟡 Mejorable
**Descripción:** El componente `<Catalog>` renderiza inicialmente un esqueleto y luego realiza un `fetch` en el cliente.
**El problema:** Esto produce un *Time To Interactive (TTI)* y *Largest Contentful Paint (LCP)* dependiente de la latencia de la API en Render, afectando las métricas Core Web Vitals de Google.
**Recomendación:** Elevar la petición de datos al Server Component (`page.tsx`) en Next.js, renderizar el catálogo inicial en el servidor, e hidratar los filtros en cliente, logrando un LCP casi instantáneo.

## Resumen de Rendimiento

| Capa | Estado Actual (1K items) | Estado Proyectado (50K items) |
| :--- | :--- | :--- |
| **API Endpoints** | 🟢 Muy Rápido (<100ms) | 🔴 Lento (Filtros complejos y LIKEs) |
| **Búsqueda** | 🟢 Tolerante y fluida | 🔴 Bloqueos de CPU por `similarity` |
| **Scraping** | 🟢 Confiable, 4 veces/día | 🟠 Frágil, riesgo de timeout o ban de IP |
| **Interfaz (UI)** | 🟢 Reactiva y limpia | 🔴 Grid infestado de productos duplicados |
