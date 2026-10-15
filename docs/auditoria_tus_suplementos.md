# Auditoría Técnica Extrema — Tus Suplementos
**Autor:** Revisión Principal Tech Lead / Arquitectura / SEO
**Alcance:** Backend (FastAPI/SQLAlchemy/Postgres), Frontend (Next.js/Tailwind), Ingestores, CRONs, SEO, Seguridad

---

## 1. Bugs Críticos y Fallos Silenciosos (P0)

### 1.4 🟠 Ventana de alertas de precio basada en reloj de pared, no en el ciclo de ejecución

```python
hace_una_hora = datetime.utcnow() - timedelta(hours=1)
ofertas_rebajadas = db.query(models.Oferta).filter(
    ...,
    models.Oferta.ultima_actualizacion >= hace_una_hora
).all()
```

El scraper de HSN puede tardar varios minutos (o más al escalar el catálogo). Si una bajada de precio se persiste al **inicio** del scrape y `generar_alertas()` se ejecuta más de 1 hora después (poco probable hoy, pero garantizado al escalar a 50k productos con más categorías/páginas), **la alerta se pierde para siempre** — no hay reintento ni cola.

**Fix:** capturar un timestamp `inicio_ejecucion = datetime.utcnow()` al arrancar `orquestador.py` y usar esa marca como límite inferior (en vez de "hace 1 hora"), o mejor: añadir una columna `alertado=False` a `Oferta` y consultar `WHERE alertado=False AND precio<precio_anterior`, marcando `alertado=True` tras encolar el email. Así el sistema es idempotente e independiente de cuánto tarde el scrape.

---

### 1.5 🟡 `verificar_csrf` puede romper clientes legítimos sin Origin/Referer

```python
if not origen_header:
    raise HTTPException(status_code=403, detail="Falta cabecera Origin (CSRF Protection)")
```
Algunos navegadores/proxies corporativos y ciertas peticiones `fetch` same-site en modo `no-referrer-when-downgrade` pueden omitir `Referer`. Esto puede causar **falsos rechazos silenciosos** (checkin diario, favoritos, likes) que el usuario reportará como "no funciona" sin que haya log de error real de negocio. Recomiendo loguear el intento fallido con IP+UA para poder diagnosticarlo, y considerar añadir un token CSRF de doble envío (`csrf_token` en cookie no-HttpOnly + header) como capa adicional, no solo Origin/Referer.

---

## 2. Cuellos de Botella y Escalabilidad

### 2.1 🔴 La paginación de `/api/productos` se hace en memoria de Python, no en SQL

Este es el hallazgo **más grave de todo el sistema**. El endpoint hace:

```python
datos_raw_duplicados = query.with_entities(
    models.Producto.id, models.Producto.sabor, models.Producto.objetivo
).all()   # TRAE TODAS LAS FILAS QUE MATCHEAN FILTROS, SIN LIMIT

datos_raw = [...]  # dedup en Python por el outerjoin con Oferta (multiplica filas)
datos_filtrados = [d for d in datos_raw if cumple_filtros_arrays(d)]  # filtro de sabor/objetivo EN PYTHON

total_resultados = len(datos_filtrados)
ids_pagina = [d.id for d in datos_filtrados[offset_real: offset_real + limit]]  # slice EN PYTHON
```

Con 1.000 productos y `outerjoin(Oferta)` (cada producto con ~2-3 ofertas activas), esto ya trae 2.000-3.000 filas por request. **A 50.000 productos, cada llamada al catálogo (incluida cada carga de página, cada cambio de filtro, cada visita SSR a Home/Categoría/Marca) traerá 100.000-150.000 filas a memoria de Python**, solo para tirar el 99.97% y quedarte con 36. Esto colapsará la RAM del proceso de Render y la latencia se irá a varios segundos por petición.

> **⚠️ Nota de actualización (2026-10-11):** La mitigación parcial del `outerjoin` ya fue aplicada (ver sección Completadas), pero el patrón fundamental de filtrado de `sabor`/`objetivo` en Python + `len()` en vez de `COUNT` SQL sigue presente. La reescritura completa con operadores `ARRAY`/`JSONB` nativos sigue pendiente para cuando el catálogo supere ~5.000-8.000 productos.

