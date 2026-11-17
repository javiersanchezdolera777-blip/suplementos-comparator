**TUS SUPLEMENTOS  /  PLAN DE DESARROLLO Y CRECIMIENTO**

*TUS SUPLEMENTOS*

**Plan maestro de desarrollo\
y crecimiento**

De comparador funcional a comparador de referencia en España

Diagnóstico consolidado · Roadmap técnico, SEO, producto y negocio · 17 de noviembre de 2026

|**Situación actual**|**Objetivo de la siguiente etapa**|
| :- | :- |
|Producto en producción y Fase SEO técnica 1 fusionada; operación real y primeras señales orgánicas.|Cerrar deuda crítica de escalabilidad y confianza antes de ampliar el catálogo o multiplicar páginas indexables.|
|253 páginas indexadas en captura del 12/11; 2.095 URLs descubiertas; 90 clics / ~1.110 impresiones en 3 meses.|Aumentar páginas útiles que reciben clics, mejorar conversión y repetición de uso; medir por cohortes y consultas.|

## **Principio rector**
No perseguir “ser el número 1” mediante más URLs o más código. Construir la comparación más fiable, rápida y útil: precios comparables, ofertas verificadas, €/kg o €/dosis cuando proceda, historial transparente, fichas navegables y datos consistentes.
## **Uso del documento**
Documento de trabajo para Javier y Diego. Separa evidencia, hallazgos de código, hipótesis y decisiones pendientes. Las prioridades son puertas de calidad: nada se escala ni se despliega directamente a producción sin rama, pruebas y Preview.


# **1. Resumen ejecutivo**
Mi diagnóstico: el proyecto tiene una propuesta de valor defendible y varias piezas de producto que pueden diferenciarlo de una tienda individual: comparación multi-comercio, normalización de productos, métricas de precio unitario, historial, alertas, Telegram y comunidad. Pero aún no está en “fase final” desde el punto de vista de robustez y crecimiento. Hay deuda técnica real en rutas calientes y automatizaciones, y la ejecución SEO debe concentrarse en páginas rastreables con utilidad diferencial.

