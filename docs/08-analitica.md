# 11. ANALÍTICA Y MEDICIÓN

## Infraestructura de Analítica Actual

La medición del proyecto actualmente se basa en una combinación de soluciones de terceros (Frontend) y mecánicas propias integradas en el flujo de la aplicación (Backend).

### 1. Google Analytics (GA4)
*   **Implementación:** Está implementado nativamente mediante el componente `@next/third-parties/google` inyectado en el `layout.tsx` principal.
*   **Variable:** Depende de `NEXT_PUBLIC_GA_ID` con un fallback *hardcodeado* (`G-GMZDENG5MM`).
*   **Funcionalidad:** Mide automáticamente eventos de página vista (pageviews), sesiones, tipo de dispositivo y scroll (funcionalidades por defecto de GA4).
*   **Limitación:** No se ha configurado Google Tag Manager (GTM) en el código, por lo que la inyección de eventos personalizados requeriría tocar el código fuente con `sendGAEvent` o migrar a GTM.

### 2. Analítica de Afiliación (TradeTracker)
*   **Implementación:** Existe un script asíncrono heredado de verificación (`<Script id="tradetracker-verification">`) en el `layout.tsx`.
*   **Advertencia:** Este script es una etiqueta de validación de propiedad del sitio que exige la red de TradeTracker, no es un tag de medición de e-commerce per se.

### 3. Motor de Relevancia y CTR Interno (Backend)
El sistema TusSuplementos cuenta con un motor algorítmico primario para calcular la popularidad ("Trending") y realizar Retargeting automatizado.

*   **API CTR:** Endpoint `POST /api/click/{product_id}`.
*   **Uso:** Cuando un usuario interactúa con un producto en la interfaz (presumiblemente al hacer clic para ver la oferta), el frontend dispara una petición en segundo plano a este endpoint.
*   **Efecto:** Incrementa la columna `clics_count` del modelo `Producto`.
*   **Impacto de Negocio:** El endpoint `GET /api/productos` utiliza `models.Producto.clics_count.desc()` como factor principal de ordenación por defecto ("Relevancia"), creando un bucle de retroalimentación donde los productos más clicados ganan mayor exposición.

*   **API Historial / Retargeting:** Endpoint `POST /api/historial/{product_id}`.
*   **Uso:** Almacena la vista explícita de un producto atándola al `Usuario` (si está logueado).
*   **Efecto:** Alimenta la tabla `HistorialVistas`, lo cual es barrido por el motor de email (`retargeting_vistas.py`) para enviar notificaciones de "carrito abandonado" pasados unos días.

## Diagnóstico del Funnel (¿Podemos medirlo todo?)

### El Funnel Teórico:
1.  **Impresión (Búsqueda Orgánica/Social)** ➡️ *Medible vía Google Search Console (No integrado en código, sino en dominio).*
2.  **Visita a TusSuplementos (Página Vista)** ➡️ *Medible vía GA4.*
3.  **Visualización de Producto (Impresión en catálogo o Ficha)** ➡️ *Parcialmente medible (El frontend no lanza un evento `view_item` a GA4, pero el backend lo registra si el usuario entra a la URL `/producto/[slug]`).*
4.  **Clic en enlace afiliado ("Ver Oferta")** ➡️ *Medible en Backend (`clics_count`) y en la plataforma de Afiliación receptora, pero NO se está enviando un evento de conversión personalizado `generate_lead` o `click_affiliate` a GA4 para cruzar la sesión.*
5.  **Conversión en tienda final** ➡️ *Imposible de medir nativamente en la plataforma*. Solo se puede visualizar en el panel de control del proveedor (Awin, HSN, Tradedoubler).

## Carencias Críticas y Recomendaciones
1.  **Falta Google Search Console (GSC):** No hay evidencia de archivos de verificación en la raíz (`google-site-verification`). Esto debe configurarse vía DNS.
2.  **Tracking de Afiliados Ciego en GA4:** Para tomar decisiones de UX/UI, necesitamos saber *qué* fuentes de tráfico convierten. Actualmente, si TikTok trae 10.000 visitas y Google trae 1.000, no podemos saber en GA4 cuál de las dos generó más clics en "Ver Oferta" (solo lo sabremos globalmente por el Backend). **Solución:** Implementar `sendGAEvent({ event: 'click_affiliate', value: product_name })` en los botones de redirección del `Catalog.tsx`.
3.  **Falta soporte UTMs estructurado:** El bot de Telegram debería estar inyectando parámetros `?utm_source=telegram&utm_medium=channel&utm_campaign=top5` en todos los enlaces generados en `newsletter_semanal.py` para que GA4 discrimine el tráfico del bot frente al tráfico directo.