**Fix recomendado (reescritura del endpoint):**

1. Mover el filtro de `sabor`/`objetivo` a SQL usando el operador nativo de Postgres para JSON/array, en vez de Python:
```python
# Si sabor/objetivo se migran a ARRAY(String) con índice GIN (ver 2.3):
if sabores_lista:
    query = query.filter(models.Producto.sabor.overlap(sabores_lista))
if objetivos_lista:
    query = query.filter(models.Producto.objetivo.overlap(objetivos_lista))
```

2. Usar una subquery de precio mínimo en vez de join directo:
```python
precio_min_subq = (
    db.query(
        models.Oferta.producto_id,
        func.min(models.Oferta.precio).label("precio_min"),
    )
    .filter(models.Oferta.activo.is_(True))
    .group_by(models.Oferta.producto_id)
    .subquery()
)

query = (
    db.query(models.Producto.id)
    .outerjoin(precio_min_subq, precio_min_subq.c.producto_id == models.Producto.id)
    ...
)

total_resultados = query.count()  # COUNT en SQL, no len() en Python
ids_pagina = [
    r.id for r in query.order_by(...).offset(offset_real).limit(limit).all()
]
```

3. Solo entonces, con el lote de 36 IDs, cargar los objetos completos (como ya hace el código) con `selectinload` (ver 1.3, ✅ completada).

Esto reduce el trabajo por petición de "toda la tabla" a "36 filas + 1 COUNT indexado".

---

### 2.3 🟠 `sabor`/`objetivo` como `JSON` sin índice obliga a filtrar en Python

```python
sabor = Column(JSON, default=list)
objetivo = Column(JSON, nullable=True)
```
Postgres no puede indexar eficientemente un `JSON` (a diferencia de `JSONB`) y, tal como está escrito hoy, el filtro de sabor ni siquiera usa operadores JSON — se hace comparando en un bucle de Python (ver 2.1). Con GIN index sobre `ARRAY(String)` o `JSONB`, el filtro sería instantáneo incluso a millones de filas.

**Fix (migración):**
```python
from sqlalchemy.dialects.postgresql import ARRAY
sabor = Column(ARRAY(String), default=list, index=True)   # con GIN vía Alembic: 
# CREATE INDEX ix_productos_sabor_gin ON productos USING GIN (sabor);
```

---

### 2.5 🟡 N+1 en `descubrir_stacks` y `obtener_perfil_publico`

Por cada stack (hasta 6) se hace una query adicional a `stack_likes` dentro de un bucle Python, y `schemas.StackResponse.model_validate(s)` fuerza la carga lazy de `s.productos` con toda la cadena de `ProductResponse` (marca, categoría, ofertas, historial). Sin `selectinload` esto es fácilmente 30-50 queries por carga del Hub Social.

**Fix:** precomputar los likes con una sola query agregada (`GROUP BY stack_id`) y usar `selectinload(models.Stack.productos).selectinload(models.Producto.ofertas)`.

---

### 2.6 🟡 Scraper de HSN sin caché incremental — recorre todo el catálogo 4 veces al día

`hsn.py` no tiene noción de "solo productos nuevos/modificados desde la última vez" — recorre categorías y páginas completas, con `time.sleep(0.3-0.8s)` por producto. A 50.000 productos, cada ejecución tardaría **horas**, entrando en conflicto con la ventana de 6h del CRON y con el resto de tiendas TradeDoubler que comparten ventana.

**Fix:** usar `Last-Modified`/ETag si HSN los expone, o al menos limitar el recorrido completo a 1 vez/día y hacer las otras 3 ejecuciones solo sobre un subconjunto de categorías "volátiles" (ofertas, más vendidos), rotando categorías por ejecución.

---

## 3. Seguridad y Auth

### 3.2 🟠 JWT sin revocación — el logout no invalida nada

`ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7` (7 días) y el `logout` solo borra la cookie del navegador (`response.delete_cookie`). Si el token fue robado (XSS en otra parte del sitio, extensión maliciosa, red comprometida), sigue siendo válido durante toda la semana aunque el usuario "cierre sesión".

