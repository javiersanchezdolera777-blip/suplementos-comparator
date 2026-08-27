# 19. AUDITORÍA FINAL Y RECOMENDACIONES

Tras un análisis profundo de todas las capas del proyecto (Backend, Frontend, BBDD, ETL, SEO), se presenta el veredicto final. TusSuplementos es un producto técnicamente muy maduro para su fase inicial (MVP / V1), con un backend asombrosamente resiliente, pero con claras lagunas en SEO y usabilidad si se pretende escalar masivamente de golpe.

## Las 10 cosas mejor hechas del proyecto (Fortalezas)
1.  **Cerebro NLP Centralizado (`utils.py`):** Mantener toda la lógica de alérgenos y formatos en un solo punto, separada del raspado web, es un acierto de arquitectura enorme que evita código espagueti.
2.  **Patrón Fail-Fast en Servicios:** Que el backend aborte la ejecución si falta un Token (ej. Resend o BD) previene fallos silenciosos y corrupción de datos.
3.  **Bucle Upsert Masivo Seguro:** Utilizar una sola transacción (`db.commit()`) para actualizar/insertar cientos de productos mejora el rendimiento de la DB y previene *locks*.
4.  **Cálculo Unificado del Precio/Kg:** Estandarizar libras, gramos y envases a gramos absolutos asegura que "El Ratio de Oro" no se pueda falsear.
5.  **Umbrales Dinámicos Antimonopolio:** Aplicar exigencias distintas de descuentos (-30% vs -50%) según la categoría demuestra una profunda inteligencia de negocio.
6.  **Arquitectura Gamificada (BBDD):** El diseño de la capa social (Perfiles, Seguidores M:M, Checks, Stacks) está normalizada de manual.
7.  **Separación Usuario / Perfil:** Aislar el `email` y `password` en una tabla, y el `username` en otra, es una práctica de seguridad avanzada.
8.  **Puntuación de Relevancia (CTR):** Que el catálogo se ordene orgánicamente por los clics reales de los usuarios asegura que el inventario se auto-regule sin trabajo manual.
9.  **Tolerancia a errores de Búsqueda (pg_trgm):** Integrar trigramas en la búsqueda permite a los usuarios escribir mal los suplementos y aun así encontrar resultados, vital para el e-commerce.
10. **Automatización "Hands-free":** Configurar CRONs para extraer, limpiar, insertar y notificar a Telegram autónomamente es la definición de ingresos pasivos escalables.

---

## Las 10 cosas que requieren más atención (Debilidades Críticas)
1.  **Exposición del SECRET_KEY:** Hardcodear la semilla JWT en `security.py` compromete todo el sistema.
2.  **Falta de JSON-LD:** La ausencia total de Schema.org paraliza el SEO transaccional en Google.
3.  **Falta de URLs Estáticas para Filtros:** No tener `/categoria/[slug]` destruye las posibilidades de rankear *mid-tails*.
4.  **Renderizado Total en Cliente (CSR):** Hacer el fetch del catálogo masivo desde el navegador perjudica el LCP (Core Web Vitals).
5.  **Multiplicación de SKUs (Duplicados):** 1 Tienda = 1 Fila nueva. El catálogo se inundará de clones inservibles en la UI.
6.  **Dependencia del Precio Anterior (Feeds):** Confiar en que Tradedoubler reporta el MSRP correcto arruina la fidelidad de los Chollos.
7.  **Bloqueo de Afiliados (Sin Cloaker):** Inyectar URLs de `tradedoubler.com` directas en el frontend garantiza que los AdBlockers destruyan el 40% de las ventas.
8.  **Escalabilidad de la Búsqueda (Similarity):** Hacer un `func.similarity` sin índice GIN tumbará la CPU del server con 10K+ productos.
9.  **Falta de Eventos de Conversión en GA4:** No enviar un ping a Google Analytics al clicar "Ver Oferta" ciega al departamento de Marketing.
10. **Rate Limiting Inexistente:** La API `/api/productos` no tiene límite de peticiones por IP; vulnerable a raspadores (scrapers) enemigos.