|**Área**|**Estado observado**|**Decisión**|
| :- | :- | :- |
|SEO técnico base|Fase 1 fusionada (PR #137, 03/11) y sitemap procesado correctamente en capturas del 12/11.|No rehacer sitemap/robots. Pasar a enlazado interno, landings válidas, fichas y rendimiento.|
|SEO orgánico|253 indexadas; 1.847 descubiertas sin indexar; 32 rastreadas sin indexar; 66 redirecciones en el corte del 12/11.|Auditar inventario y páginas con potencial; no indexación masiva.|
|Ranking “comparador de suplementos”|El usuario recuerda posición 3–4 y ahora no ve la web. La captura GSC no demuestra la trayectoria de esa consulta por sí sola.|Core Update de noviembre en curso; aislar query/país/dispositivo/página antes de tocar contenido.|
|Escalabilidad/backend|/api/productos materializa resultados antes de paginar; ingestores hacen carga completa de catálogo; N+1 en alertas; índices faltantes.|Bloqueante antes de ingesta masiva y más catálogo.|
|Operación/automatizaciones|Desajuste confirmado en timestamp Telegram/cooldown; runtimes Python mezclados y sin timeout explícito en cron.|Reparar y añadir observabilidad/idempotencia antes de crecer.|
|Frontend/SEO|ProductCard depende de modal para enlace a ficha; enlaces afiliados con rel inconsistente; H1 genérico; landings pueden ser vacías 200.|Primer PR acotado de discoverability y afiliación; segundo PR de landings.|
|Rendimiento web|Diagnóstico facilitado: móvil PageSpeed 63, LCP 6,2 s, FCP 2,7 s, TBT 390 ms; evidencia antigua sin URL/fecha exacta del test.|Repetir PSI y CrUX/field data antes de atribuir causa; tratar como prioridad comercial.|
|Crecimiento/producto|Estrategia pSEO, €/kg, sellos, UGC, rankings, retención y CSS.|Secuenciar. No lanzar páginas programáticas a gran escala hasta tener calidad de datos y gates.|

## **Conclusión ejecutiva**
La ruta no es “SEO primero a cualquier precio”. Es: (1) estabilizar ingestión y consultas críticas, (2) asegurar confianza del dato y experiencia móvil, (3) facilitar rastreo y conversión de fichas, (4) publicar un pequeño conjunto de landings valiosas, (5) escalar páginas programáticas y canales de retención basados en datos reales.
# **2. Alcance y fuentes**
- Repositorio: javiersanchezdolera777-blip/suplementos-comparator, rama por defecto main. Últimas PR consultadas: #137 SEO Phase 1 (fusionada 03/11), #136 orquestador, #135 preparación ingesta masiva, #134 índices y #133 fixes ingestores (todas fusionadas en octubre/noviembre según GitHub).
- Informe SEO con corte 12/11/2026 (20 páginas), CSV Tabla(1).csv de 66 URLs, Diagnóstico Core Web Vitals, ESTRATEGIA SEO y Auditoría técnica, más message (18).
- Revisión estática selectiva del main el 17/11: main.py, models.py, ingestores Farma2Go/Sportlive/utils, orquestador.py, send\_telegram\_deals.py, reset\_cooldown.py, workflows y componentes SEO del frontend.
- Web research oficial: actualización de ranking de noviembre, guía de Google para investigar caídas, guías de datos estructurados Product y requisitos CSS. No se ha accedido a Search Console, PageSpeed ni producción de forma autenticada; cifras GSC proceden de capturas.
## **Limitaciones importantes**
- No se aportó exportación completa de las 1.847 URLs descubiertas sin indexar ni de las 32 rastreadas; el CSV de redirecciones no incluye status HTTP ni Location.
- No se ha inspeccionado la base de datos de producción ni ejecutado el crawler contra todas las rutas; las conclusiones de código son estáticas y requieren pruebas.
- La auditoría técnica es un documento de hallazgos, no prueba que todos los riesgos se manifiesten con el volumen actual. Las tareas deben validarse con trazas, consultas y pruebas de carga.
- El informe de CWV no identifica con certeza el elemento LCP ni incluye fecha/URL/perfil de laboratorio; no aplicar su propuesta literal de priority a más imágenes sin volver a medir.
# **3. Diagnóstico SEO y por qué desapareció “comparador de suplementos”**
## **3.1. Foto de Search Console (corte 12/11)**

|**Indicador**|**Dato capturado**|**Lectura correcta**|
| :- | :- | :- |
|Indexadas|253|Subida desde 40 (dato anterior comunicado). La coincidencia temporal con Fase 1 no prueba causalidad exclusiva.|
|Descubiertas por sitemap|2\.095: 1.018 + 1.000 + 77|Los tres hijos están en estado Correcto. Descubrir no significa rastrear ni indexar.|
|No indexadas por motivo|1\.958: 1.847 descubiertas, 66 redirecciones, 32 rastreadas, 10 canónicas alternativas, 2 404, 1 robots|No es necesariamente el mismo universo de 2.095 URLs del sitemap; no calcular una tasa simple.|
|Rendimiento 3 meses|90 clics, ~1.110 impresiones, CTR 8,1 %, posición media 29,9|Visibilidad temprana; posición es agregada y puede empeorar cuando aparecen consultas nuevas con posiciones bajas.|
|Últimos 28 días (otra tarjeta)|24 clics, 882 impresiones; +41 % clics y +635 % impresiones frente al periodo anterior|Señal de crecimiento, pero no mezclar rangos ni tarjetas para calcular proporciones.|
|IA generativa|66 impresiones; home 30; Webotanix Triple Magnesio 12; Collmar 4|Impresiones dentro de funciones IA; no son clics. Fichas de producto empiezan a aparecer.|
|Página principal|84 clics y 436 impresiones en tabla de páginas; /about 4 clics/117; /legal 3/62|Home concentra la mayoría de clics visibles. Las filas mostradas suman 93 frente a 90 en tarjeta; no derivar shares.|
|Consulta|“comparador de suplementos”: 6 clics / 11 impresiones en la captura|Muestra diminuta, pero intención muy valiosa. Posición que vio el usuario manualmente no equivale a posición diaria fija.|

## **3.2. Caída del ranking: hipótesis principal y comprobación**
He encontrado una coincidencia temporal muy relevante: Google anunció la November 2026 core update el 10 de noviembre de 2026, global y para todos los idiomas, con despliegue de hasta dos semanas. El 17/11 seguía apareciendo como activa en el Search Status Dashboard. Por tanto, puede explicar movimientos recientes, pero no demuestra que sea la causa específica de que Tus Suplementos saliera del top 10 para esa consulta.

Google recomienda separar una caída pequeña (por ejemplo, posición 2 a 4) de una caída grande (4 a 29), observar si afecta a todo el sitio o a un grupo de páginas, y comparar periodos equivalentes. También advierte de fluctuaciones de posición y cambios externos en los resultados. Referencia: https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops

|**Causa posible**|**Qué sabemos**|**Cómo probar**|
| :- | :- | :- |
|November 2026 core update|Coincide con el momento actual y sigue en rollout el 17/11.|Esperar a que termine el despliegue; comparar 7/28 días pre/post por query y page. Evitar cambios radicales durante el rollout.|
|La posición recordada era una observación local|Búsqueda manual puede variar por ubicación, dispositivo, sesión, idioma y módulos SERP.|Usar Search Console: query exacta, país España, dispositivo móvil/escritorio, página destino, fechas; cruzar con una comprobación neutral y repetible.|
|La home no satisface suficientemente la intención exacta|H1 actual es genérico “Compara precios y ahorra en tu suplementación”; title habla de comparador pero el texto visible no desarrolla “comparador de suplementos”.|Revisar resultados competidores, title/H1/copy y contenido real. Mejorar propuesta sin keyword stuffing ni cambios antes del diagnóstico.|
|Relevancia/competencia cambió|Los competidores y la SERP pudieron mejorar; los resultados son dinámicos.|En GSC exportar páginas y consultas que pierden clics/impresiones; comparar qué dominios ocupan top 10 y qué formatos muestran.|
|Problema técnico o de seguridad|Sitemaps correctos y las páginas principales funcionan según las capturas; no hay evidencia de acción manual.|Comprobar Manual Actions, Security Issues, indexación de home, canonical, robots, rastreo, uptime y logs Googlebot.|
|Cambio de intención/demanda|No hay serie temporal query exacta más allá de 11 impresiones mostradas.|Comparar impresiones globales de query y Google Trends España; distinguir pérdida de posición de caída de demanda.|

Decisión: no reescribir hoy la home ni cambiar title de forma reactiva. Primero exportar en GSC los datos exactos de “comparador de suplementos” por fecha, consulta, página, país y dispositivo; comparar una ventana de 28 días con la anterior, y aislar el 10/11 como inicio de la update.
## **3.3. Problemas SEO técnicos que sí están sustentados**
- ProductCard se construye como un div clickable que abre un modal. El enlace a /producto/{slug} aparece dentro del modal; Google y usuarios no disponen de un enlace HTML directo visible desde el listado antes de la interacción. Prioridad alta: añadir un enlace <a>/Link rastreable en título o acción de la tarjeta.
- Los enlaces de afiliación están inconsistentes: CTA principal usa rel="noopener noreferrer"; CTA alternativo dentro del modal usa también rel sin sponsored; otros enlaces sí llevan nofollow. Normalizar enlaces comerciales a rel="sponsored nofollow noopener noreferrer" y mantener enlaces editoriales normales.
- La ruta de categorías traduce slugs conocidos y para desconocidos crea un nombre genérico. Backend filtra con igualdad exacta por nombre de categoría. Resultados cero no llevan a notFound y la página sigue con HTTP 200. Esto reproduce las dos pruebas fallidas: alimentacion-saludable y salud-y-bienestar mostraban 0 productos. No indexar esas rutas.
- La ruta de marca también convierte cualquier slug desconocido a nombre de marca y puede renderizar catálogo vacío. Necesita resolver slugs desde fuente de verdad y validación con productos elegibles.
- El H1 de Catalog es genérico y compartido entre home/categorías/marcas. Las landings necesitan H1, intro, title, enlaces y contenido útil específicos, con datos reales.
- Sitemap mantiene arrays estáticos de 5 categorías y 7 marcas. Deben derivarse o validarse desde categorías/marcas elegibles del catálogo, no añadir slugs “por intuición”.
- Product JSON-LD define InStock sin confirmar disponibilidad real y priceValidUntil = hoy + 7 días, no expiración de la tienda. Corregir valores para reflejar solo datos conocidos; revisar si Product snippets es el enfoque adecuado para comparador/afiliación. Google distingue Product snippets y Merchant listings.
- ProductCard CTA principal apunta directamente a product.affiliate\_url y no usa /api/out; no envía rel sponsored y quizá no registra clic interno. Unificar tracking y destino sin romper afiliación ni perder medición.
## **3.4. Redirecciones, 404 y parámetros**
Los 63 endpoints /api/out del CSV (aprox.; inferencia de patrones; no HTTP codes) y las variantes de dominio son esperables como motivos de no indexación. El backend devuelve RedirectResponse 302 de forma deliberada porque el destino afiliado es dinámico. No convertir /api/out a 301. Verificar que cada endpoint hace un único 302 al comerciante correcto y que nunca está en sitemap. Las variantes http/apex deben terminar en una sola redirección permanente a https://www.tussuplementos.com.

Los dos 404 visibles eran /& y raíz del API. API root puede permanecer 404 si no tiene landing pública. /& se debe rastrear hasta su enlace generador. Las 10 canónicas alternativas probablemente incluyen page/filtros; confirmar canonical y que no estén en sitemap. La URL bloqueada por robots.txt no aparece identificada en el corte.
# **4. Estado técnico real en main: hallazgos cotejados**
Los siguientes puntos se comprobaron en el código del main consultado. “Pendiente confirmado” significa que la estructura descrita sigue apareciendo; no significa que el fallo ya haya saturado producción.

|**Área/archivo**|**Hallazgo confirmado**|**Prioridad y decisión**|
| :- | :- | :- |
|backend/main.py · /api/productos|La consulta intermedia obtiene todas las filas candidatas con .all(), luego deduplica/filtra arrays en Python y solo después pagina los IDs. Esto sigue materializando un conjunto grande en RAM.|P0 escalabilidad. Replantear con filtros/paginación SQL y conteos correctos. Los filtros de arrays requieren diseño SQL específico; no basta con sustituir .all() a ciegas.|
|backend/ingestores/pharma2go.py|Carga todos los productos y ofertas en productos\_bd mediante .all() para hacer upsert.|P0 escalabilidad. Evaluar procesamiento por lotes/consulta por SKU/slug e índices; preservar reglas multi-store.|
|backend/ingestores/sportlive.py|Mismo patrón de carga completa de productos+ofertas.|P0 escalabilidad. Igual política de lotes e idempotencia.|
|backend/scripts/orquestador.py|generar\_alertas carga ofertas rebajadas; por cada oferta accede oferta.producto y lanza query para usuarios favoritos. Riesgo N+1. timestamp\_inicio existe y se pasa como corte, pero no elimina N+1.|P0 operación. Consolidar con JOIN / selectinload; agregar pruebas de cantidad de consultas y alertas no duplicadas.|
|backend/models.py|Favorito.usuario\_id/producto\_id, HistorialVistas y ResenaSabor FK consultadas sin index=True en los fragmentos observados; falta índice compuesto Oferta(producto\_id, activo).|P1. Antes de migrar, comparar índices existentes/migraciones y evitar duplicados; EXPLAIN ANALYZE en staging.|
|backend/ingestores/utils.py|clasificar\_producto construye arrays de palabras basura dentro de llamada y ejecuta búsquedas repetidas.|P1 CPU. Precompilar regex o usar matchers con benchmark y suite de falsos positivos; no cambiar semántica de clasificación sin corpus de regresión.|
|backend/send\_telegram\_deals.py + reset\_cooldown.py|mark\_as\_published actualiza publicado\_telegram=TRUE pero no fecha\_publicacion\_telegram; reset\_cooldown solo rearma publicaciones con fecha antigua.|P1 bug operativo confirmado. Guardar NOW() atómico y probar el ciclo publicar→cooldown→reset.|
|.github/workflows|cron\_precios usa Python 3.11, newsletter/retargeting/telegram usan 3.10; cron sin timeout-minutes explícito.|P1. Unificar runtime tras test; timeout <= límite real de GitHub Actions; dividir ingesta HSN si sobrepasa 6h.|
|frontend/src/components/ProductCard.tsx|La ficha de producto solo se enlaza desde el modal; imagen usa priority en cada tarjeta de producto; CTA afiliado usa rel incompleto.|P0 SEO/CWV/monetización. Enlace HTML directo, prioridad LCP solo elementos above-the-fold verificados, rel sponsored.|
|frontend/src/app/categoria y /marca|Metadata por slug genérico; no validar entidad/contador; fetch falla a catálogo vacío sin notFound.|P0 SEO. Resolver contra catálogo real; 404/noindex según caso; nunca landing vacía indexable.|
|frontend/src/app/page.tsx|No lee searchParams para page; la home renderiza carga principal con page=1.|P1. Determinar si hay paginación indexable o filtros solo UX; aplicar canonical/noindex a parámetros y SSR correcto solo si tiene valor.|
|frontend/src/app/producto/[slug]/page.tsx|JSON-LD Product/Offer con disponibilidad forzada y expiración artificial; escaping script JSON-LD necesita hardening.|P1. Solo valores verificados, escapar cierre de script, validar Rich Results Test.|
|frontend/src/app/layout.tsx|metadata global canonical home; las rutas revisadas la sobreescriben, pero otras rutas públicas deben auditarse.|P1. Crawl de todas las rutas, canonical propia o ninguna donde no proceda.|
|backend/main.py · live-search/config/filtros|live-search sin rate limit en el extracto; config/filtros recorre sabores de todos los productos sin caché observada.|P1 escalabilidad/abuso. Debounce cliente + rate-limit server + cache invalidation/cálculo SQL eficiente.|

## **Puntos que parecen ya solucionados o parcialmente solucionados**
- Los ingestores Farma2Go y Sportlive ya descartan precios <= 0 (confirmado en main). No duplicar esta tarea.
- El orquestador ya captura timestamp de inicio y la función generar\_alertas acepta desde\_fecha. Aún queda corregir consulta N+1.
- El endpoint descubrir-stacks filtra Stack.es\_publico == True en el fragmento revisado; la nota de privacidad de stacks podría estar parcialmente resuelta. Comprobar endpoint concreto, no asumir todos.
- PR #134/135/136 ya incorporaron índices/preparación de ingestores y ajuste horario. Revisar migraciones y diff si se reabre cualquier tema.
# **5. Rendimiento, experiencia y confianza del usuario**
Diagnóstico aportado por el equipo: móvil PageSpeed 63, LCP 6,2 s, FCP 2,7 s, TBT 390 ms; avisos de ahorro potencial 213 KiB en imágenes, 150 ms en recursos bloqueantes y 267 KiB de JavaScript sin usar. Son datos de un test puntual y no sustituyen Core Web Vitals de campo (CrUX/Search Console).

|**Métrica/tema**|**Diagnóstico**|**Acción recomendada**|
| :- | :- | :- |
|LCP|6,2 s móvil; sospecha de imagen principal/primer producto, aún sin elemento LCP identificado.|Repetir PSI en URL exacta y móvil; guardar LCP element. Optimizar ese asset, dimensiones, AVIF/WebP, fetchpriority sólo al LCP real.|
|FCP|2,7 s.|Analizar TTFB, CSS crítico, fonts; Next/font ya está en layout.tsx (Geist), por tanto no asumir fuente externa como causa sin waterfall.|
|TBT|390 ms; 6 tareas largas y ~267 KiB JS no usado.|Bundle analyzer; split/dynamic import de modales, gráficos, auth/contextos secundarios; medir reducción y errores.|
|Imágenes|213 KiB potencial; ProductCard asigna priority a imagen de cada tarjeta y precarga al hover.|Eliminar priority indiscriminado; reservar preload/fetchPriority alta a LCP y quizá primeras tarjetas visibles según prueba. Lazy load bajo el fold.|
|Interacción|Catalog, Navbar, ProductCard son client-side y hay muchos estados/hooks.|Reducir JS en cliente progresivamente, no reescribir app entera. Medir INP/CLS/TTFB.|
|Consentimiento|Message (18) propone bloquear GA4/TradeTracker hasta consentimiento.|Implementar consentimiento válido y auditar cookies/etiquetas. Necesita revisión legal/RGPD antes del deploy.|

# **6. Estrategia de producto: de catálogo a comparador diferencial**
## **6.1. Propuesta competitiva**
No intentar competir con HSN o MyProtein como fabricante/tienda. La ventaja del comparador es neutralidad y agregación: mismo producto, distintos vendedores, coste comparable, historial, disponibilidad y transparencia de cambios. La home, fichas y categorías deben dejar claro cómo se calculan los precios, de dónde vienen las ofertas y cómo se monetizan enlaces afiliados.

- Ratio de oro: precio €/kg, €/100 g, €/unidad o €/dosis solo cuando la unidad, el contenido neto y la dosis sean comparables y estén disponibles.
- Historial de precio: mínimos/habitualidad calculados a partir de muestras temporales suficientes; no etiquetar “precio inflado” sin metodología defendible.
- Confianza: hora de actualización por oferta, comerciante, enlace de compra, aviso de afiliación, criterios de inclusión/exclusión y política de corrección de datos.
- Producto maestro: comparar mismo producto/presentación/SKU; no fusionar sabores, gramajes o variantes distintas por similitud de nombre.
- Comunidad/UGC: reseñas de sabores y stacks solo cuando sean reales, moderados, visibles y aporten experiencia; no crear reseñas sintéticas ni indexar perfiles vacíos.
## **6.2. SEO programático con control**

|**Tipo de landing**|**Regla para publicar**|**Contenido único necesario**|
| :- | :- | :- |
|Categoría base|Entidad existente, ≥5 productos activos elegibles (umbral inicial propuesto, revisar por demanda y calidad).|Qué compara, tipos/formatos, rango €/kg real, marcas/tiendas, FAQ útil, enlaces a productos y subcategorías.|
|Categoría + atributo (isolate, creatina Creapure)|≥5 productos coincidentes, filtro exacto y estable, demanda de búsqueda comprobada.|Explicar atributo, criterios de comparación, tabla actualizada y metodología.|
|Ficha producto|Producto maestro identificado; slug estable; oferta activa; datos diferenciados; priorizar multi-comerciante o señales de demanda.|Nombre/presentación exactos, comerciantes, mejor precio, ratio unitario, historial, detalles verificados, enlaces de categoría/marca.|
|Marca|Marca real, productos activos, catálogo suficiente y demanda propia.|Qué productos existen en el comparador, lista/rango/precios reales, marcas relacionadas si proceden.|
|Rankings €/kg|Sólo categorías homogéneas; unidad normalizada; stock/oferta vigente; explicar metodología y fecha.|Ranking con filtros, unidad, fecha de actualización y notas sobre comparabilidad.|
|Sellos de materia prima|Sello verificado en atributo/fuente del producto, no por palabra vaga.|Qué significa el sello, productos confirmados, enlaces y advertencia de que no sustituye calidad total.|
|Filtros y parámetros|Por defecto navegación UX no indexable; permitir páginas SEO sólo si tienen demanda y valor estables.|Canonical/index/noindex consistente; evitar combinaciones infinitas.|

No abrir 50.000 páginas de golpe. La estrategia adjunta sugiere indexación por oleadas; el informe SEO actual añade una puerta más estricta: toda landing del sitemap debe devolver 200, canonical correcta, productos reales y contenido útil. El umbral de 2 ofertas multi-tienda puede ser una señal de calidad, no una regla única inamovible; validar por categoría, demanda y exactitud del match.
## **6.3. Oportunidades de crecimiento de negocio**
- Alertas de precio: CTAs claros (“Avísame si baja de X €”), frecuencia de notificación limitada, umbral configurable y deduplicación.
- Telegram y newsletter: mantener canales propios, pero medir clics salientes, suscripciones, bajas, CTR y ventas atribuidas; la automatización no debe publicar ofertas caducadas.
- Rankings de datos propios: “proteínas por €/kg”, “creatinas certificadas” y evolución mensual, cuando el dato sea preciso y transparente.
- Comparativas VS: crear pocas páginas basadas en productos realmente comparables y con búsquedas; no generar todas las combinaciones de pares.
- Contenido y backlinks: publicar metodología y análisis basado en datos propios; colaborar con comunidades de manera honesta. Evitar compra/esquemas de enlaces y contenido a escala repetitivo.
- Google CSS: la captura del 12/11 sugiere 214 productos detectados. El CSS exige, entre otros, empresa registrada en país admitido, al menos 50 dominios de comerciantes distintos por país y páginas comparativas con al menos dos comerciantes. No asumir elegibilidad; primero contar dominios únicos activos y condiciones.
# **7. Roadmap conjunto Javier + Diego**
Horizonte orientativo de 8–12 semanas para cerrar los principales bloques de producto y dejar un motor de crecimiento sostenible. Duraciones estimadas por equipo pequeño de dos personas, sujeto a resultados de pruebas y estado real del backlog. No es una promesa de ranking/visitas.
## **Gate 0 — Congelar referencia y visibilidad (0,5–1 día)**

|**Owner sugerido**|**Trabajo**|**Criterio de salida**|
| :- | :- | :- |
|Ambos|Tag/commit de referencia main, backup DB probado, staging/Preview y checklist de rollback.|Se puede volver al estado estable; ningún trabajo SEO se hace directamente en main.|
|Javier|Exportar GSC exacto: query comparador de suplementos, España, página, dispositivo, fecha; rendimiento 28 días vs anteriores y periodo previo a 10/11.|Baseline reproducible de query/page/country/device y fecha de update.|
|Diego|PageSpeed móvil/desktop en home, categoría, marca y producto; guardar reportes PSI, LCP element, CrUX si disponible.|Baseline con datos de laboratorio y campo diferenciados.|
|Ambos|Backlog de issues con P0/P1/P2, dueño, PR, prueba y decisión.|No se duplican tareas ya fusionadas en #131–#137.|

## **Gate 1 — Estabilidad de backend y operación (1–2 semanas)**

|**Owner sugerido**|**Tarea prioritaria**|**Acceptance criteria**|
| :- | :- | :- |
|Javier|Replantear /api/productos para paginar/filtrar en DB sin cargar todos los IDs/productos a RAM.|Mismos resultados y orden con filtros actuales; EXPLAIN; prueba con dataset sintético grande; memoria/latencia comparadas.|
|Javier|Farma2Go/Sportlive: retirar carga completa productos\_bd, procesar lotes y upsert seguro; no asumir slug idéntico si no es mismo producto.|Carga repetida idempotente; no duplicados; sin pérdidas de productos/ofertas; commits por lote y rollback; pruebas de fallos/reintento.|
|Javier|Desactivar ofertas obsoletas sólo si el ingestor completó con éxito y el snapshot está completo; set de productos vistos por tienda.|Una ingesta parcial/fallida nunca desactiva masivamente ofertas. Dry-run y métricas de bajas.|
|Javier|Corregir N+1 de generar\_alertas con JOIN/selectinload y claves/indexes.|Número de queries acotado respecto al número de ofertas; alertas correctas, deduplicadas y sin usuarios ajenos.|
|Javier|Corregir mark\_as\_published para establecer fecha\_publicacion\_telegram; robustecer conexión con finally/context manager.|Test publicar→reset cooldown 7d; fecha no nula; no romper ejecución si Telegram falla.|
|Javier|Revisar TTL cache, regex clasificadora, errores y métricas del orquestador.|Suite con corpus de títulos borderline (whey chocolate, gelatina/gel, suplementos veterinarios); avisos si ingestor devuelve anomalías.|
|Javier|Índices: inventario de migrations y EXPLAIN antes de crear.|Migración idempotente y no duplicada; índices en FK calientes y compuesto producto\_id/activo sólo si se confirma plan.|
|Javier|Operación GitHub Actions: Python version, timeout, dividir HSN si ciclo pasa límite de runner.|Duración de cada proveedor dentro de límite, reintentos idempotentes, no solapamiento y notificación de fallo.|

## **Gate 2 — Seguridad y confianza (3–5 días, en paralelo sólo con tests)**

|**Tarea**|**Prueba de salida**|
| :- | :- |
|Auth manual/Google; impedir conflictos de hash login\_google; verificación email si aplica.|Tests de alta/login/recuperación, email no verificado, usuarios preexistentes y OAuth.|
|Rate-limit: revisar proxy IP real, live-search rate limit y debounce cliente.|Varios usuarios detrás de Render no comparten bucket; throttling medible.|
|Rutas internas/swagger y secretos TradeDoubler.|No existe bypass de rate limit; secretos fuera del repo y rotados si se expusieron.|
|Check-in único por perfil/fecha con constraint y operación transaccional.|Peticiones concurrentes conceden XP una sola vez; migración reversible.|
|Foto perfil tamaño máximo y carga diferida; JSON-LD escapado.|Payload por encima del límite rechazado; input malicioso no puede cerrar script ni inyectar HTML.|
|Privacidad/consentimiento GA4/TradeTracker y baja newsletter.|Etiquetas no esenciales bloqueadas antes de consentimiento; consent/revoke/baja auditables.|

## **Gate 3 — Discoverability, SEO on-page y Core Web Vitals (1–2 semanas)**

|**Owner sugerido**|**Tarea**|**Acceptance criteria**|
| :- | :- | :- |
|Diego|Enlace HTML directo a /producto/{slug} desde ProductCard; conservar modal UX.|HTML/render tiene anchor rastreable y navegable; keyboard/accessibility; modal no se rompe.|
|Diego|Auditoría de todos los links afiliados: sponsored nofollow y CTA con tracking /api/out consistente.|Todos los links comerciales correctos; medir clic por oferta; ningún enlace interno marcado sponsored.|
|Diego|Reducir priority en imágenes de todas las tarjetas; sólo LCP real/preloads above fold.|PSI y waterfall muestran LCP mejor y sin exceso de preloads.|
|Diego|Split de bundle: modales, PriceHistoryChart, auth pesada y componentes no críticos.|JS inicial menor; sin errores hidratación; TBT/INP mejoran en dispositivos de prueba.|
|Diego|Corregir errores de paginación y query params: canonical/noindex/SSR según tipo; no enlazar ?page=1 ni /&.|URLs canónicas limpias; Google recibe enlaces estándar; no duplicados innecesarios.|
|Ambos|Crawl de todas las rutas públicas: status, canonical, title, H1, index/noindex, enlace interno.|Inventario sin landings vacías 200, canonical home heredada o páginas huérfanas prioritarias.|

## **Gate 4 — Landings categoría/marca y estrategia de catálogo (1–2 semanas)**

|**Tarea**|**Acceptance criteria**|
| :- | :- |
|Crear fuente de verdad de slug/entidad desde API/BD con conteo de productos elegibles.|Cada slug corresponde a una entidad y devuelve resultados correctos con acentos/capitalización resueltos.|
|Invalidar rutas inexistentes o permanentemente vacías; definir una política para catálogo temporalmente vacío.|No hay URL inexistente indexable con 200; no se usa notFound ante fallo temporal de backend sin distinguirlo.|
|H1/title/intro únicos para cinco categorías prioritarias y hasta cinco marcas principales por datos reales.|Texto basado en productos y filtros reales, no copy repetido; CTA y enlaces útiles.|
|Añadir navegación a landings desde header/footer/landing contextualmente.|Categorías y marcas accesibles en HTML en pocos clics; no depender solo de filtros client-side.|
|Sitemap dinámico validado.|100% de URLs listadas responden 200, canonical propia, entidad/productos elegibles y datos de actualización fiables.|

## **Gate 5 — 10–20 fichas prioritarias y datos estructurados (1–2 semanas)**
- Priorizar por Search Console: Webotanix Triple Magnesio, Collmar Eternity, Kobho Whey, Ynsadiet Liposovit/Omega-3, LCN Omega Base, Zenement Omega-3, Kiroot D3 K2, Curcumin Complex Puro Omega y otras con impresiones/AI impressions.
- Verificar identidad del producto, presentación y ofertas por comercio. Añadir información diferencial sólo con datos existentes: precio mínimo, oferta, €/kg/dosis, historial y última actualización.
- JSON-LD Product/AggregateOffer correcto y coherente con el contenido visible. No inventar availability ni priceValidUntil. Evaluar Product snippets (comparador) frente a Merchant listings (venta propia). Validar con Rich Results Test y URL Inspection.
- Optimizar imágenes, alt y descripción; evitar párrafos plantilla repetidos generados únicamente para aumentar longitud.
## **Gate 6 — pSEO, BOFU y retención (continuo, después de gates anteriores)**

|**Línea de crecimiento**|**Primer experimento limitado**|**KPI de éxito**|
| :- | :- | :- |
|Rankings €/kg|Proteínas whey comparables; luego creatina monohidrato. Dataset limitado y metodología visible.|CTR a fichas/ofertas, engagement útil, ingresos/1000 sesiones; exactitud de €/kg auditada.|
|Sellos|Landing Creapure sólo si hay datos confirmados y suficiente catálogo.|Impresiones/clics long-tail y conversión a oferta; porcentaje de sello verificado.|
|Comparativas VS|5 comparativas de productos con demanda real y atributos compatibles.|Clic orgánico, clic a comerciante, tiempo hasta salida y feedback.|
|UGC|Solicitar reseña sabor tras uso real; moderación/anti-spam.|Reseñas verificadas, tasa de abuso, usuarios activos y valor de búsqueda; sin schema review si no cumple políticas.|
|Alertas/Telegram/newsletter|A/B de CTA “avísame si baja” y top semanal con datos reales.|Suscripciones, bajas, clics, conversiones afiliadas y tasa de alertas útiles.|
|Backlinks/brand|Publicar metodología de comparación e informes de datos; colaboraciones transparentes.|Dominios de referencia relevantes, menciones de marca y tráfico referido.|
|CSS Shopping|Contar dominios comerciales únicos y productos con ≥2 comerciantes; comprobar empresa/addresses.|Elegibilidad por checklist oficial, no por el aviso “214 productos detectados”.|

# **8. Priorización práctica para el equipo**

|**Orden**|**Trabajo**|**Owner recomendado**|**Dependencias**|**No avanzar hasta…**|
| :- | :- | :- | :- | :- |
|P0-1|/api/productos SQL pagination + tests de regresión|Javier|Nada; base local/staging|Comparar mismos filtros, total, orden y paginación.|
|P0-2|Ingestores por lotes + idempotencia + snapshot completo|Javier|Esquema DB y logs de ingesta|Reprocesar proveedor dos veces y validar cero duplicados/falsos desactivados.|
|P0-3|Enlace directo ProductCard + rel sponsored y tracking|Diego|Diseño interacción modal|HTML y navegación real + tracking funcionando.|
|P0-4|LCP/JS: medir y optimizar imagen/priority/componentes|Diego|PSI repetible|LCP element y bundle confirmados; PSI y campo comparados.|
|P1-1|N+1 alertas + Telegram timestamp/cooldown + observabilidad|Javier|Tests de backend|Alertas de prueba y ciclo Telegram/reset correctos.|
|P1-2|Categorías/marcas validadas y H1/metadata diferenciadas|Diego + Javier API|Fuente de verdad endpoint/BD|No hay landing vacía 200 ni slug improvisado.|
|P1-3|Seguridad/rate-limit/consentimiento|Javier + Diego|Decisiones funcionales/legales|Tests auth, proxy y consentimiento completos.|
|P1-4|20 fichas y Product schema verificado|Ambos|Datos maestros y ofertas fiables|Render + Rich Results Test + URL Inspection.|
|P2|Rankings/sellos/VS/UGC/CSS/backlinks|Ambos|Gates 0–5 cerrados|Métrica/valor probado y dueño de mantenimiento.|

# **9. Cuadro de mando**

|**Dimensión**|**Métrica**|**Frecuencia**|**Objetivo inicial / criterio**|
| :- | :- | :- | :- |
|SEO|Clics e impresiones no-brand, España, por página y query|Semanal|Crecimiento sostenido; medir por URL y consulta, no solo posición media.|
|Keyword clave|“comparador de suplementos” por España, móvil/desktop, fecha|Semanal durante update; mensual después|Recuperación/estabilidad del top 10; comparar después del rollout.|
|Indexación|Indexadas vs descubiertas/rastreadas; grupos homogéneos|Semanal|Más fichas valiosas indexadas; no perseguir volumen bruto.|
|Sitemaps|URLs elegibles vs URLs incluidas; status y canonical|Cada deploy + semanal|100% URL válida y sin vacías/redirect/noindex.|
|CWV|LCP, INP, CLS field + PSI lab|Quincenal y antes/después de releases|Objetivos Google de Core Web Vitals en campo; priorizar móvil.|
|Backend|p95/p99 /api/productos, queries, memoria, error-rate|Por release + mensual|Sin crecimiento lineal de RAM con catálogo; latencia p95 definida tras baseline.|
|Ingesta|Duración por tienda, productos procesados, actualizados, descartados, fallos, ofertas desactivadas|Cada ejecución|Idempotencia y reconciliación; cero falsos positivos de desactivación.|
|Afiliación|CTR catálogo→out, out→merchant, conversiones/comisiones por proveedor|Semanal|Baseline por categoría/comerciante; optimizar con datos reales.|
|Retención|Alertas, newsletter/Telegram, activación, bajas|Semanal|Más usuarios que vuelven; no aumentar envíos irrelevantes.|
|Seguridad|Rate limit, auth errors, abuse, payload rejections|Mensual y por release|Sin bypasses ni leaks; privacidad/consentimiento cumplidos.|

No fijar metas arbitrarias como 8.000 páginas indexadas o 25.000 sesiones mensuales como compromiso. Definir objetivos tras 4 semanas de baseline y medir conversiones y valor, no solo páginas/clics.
# **10. Método de trabajo Javier + Diego**
1. Un único ticket = una intención y un criterio de aceptación. Evitar PRs que mezclen refactor, SEO, seguridad y diseño.
1. Crear rama desde main actualizada; no trabajar directamente en main ni editar producción.
1. Antes de modificar backend, preparar test reproducible con DB local/staging anonimizada. Nunca ejecutar migraciones/desactivaciones en producción desde pruebas.
1. Para cambios de esquema: revisar migrations existentes, índices duplicados, estrategia de rollback y estimación de lock/tiempo.
1. El agente de código recibe prompts quirúrgicos: alcance permitido, archivos permitidos, comportamiento que no debe cambiar, pruebas requeridas y prohibición de deploy/merge.
1. Ejecutar lint, typecheck, tests unitarios/integración, build frontend/backend y análisis estático; comparar con baseline.
1. Abrir PR con resumen, archivos, riesgos, pruebas, capturas/benchmarks. Preview de Vercel y staging backend con fixture representativo.
1. Revisar diff en pareja: uno implementa y otro audita, luego intercambiar roles. Merge solo si todos los checks están verdes y rollback claro.
1. Después del deploy, smoke test de home, búsqueda, categoría, marca, ficha, oferta afiliada, login, alertas y sitemaps; verificar logs y métricas.
## **Distribución sugerida**

|**Javier — backend/datos/operación**|**Diego — frontend/UX/SEO técnico**|**Ambos**|
| :- | :- | :- |
|SQL pagination, ingestores, alertas, migrations, índices, workflows, auth, rate limit, cache, observabilidad.|ProductCard anchors, rel afiliación, CWV, bundle, metadata, canonical, landings, navegación, UX.|Prioridades, QA end-to-end, Search Console, contenido diferencial, CRO, producto y definición de métricas.|

# **11. Riesgos y guardarraíles**

|**Riesgo**|**Impacto**|**Mitigación**|
| :- | :- | :- |
|Ingesta incompleta marca ofertas correctas como inactivas|Pérdida de precios y comparativas fiables.|Solo reconciliar/desactivar cuando snapshot de tienda completo y exitoso; dry-run y umbrales de caída.|
|Reescritura /api/productos cambia resultados|Filtros/orden/paginación regresan.|Contrato API y tests de paridad con corpus; benchmark y rollback.|
|Crear miles de landings delgadas|Dilución de calidad/indexación; contenido repetitivo.|Publicación por oleadas y umbrales; noindex o 404 según estado real.|
|Cambios agresivos durante Core Update|No se puede atribuir efecto, se introducen regresiones innecesarias.|Esperar fin rollout y comparar datos; resolver antes solo defectos técnicos demostrados.|
|Cambios en JSON-LD con datos no reales|Rich results no elegibles o pérdida de confianza.|Schema solo con datos visibles/verdaderos; Rich Results Test y auditoría.|
|Aumentar priority en muchas imágenes|Sobrecarga de red y LCP peor.|Preload únicamente LCP real; lazy load resto.|
|Cambios en crawler/robots sin entender parámetros|Bloquear URLs útiles o aumentar espacio de facetas.|Inventario de parámetros y canonical antes de robots/noindex.|
|CSS o feeds sin elegibilidad|Rechazo, suspensión o trabajo desperdiciado.|Verificar 50 dominios únicos y resto de requisitos CSS antes de empezar.|

# **12. Referencias y documentación**
- Informe SEO Tus Suplementos, corte 12/11/2026, 20 páginas; secciones 3–8, 11–14 y anexos A/B.
- ESTRATEGIA SEO (1).txt: pSEO, BOFU €/kg, sellos, retención, newsletter/Telegram, roadmap seis meses. Sus objetivos de tráfico se tratan como aspiracionales.
- Auditoría técnica.txt: N+1, índices, regex, Telegram cooldown, memoria, workflows, propiedades ORM y URL larga.
- message (18).txt: backlog ingesta, seguridad, SEO/Frontend/Telegram, HSN runtime, filtros y clasificador.
- Diagnóstico Core Web Vitals (1).txt: PSI puntual, LCP 6,2 s, FCP 2,7 s, TBT 390 ms y ahorros estimados.
- Google Search Central — Debugging drops in Search traffic: https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops
- Google Search Status Dashboard — November 2026 Core Update (iniciada 10/11/2026; rollout estimado hasta 2 semanas): https://status.search.google.com/
- Google Search Central — Product snippets: https://developers.google.com/search/docs/appearance/structured-data/product-snippet
- Google Search Central — Merchant listings: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing
- Google CSS Center — requisitos: https://support.google.com/css-center/answer/7524491?hl=es-ES
- Google Search Central — ecommerce navigation: https://developers.google.com/search/docs/specialty/ecommerce/help-google-understand-your-ecommerce-site-structure
# **13. La primera semana: qué hacemos ahora**
No empezar con una gran reescritura SEO. La secuencia recomendada para los próximos días es:

1. Javier: abrir rama y resolver /api/productos para que no haga full materialization pre-paginación; añadir pruebas de paridad/benchmark.
1. Javier: preparar fix N+1 alertas y timestamp de Telegram/cooldown con tests; identificar índices existentes para no duplicar migraciones.
1. Diego: PR separado para enlace directo en ProductCard, rel sponsored y reducir priority al LCP real; evitar cambios visuales no relacionados.
1. Ambos: exportar query exacta “comparador de suplementos” desde GSC con España, móviles/desktop y páginas; esperar cierre de Core Update para evaluación estable.
1. Diego: repetir PSI móvil de home y páginas prioritarias; identificar LCP real y bundle pesado antes de optimizar.
1. Ambos: crear inventario de categorías/marcas con nombres reales y conteos; no añadir todavía categorías que devuelven cero.

Resultado esperado de esta semana: PRs pequeños, pruebas demostrables y una fotografía fiable de la caída de ranking. No perseguir una meta arbitraria de indexación; preparar el comparador para que cada producto y oferta publicada sea útil, rápido y fiable.
DOCUMENTO INTERNO  •  17 NOVIEMBRE 2026  •  PLAN VIVO