**Fix:** añadir un `jti` (UUID) al payload del JWT y una tabla/Redis set de tokens revocados verificada en `obtener_usuario_actual`, o migrar a access token corto (15 min) + refresh token rotativo almacenado en BD.

### 3.3 🟠 `secure=IS_PROD` depende de una única variable de entorno exacta

```python
IS_PROD = os.getenv("ENV") == "production"
...
response.set_cookie(..., secure=IS_PROD, ...)
```
Si en Render la variable se llama distinto o tiene un valor ligeramente distinto (`"Production"`, `"prod"`), `IS_PROD` será `False` **en producción real**, y la cookie de sesión se emitirá sin `Secure` — viajará en texto claro sobre HTTP si algún endpoint no fuerza HTTPS (o ante cualquier downgrade).

**Fix:** invertir la lógica por seguridad ("fail-safe"): asumir `Secure=True` salvo que se declare explícitamente entorno local:
```python
IS_LOCAL = os.getenv("ENV", "production") in ("local", "development")
secure=not IS_LOCAL
```

### 3.4 🟡 Verificación de Google login no comprueba `email_verified`

```python
idinfo = id_token.verify_oauth2_token(google_data.token, google_requests.Request(), client_id, clock_skew_in_seconds=10)
email = idinfo["email"]
```
No se valida `idinfo.get("email_verified")`. Un email de Google no verificado permitiría crear una cuenta suplantando un correo que no controla el atacante.

**Fix:**
```python
if not idinfo.get("email_verified"):
    raise HTTPException(status_code=401, detail="Email de Google no verificado")
```

### 3.5 🟡 Whitelist de CORS con IP de LAN filtrada al repositorio

```python
origins = [..., "http://192.168.64.1:3000", ...]
```
No supone un vector de explotación externo real, pero es higiene pobre: revela infraestructura de desarrollo dentro del código de producción. Separar `origins` por entorno (`ENV=local` añade las IPs de LAN, producción no las incluye nunca).

### 3.6 🟢 Nada de SQL Injection detectado
Todas las queries usan el ORM con bind parameters. El único acceso a SQL crudo (`send_telegram_deals.py` con `psycopg2`) usa placeholders `%s` correctamente. Bien.

---

## 4. SEO Técnico y Frontend

### 4.3 🟠 Riesgo de Thin Content por sobre-recorte de descripciones

`normalizar_descripcion_ui` corta agresivamente el texto en cuanto encuentra tags como "ingredientes:" o "beneficios de" **sin comprobar cuánto texto queda**. Para descripciones cortas de proveedor, esto puede dejar 1-2 frases (<100 caracteres) como única descripción única de la ficha de producto — contenido "thin" que Google penaliza en rastreo de e-commerce con miles de páginas similares.

**Fix:**
```python
t_recortado = t[:idx_corte].strip()
# Salvaguarda anti thin-content: si el recorte deja muy poco texto, usar el original
if len(t_recortado) < 80 and len(t) >= 80:
    t_recortado = t
t = t_recortado
```

### 4.4 🟡 Home renderiza solo el primer batch por SSR; el resto del catálogo depende 100% de cliente
`page.tsx` hace `fetch` inicial (`limit=36&page=1`, `revalidate: 3600`) — correcto para LCP de la página 1 — pero cualquier filtro (categoría vía `?categoria=`, búsqueda `?q=`) reconstruye el listado enteramente en cliente sin nuevo SSR, perdiendo la oportunidad de servir HTML indexable para combinaciones de filtro con volumen de búsqueda real (p. ej. "whey isolate vainilla"). Dado que ya existen rutas dedicadas (`/categoria/[slug]`, `/marca/[slug]`) con SSR, se recomienda extender ese patrón a combinaciones categoría+atributo (`/proteinas/isolate`, `/proteinas/vainilla`) tal como ya está en el roadmap, priorizándolo porque hoy es la mayor pérdida de tráfico orgánico potencial.

