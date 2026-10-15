# Plan de Reparto Definitivo — Tus Suplementos
**Base:** auditoría recortada + verificación directa contra `main` (commit `52a8d90`, 2026-09-14) + revisión técnica del argumento JSONB/DISTINCT.

> **📌 Nota sobre `ingestor_generico.py` / Bulk / MyProtein (resuelta 2026-10):**
> Se optó por la **Opción B**: limpiar código obsoleto. Se eliminó `ingestor_generico.py` del repositorio y se quitaron las entradas `Bulk` y `MyProtein` de `tiendas_config.py`. Actualmente solo quedan las tiendas activas (SportLive, Pharma2Go) más el ingestor dedicado de HSN. Si se añaden tiendas nuevas en el futuro, se implementarán directamente con el patrón `Producto→Oferta` vigente.

---

## Reparto por persona

**Persona A — Backend / Arquitectura / Ingesta / Seguridad**
**Persona B — Frontend / SEO / Negocio**

Los números de hallazgo mantienen la numeración del audit recortado que me pasaste, más los añadidos marcados como `[NUEVO]`.

---

## Semana 1

| # | Tarea | Owner | Esfuerzo | Por qué ahora |
|---|---|---|---|---|
| 3.3 | `secure=IS_PROD` → fail-safe (`secure=not IS_LOCAL`) | **A** | Muy bajo | 10 minutos, evita cookie insegura por typo de env var |
| 3.4 | Verificar `email_verified` en login de Google | **A** | Muy bajo | 5 minutos |
| 4.3 | Salvaguarda anti thin-content en `normalizar_descripcion_ui` | **B** | Muy bajo | Evita descripciones de <80 caracteres en fichas |

---

## Semana 2

| # | Tarea | Owner | Esfuerzo | Notas |
|---|---|---|---|---|
| 2.5 | N+1 en `descubrir_stacks` / `obtener_perfil_publico`: agregar likes con `GROUP BY` y `selectinload` en stacks→productos | **A** | Medio | — |
| 1.4 | Ventana de alertas de precio: timestamp de inicio de ejecución o flag `alertado` en `Oferta` | **A** | Bajo | Evita alertas perdidas si el scrape tarda |
| 1.5 | Log de intentos CSRF fallidos (IP+UA) para poder diagnosticar falsos rechazos | **A** | Muy bajo | Es hardening, no bug — bajo esfuerzo, hacedlo de paso |
| 6.2 | Sección de reseñas de sabor en ficha de producto (endpoints `GET/POST /api/resenas` ya existen) | **B** | Bajo-Medio | UGC gratis, ayuda SEO + conversión |

---

## Semana 3

| # | Tarea | Owner | Esfuerzo | Notas |
|---|---|---|---|---|
| 6.3 | Tabla `ClicAfiliado` para atribución de clics por tienda/oferta | **A** | Bajo | Habilita decisiones de negocio con datos reales |
| 3.2 | JWT con `jti` + revocación (o documentar el riesgo si se pospone) | **A** | Medio | Puede posponerse a sprint siguiente si falta tiempo |
| 3.5 | Limpiar CORS: separar `origins` dev/prod, quitar IP de LAN | **A** | Muy bajo | Housekeeping |
| 5.3 | Deprecar `skip` en favor de `page` en `/api/productos` | **A** | Muy bajo | — |
| 2.6 | Explorar caché incremental en scraper HSN (o al menos rotar categorías por ejecución) | **A** | Medio | Empezar a diseñarlo, no necesariamente terminarlo este sprint |
| 6.4 | Badge "precio más bajo en 90 días" en `ProductCard` | **B** | Bajo | Depende de 6.1 (ya completada) |
| 5.4 | Mover filtros de `Catalog.tsx` a Zustand + memoización de `FilterSidebar` | **B** | Medio | Tech debt, no bloqueante |
| 5.5 | Sustituir `alert()` por `toast` en `GestorStacks.tsx`/perfil público | **B** | Muy bajo | — |
| 5.2 | Limpiar código muerto (`ProductViewTracker.tsx`) | **B** | Muy bajo | — |
| 6.5 | Segmentar newsletter semanal por categoría más vista del usuario | **B** | Medio | Sin infraestructura nueva, usa `HistorialVistas`/`Favorito` ya existentes |

---

