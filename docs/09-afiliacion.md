# 12. AFILIACIÓN Y MONETIZACIÓN

## Modelo de Implementación Actual
El modelo de negocio de TusSuplementos depende íntegramente de la generación de tráfico cualificado hacia tiendas externas mediante enlaces traqueados (CPA/Revenue Share). No hay pasarela de pagos propia (Stripe/PayPal).

### Redes de Afiliación Activas
1.  **Programa Directo (HSN):** El sistema scraper (`hsn.py`) lee el dominio nativo. Presumiblemente, la inyección del tag de afiliado se hace por reglas de strings en el pipeline final, o están hardcodeados los parámetros en el entorno.
2.  **TradeDoubler:** Origen de los datos para **Farma2Go** y **SportLive**. El script de ingestión captura los Datafeeds que proporcionan directamente el nodo `productUrl` (la URL larga que pasa por el servidor de TradeDoubler y genera la cookie en el navegador del usuario antes de llegar a la tienda).

## Tracking y Enlaces

### Estructura de Enlaces
*   En la base de datos (PostgreSQL), la tabla `productos` reserva la columna `afiliado_url` (String) para almacenar el enlace final de destino que debe clickar el usuario.
*   En el frontend (`Catalog.tsx`, `ProductCard.tsx`), el botón de compra o "Ver Oferta" renderiza este enlace nativamente (`<a href={producto.afiliado_url}>`).

### Medición de Clics
*   **Parcialmente Implementado:** El Frontend intercepta el click en "Ver Oferta" y, en paralelo, dispara una llamada `POST /api/click/{producto.id}`. Esto incrementa la columna interna `clics_count` para alimentar el motor de relevancia ("productos populares"), pero **no** es un clóaker o link-redirector puro.
*   **Ausencia de Cloaking:** A diferencia de comparadores profesionales que usan URLs como `tussuplementos.com/go/producto-slug` y desde el servidor devuelven un *HTTP 302 Redirect* hacia el enlace sucio de afiliado, el frontend de TusSuplementos imprime el enlace de afiliado real (TradeDoubler, Awin) directo en el DOM.

## Riesgos y Problemas Identificados

### 1. Bloqueadores de Publicidad (AdBlockers)
*   Imprimir enlaces directos con dominios conocidos como `clk.tradedoubler.com` o `awin1.com` en el DOM (`<a href="...">`) es extremadamente arriesgado. El 40% de los usuarios modernos usan extensiones como uBlock Origin o Brave Browser que **eliminan o bloquean nativamente estos enlaces**, rompiendo el botón de compra o impidiendo la inyección de la cookie, lo que destroza la conversión.

### 2. Latencia de Redirecciones (Tradedoubler)
*   Como se detalla en el `CURRENT_STATE.md`, el roadmap avisa de que el frontend padece lentitud en las redirecciones de Tradedoubler. Esta mala UX sucede cuando el usuario clica y el navegador salta por múltiples dominios tracker antes de aterrizar en Farma2Go.

## Arquitectura Recomendada (V2)

Para escalar las operaciones a futuro integrando campañas temporales, códigos descuento y nuevas tiendas (Aminha Farmacia, Bulk), el sistema requerirá una refactorización hacia un **Motor de Redirección Interno (Cloaker)**:

1.  **Endpoint Redireccionador:** Crear `GET /out/{slug}` o `GET /go/{id}` en el Backend (FastAPI).
2.  **Flujo:**
    *   El usuario hace clic en un enlace limpio: `https://www.tussuplementos.com/out/whey-protein-hsn`.
    *   El servidor FastAPI recibe la petición.
    *   Suma +1 a las analíticas internas en la DB.
    *   Devuelve una respuesta `HTTP 302 Found` con la `Location` apuntando a la URL real de TradeDoubler/Awin.
3.  **Beneficios:**
    *   **Anti-AdBlock:** uBlock Origin verá un enlace limpio al propio dominio y no lo bloqueará inicialmente.
    *   **Protección de Pagerank:** Evita que Google castigue la web por emitir miles de links salientes a redes de publicidad. Se complementa usando encabezados `rel="nofollow sponsored"`.
    *   **Limpieza de UI:** El usuario no se asusta al ver URLs largas o con símbolos extraños al pasar el ratón sobre el botón de compra.
    *   **Gestión Centralizada:** Si TradeDoubler cambia su prefijo de trackeo mañana, se cambia la lógica en el Backend sin alterar cientos de miles de URLs en el Frontend.