### 4.5 🟢 Cosas bien hechas
- `robots.ts`, `manifest.ts`, canonical tags en Home/Categoría/Marca/Producto: correctos.
- Uso de `next/image` con `sizes` y `fill` en `ProductCard` y ficha de producto: buena práctica para LCP/CLS.
- ISR con `revalidate: 3600` en listados: adecuado para catálogo que cambia varias veces al día.

---

## 5. Deuda Técnica y Limpieza de Código

### 5.2 Código muerto / comentarios de debug en frontend
```tsx
// ProductViewTracker.tsx
const token = "dummy"; // Dummy fallback to avoid refactoring entire effect logic...
```
Variable sin uso y comentario de "nota mental" dejado en producción. Eliminar.

### 5.3 Parámetros duplicados/ambiguos en `/api/productos`
`skip` y `page` coexisten resolviendo la ambigüedad con `skip if skip > 0 else (page-1)*limit` — si un cliente manda ambos, `page` se ignora silenciosamente. Elegir uno (recomendado `page`) y deprecar `skip` con un warning de log si se recibe.

### 5.4 Componentes cliente sin memoización en listas grandes
`FilterSidebar.tsx` recibe ~25 props (patrón "prop drilling" extremo) y se re-renderiza completo en cada tecla del buscador de marca (`brandSearch`). Con 50-100 marcas esto es aceptable, pero conviene:
- Mover el estado de filtros a un store (Zustand, ya usado para `compareIds`) en vez de prop-drilling desde `Catalog.tsx`.
- Envolver el `filterContent` en `useMemo` dependiente solo de las props que cambian.

### 5.5 Uso de `alert()` en `GestorStacks.tsx`/perfil público
`alert(data.mensaje)` para feedback de seguir/no-seguir usuario — UX pobre y bloqueante, además de inconsistente con el resto de la app que ya usa `react-hot-toast`. Sustituir por `toast.success(...)`.

---

## 6. Oportunidades de Negocio y Monetización

### 6.2 🟦 Reseñas de sabor: backend listo, cero superficie en UI
Endpoints `GET/POST /api/resenas` existen y funcionan (`ResenaSaborResponse` con autor/foto), pero `producto/[slug]/page.tsx` no tiene ninguna sección de reseñas. Esto es contenido generado por usuario (UGC) gratuito que:
1. Mejora SEO (contenido único, fresco, con menciones de sabor/marca).
2. Aumenta confianza de conversión igual que en Amazon.
Prioridad alta: añadir sección "Opiniones sobre el sabor" en la ficha de producto.

### 6.3 🟦 Atribución de clics solo a nivel de producto, no de oferta/tienda
`/api/out/{tienda}/{slug}` incrementa `producto.clics_count` (agregado), pero no registra **qué tienda concreta** generó el clic, ni marca temporal. Sin esto es imposible saber qué tienda convierte mejor por categoría.

**Fix (tabla nueva, barata de implementar):**
```python
class ClicAfiliado(Base):
    __tablename__ = "clics_afiliados"
    id = Column(Integer, primary_key=True)
    oferta_id = Column(Integer, ForeignKey("ofertas.id"), index=True)
    tienda = Column(String, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, index=True)
```

### 6.4 🟦 CTR de afiliación: micro-urgencia sin fricción de UX
El botón "Ver oferta" es siempre idéntico. Con el historial de precios (6.1, ✅ completada) ya disponible, se puede mostrar un badge condicional:
- "Precio más bajo de los últimos 90 días" (cuando `precio == min(historial_precios)`).
- "Sube pronto: subió un X% la semana pasada" (cuando hay tendencia alcista detectable).

### 6.5 🟦 Newsletter/Retargeting: sin segmentación por categoría de interés
`newsletter_semanal.py` envía el mismo Top 5 a todos los suscriptores. Segmentar el Top 5 por categoría más vista de cada suscriptor subiría el CTR del email sin coste de infraestructura adicional relevante.

---

## Resumen de Prioridades Inmediatas (siguiente sprint)