## Backlog explícito (no este sprint, pero no lo perdáis)
- 2.1 completo (migración `JSON→ARRAY(String)` + filtrado 100% en SQL): **aplazado a propósito**. Retomarlo cuando el catálogo supere ~5.000-8.000 productos o cuando la latencia de `/api/productos` supere ~500ms de forma consistente — lo que ocurra primero. Con las mitigaciones ya aplicadas (quitar el outerjoin + estandarizar ingestores + selectinload), llegaréis holgados hasta ese umbral.
- 4.4 (SSR real para combinaciones de filtro, `/proteinas/isolate` etc.) — roadmap SEO a medio plazo, no bloquea nada operativo.
- 2.6 (caché incremental HSN) — diseñarlo en semana 3, ejecutarlo cuando el scrape empiece a acercarse al límite de la ventana de 6h del CRON.

---

## Reglas para no pisaros
1. PRs pequeños, uno por fila de la tabla.
2. Migraciones de índices/columnas: siempre por `dev-ofertas` primero, nunca directo a la rama de producción de Neon.
3. Si en algún momento alguien toca `/api/productos` fuera de lo acordado, avisadlo antes de mergear — es el fichero compartido más sensible.

---

## ✅ Completadas

Tareas verificadas contra el código fuente actual (2026-10-11):

| # | Tarea | Owner | Verificación |
|---|---|---|---|
| `[NUEVO]` | ~~Decidir y ejecutar la opción (a) o (b) sobre `ingestor_generico.py`~~ | **A** | Opción B aplicada: `ingestor_generico.py` eliminado, Bulk y MyProtein removidos de `tiendas_config.py`. Solo quedan SportLive, Pharma2Go y HSN. |
| 3.1 | ~~Rate limiting en `/api/login`, `/api/registro`, `/api/newsletter/subscribe`, `/api/auth/google` (slowapi)~~ | **A** | `slowapi` instalado (`requirements.txt` L38). `Limiter(key_func=get_remote_address)` en `main.py` L38. Decoradores: `/api/registro` 5/min (L697), `/api/login` 10/min (L721), `/api/auth/google` 10/min (L815), `/api/newsletter/subscribe` 3/hour (L1683). |
| 1.3 | ~~`selectinload` en `/api/productos`, `/comparar`, `/favoritos`, `/stacks/{id}`, `descubrir_stacks`, `obtener_perfil_publico`~~ | **A** | `selectinload(Producto.ofertas).selectinload(Oferta.historial_precios)` implementado en `main.py` (L548-549, L606-607, L989-992, L1642-1644, L1775-1777). |
| `[NUEVO]` | ~~Sacar el `outerjoin(Oferta)` del paso que extrae `id/sabor/objetivo` en `/api/productos`~~ | **A** | Verificado: 0 ocurrencias de `outerjoin` en `main.py`. La consulta de paginación ya no multiplica filas por joins innecesarios con Oferta. |
| `[NUEVO]` | ~~Estandarizar en los ingestores que `sabor` y `objetivo` se guarden siempre como lista~~ | **A** | `utils.py` L882-893: sanitización final que convierte `None→[]` y `str→[str]` para ambos campos. `hsn.py` L793-797: normalización explícita adicional antes de guardar. Todos los ingestores pasan por `clasificar_producto()` de `utils.py`. |
| 2.4 | ~~Índices en `Oferta.producto_id`, `Oferta.activo`, `Producto.categoria_id`, `Producto.marca_id` (+ compuesto `(activo, tienda)`)~~ | **A** | `models.py`: `index=True` en las 4 columnas FK/boolean + índice compuesto `ix_oferta_activo_tienda` via `__table_args__`. |
| 2.2 | ~~Sitemap con `generateSitemaps()` en lotes + endpoint interno ligero (`slug`+`updated_at`)~~ | **B** | `sitemap.ts` usa `generateSitemaps()` con chunks de 1000 contra `/api/internal/sitemap-batch`. Índice de sitemaps generado con `sitemap-index.xml/route.ts`. Ya procesado por Google. |
| 4.1 | ~~Paginación con `<Link href="?page=N">` real en `Pagination.tsx`~~ | **B** | `Pagination.tsx` usa `<Link>` de Next.js con `getPageUrl()` que genera `?page=N#catalogo` real y rastreable por Googlebot. |
| 4.2 | ~~JSON-LD: añadir `availability` + `priceValidUntil`~~ | **B** | `producto/[slug]/page.tsx` L139-140: `"availability": "https://schema.org/InStock"` y `"priceValidUntil"` con fecha dinámica (+7 días). |
| 6.1 | ~~Sparkline de historial de precios en ficha de producto~~ | **B** | `PriceHistoryChart.tsx` (260 líneas): componente completo con recharts, soporte multi-tienda, toggle 3m/1y, % de cambio, modo compact. Integrado en `ProductCard.tsx` y ficha de producto. |
