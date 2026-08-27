# 18. RIESGOS DEL PROYECTO

Esta sección consolida el mapa de calor de todos los riesgos detectados en la auditoría, clasificados por dominio, impacto y probabilidad, ofreciendo recomendaciones procesables.

## Riesgos Técnicos

### 1. `SECRET_KEY` de Autenticación Expuesta
*   **Gravedad:** 🔴 Crítica.
*   **Probabilidad:** Muy Alta (Si el repositorio es público o se compromete el servidor).
*   **Descripción:** La clave secreta del JWT está *hardcodeada* en `backend/security.py`. Esto permite la falsificación de tokens de sesión para cualquier usuario (incluyendo administradores) bypassando Google OAuth.
*   **Recomendación:** Migrar inmediatamente al archivo `.env` mediante `os.getenv("JWT_SECRET_KEY")` y rotar/cambiar la contraseña.

### 2. Paginación Profunda Ineficiente
*   **Gravedad:** 🟡 Moderada (Afectará a largo plazo).
*   **Probabilidad:** Alta (Al superar 10K productos).
*   **Descripción:** Usar `OFFSET` en SQLAlchemy fuerza a PostgreSQL a escanear miles de filas descartables.
*   **Recomendación:** Implementar "Keyset Pagination" o Paginación por Cursor.

## Riesgos SEO

### 3. Ausencia de Esquemas de Datos (JSON-LD)
*   **Gravedad:** 🔴 Crítica.
*   **Probabilidad:** 100% (Detectado actualmente).
*   **Descripción:** El e-commerce no declara metadatos de tipo `Product` ni `Offer`. Googlebot será incapaz de habilitar *Rich Snippets* (precios, stock, valoraciones) en las SERPs, hundiendo el CTR orgánico frente a la competencia.
*   **Recomendación:** Inyectar esquema JSON-LD en la cabecera de la plantilla dinámica `[slug]`.

### 4. Orfandad de Landings Comerciales
*   **Gravedad:** 🟠 Alta.
*   **Probabilidad:** 100% (Diseño actual).
*   **Descripción:** Los filtros actuales del catálogo (ej. `/?categoria=proteinas`) se ejecutan vía Javascript en el Cliente (CSR) mutando querystrings. No hay rutas físicas SSR como `/categoria/proteinas` que alojen `<h1>` y contenido semántico indexable. El sitio no posicionará para *mid-tail keywords*.
*   **Recomendación:** Crear rutas dinámicas con App Router en `/app/categoria/[id]/page.tsx` con SSR puro.

### 5. Canibalización de URLs Dinámicas
*   **Gravedad:** 🟠 Alta.
*   **Probabilidad:** Alta.
*   **Descripción:** Si el archivo `robots.txt` no bloquea los parámetros de ordenación (`?orden=precio_asc`, `?solo_ofertas=true`), Google indexará docenas de páginas con contenido idéntico, penalizando por contenido duplicado.
*   **Recomendación:** Añadir `Disallow: /*?orden=*` en el robots.txt y asegurar el tag `<link rel="canonical">` apuntando a la URL base.

## Riesgos de Escalabilidad y UX

### 6. Explosión de SKUs Duplicados en Catálogo
*   **Gravedad:** 🔴 Crítica.
*   **Probabilidad:** Alta.
*   **Descripción:** El modelo actual inserta un nuevo Producto por cada Tienda. El mismo bote de proteínas aparecerá repetido si lo venden 3 tiendas, arruinando la usabilidad de la web.
*   **Recomendación:** Migración Urgente a V2. Unificar SKUs bajo un Modelo Maestro (Tabla Producto abstracto) y anidar los precios en una Tabla hija (Ofertas).

## Riesgos de Afiliación y Monetización

### 7. Bloqueo de URLs de Tradedoubler (AdBlockers)
*   **Gravedad:** 🔴 Crítica.
*   **Probabilidad:** 40% (Adopción actual de adblockers en navegadores).
*   **Descripción:** Los botones de "Ver Oferta" contienen los links sucios directos a redes de afiliación (`clk.tradedoubler...`). Brave Browser o uBlock Origin bloquearán los clicks del usuario o eliminarán el componente de la pantalla, reduciendo severamente las conversiones.
*   **Recomendación:** Construir un Cloaker Interno. Redirigir siempre a `/out/producto-slug` (dominio local) y en el Backend responder con un HTTP 302 a la URL de afiliado real.

### 8. Falsos Chollos (Falta de MSRP)
*   **Gravedad:** 🟠 Alta.
*   **Probabilidad:** Alta (Típico en feeds XML).
*   **Descripción:** Los ingestores confían ciegamente en el `precio_anterior` provisto por Tradedoubler, el cual a menudo es erróneo o inventado por la tienda para fingir rebajas. Esto inunda el canal de Telegram con falsas alarmas, erosionando la confianza del usuario.
*   **Recomendación:** Desarrollar un **Price History Engine** propio que calcule la media móvil de 30 días de cada producto y la use como precio base real.

## Riesgos de Dependencia de Terceros

### 9. Ban de IP por Scraping (HSN)
*   **Gravedad:** 🟠 Alta.
*   **Probabilidad:** Media (Si aumenta la frecuencia o concurrencia).
*   **Descripción:** El scraper de HSN se ejecuta desde las IPs de GitHub Actions. Si HSN implementa protecciones como Cloudflare Bot Management severas, el ingestor colapsará.
*   **Recomendación:** Preparar un proveedor de Proxies Residenciales o rotativos para emergencias.

## Riesgos Legales o de Licencias
*   **Gravedad:** 🟢 Baja (Ninguno detectado).
*   **Descripción:** Todas las dependencias son OSS permisivas (MIT, BSD, Apache). Ningún riesgo de copyleft o infección de patente detectado. GDPR compliance requerirá asegurar que `/cookies` funciona y se guarda el consentimiento antes de encender GA4 (Actualmente GA4 se dispara siempre en `layout.tsx`).