| # | Hallazgo | Categoría | Esfuerzo | Impacto |
|---|----------|-----------|----------|---------|
| 2.1 | Reescribir paginación de `/api/productos` en SQL | Escalabilidad | Alto | Crítico (bloquea crecer de 1k a 50k) |
| 3.3 | Fail-safe en `secure` cookie | Seguridad | Muy bajo | Medio (evita cookie insegura en prod) |
| 3.4 | Verificar `email_verified` en Google login | Seguridad | Muy bajo | Medio (suplantación de email) |
| 6.2 | Exponer reseñas de sabor en la ficha | Negocio | Bajo-Medio | Alto (conversión, SEO UGC) |

---

## ✅ Completadas

Hallazgos verificados contra el código fuente actual (2026-10-11):

| # | Hallazgo | Categoría | Verificación |
|---|----------|-----------|-------------|
| 1.3 | ~~N+1 en la carga de `ofertas` y `historial_precios` en `/api/productos`~~ | P0 — Bug | `selectinload(Producto.ofertas).selectinload(Oferta.historial_precios)` aplicado en `main.py` en todos los endpoints: `/api/productos` (L548-549), `/comparar` (L606-607), `obtener_perfil_publico` (L989-992), `/favoritos` (L1642-1644), `/stacks/{id}` (L1775-1777). |
| `[NUEVO]` | ~~Sacar el `outerjoin(Oferta)` del paso que extrae `id/sabor/objetivo` en `/api/productos`~~ | Escalabilidad | Verificado: 0 ocurrencias de `outerjoin` en `main.py`. La consulta de paginación ya no multiplica filas por joins innecesarios con Oferta. |
| `[NUEVO]` | ~~Estandarizar que `sabor` y `objetivo` se guarden siempre como lista en los ingestores~~ | Escalabilidad | `utils.py` L882-893: sanitización final `clasificar_producto()` que convierte `None→[]` y `str→[str]` para ambos campos. `hsn.py` L793-797: normalización explícita adicional. Todos los ingestores (HSN, Pharma2Go, SportLive) pasan por esta función. |
| 2.2 | ~~El sitemap hace hasta 250+ fetches HTTP secuenciales~~ | Escalabilidad | Reescrito en `sitemap.ts` con `generateSitemaps()` + chunks de 1000 productos via `/api/internal/sitemap-batch`. Índice XML en `sitemap-index.xml/route.ts`. Ya procesado por Google. |
| 2.4 | ~~Faltan índices en columnas de join/filtro muy usadas~~ | Escalabilidad | `models.py`: `index=True` en `Oferta.producto_id`, `Oferta.activo`, `Producto.categoria_id`, `Producto.marca_id` + índice compuesto `ix_oferta_activo_tienda(activo, tienda)` via `__table_args__`. |
| 3.1 | ~~Sin Rate Limiting en ningún endpoint~~ | Seguridad | `slowapi` instalado (`requirements.txt` L38). `Limiter(key_func=get_remote_address)` configurado en `main.py` L38. Decoradores aplicados: `/api/registro` 5/min (L697), `/api/login` 10/min (L721), `/api/auth/google` 10/min (L815), `/api/newsletter/subscribe` 3/hour (L1683). Handler de error registrado con `_rate_limit_exceeded_handler`. |
| 4.1 | ~~Paginación no rastreable — contenido "fantasma" para Google~~ | SEO | `Pagination.tsx` refactorizado: usa `<Link>` de Next.js con `href={getPageUrl(page)}` generando URLs reales `?page=N#catalogo`. Googlebot puede rastrear todas las páginas. |
| 4.2 | ~~JSON-LD de producto incompleto para Rich Results~~ | SEO | `producto/[slug]/page.tsx` L139-140: `"availability": "https://schema.org/InStock"` y `"priceValidUntil"` con fecha dinámica (+7 días). Rich snippets elegibles. |
| 6.1 | ~~Historial de precios: modelado al 100%, visible al 0%~~ | Negocio | `PriceHistoryChart.tsx` (260 líneas): componente completo con recharts, soporte multi-tienda con colores diferenciados, toggle 3m/1y, indicador de % de cambio, modo compact. Integrado en `ProductCard.tsx` y ficha de producto. |