---

## Las 10 mejoras que deberían hacerse ANTES del lanzamiento (Go-Live)
Si el producto va a lanzarse públicamente o recibir tráfico de pago/campañas, estos puntos son bloqueantes:
1.  **Mover `SECRET_KEY` al `.env`** en Render y cambiar su valor.
2.  **Inyectar JSON-LD `Product`** en el componente `[slug]/page.tsx`.
3.  **Crear un Endpoint Cloaker** en backend (`/out/{id}`) para enmascarar los enlaces de afiliados contra uBlock/Adblock.
4.  **Habilitar SSR de Catálogo Base** en Next.js para mejorar el TTI y la usabilidad inicial.
5.  **Añadir Disallow en robots.txt** a todos los parámetros de ordenación (`?orden=`, `?solo_ofertas=`) para evitar canibalización indexada.
6.  **Auditar Legalmente el GDPR:** El tracker de GA4 y TradeTracker no pueden dispararse hasta que el usuario acepte cookies (banner de cookies estricto).
7.  **Restringir los CORS** en `main.py` explícitamente a `tussuplementos.com`.
8.  **Generar el Sitemap Dinámico:** Conectar `sitemap.ts` al backend para incluir las fichas de todos los productos en stock.
9.  **Implementar Tagging GA4 Básico:** Crear eventos de "Ver Oferta" en los botones clave.
10. **Añadir Índice GIN/GiST** en PostgreSQL para el campo `nombre` soportando la extensión trigramas.

---

## Las mejoras que pueden esperar (Post-lanzamiento)
*   **V2 Multi-Tienda (Ficha Unificada):** Modificar todo el ORM y la BBDD para agrupar ofertas en un solo producto es titánico. Mejor lanzar, validar el modelo de negocio, y refactorizar en Sprint 4 o 5.
*   **Motor Histórico de Precios:** Requiere recolectar datos durante meses para ser útil. Puede esperar a que haya tráfico recurrente.
*   **Colas Asíncronas (Celery):** Hasta no tener 10 o 20 tiendas raspando simultáneamente, el CRON sincrónico funciona perfectamente.
*   **Paginación por Cursores (Keyset):** El Offset actual aguantará hasta los 10K-20K productos sin demasiados problemas.

---

## Deuda Técnica Detectada
*   **Paso de Diccionarios a Modelos NLP:** En `utils.py`, el motor usa expresiones regulares masivas y strings sueltos. Debería migrarse hacia esquemas tipados robustos u ontologías semánticas formales para mantener la mantenibilidad si el negocio crece a Europa.
*   **Alembic:** El esquema DB ha evolucionado con `create_all()`. Añadir Alembic al proyecto ahora requerirá hacer una instantánea (snapshot) de la DB de producción y generar una migración base (`initial`) para alinear el estado.
*   **Inestabilidad de Scrapers por Hyvä:** El DOM de HSN usa Magento Hyvä Theme (muy dinámico/React). Confiar en CSS selectors (`soup.select()`) es deuda técnica porque se romperá a menudo. Se debe priorizar al 100% el objeto `application/ld+json` de la cabecera sobre el HTML renderizado.

---

## Decisiones arquitectónicas que conviene revisar antes de escalar
*   **Migración de SQLite/Postgres a Multi-Region:** Si el negocio se abre a Latam, tener la base de datos centralizada en Frankfurt (por ejemplo) penalizará los *reads*.
*   **Redis para Modo Versus:** Consultar el catálogo permanentemente contra el disco/Postgres para algo que cambia tan poco (el precio diario) es ineficiente. Añadir una capa de caché Redis (TTL de 6 horas) al endpoint `/api/productos` absorbería el 90% del impacto en la BBDD en momentos de picos virales (ej. influencers en TikTok).
