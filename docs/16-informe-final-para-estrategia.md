# 20. INFORMACIÓN PARA ESTRATEGIA DE NEGOCIO, SEO Y MARKETING

Este documento está diseñado para el consultor estratégico, Growth Hacker o CMO (Chief Marketing Officer) que deba trazar el plan de adquisición y monetización de TusSuplementos, basándose en la realidad técnica del código.

## 1. ¿Qué activos tenemos ya?
*   **Un "Oráculo" de Suplementos:** Tenemos una base de datos brutalmente estructurada, donde cada producto no es un bloque de texto, sino que tiene identificados sus "ingredientes clave" (`tipo_proteina`, `porcentaje_proteina`, `alérgenos`).
*   **Comunidad Gamificada (Moat):** Un sistema completo de Perfiles sociales, Stacks (rutinas compartidas) y Check-ins diarios. Esto significa que **podemos generar recurrencia** más allá de las ventas.
*   **El Ratio de Oro (Precio/Kg):** Una métrica calculada matemáticamente imposible de falsificar por el marketing de las marcas, que aporta transparencia total.
*   **Broadcasting Automático:** Canales de distribución ya construidos y operando solos (Telegram, Email Newsletter, Motor de Retargeting de "abandonos").
*   **Filtro Antimonopolio:** Un algoritmo que asegura que nunca promocionemos falsas ofertas a nuestra comunidad.

## 2. ¿Qué nos falta para lanzar (Go-Live Marketing)?
*   **Cloaker de Afiliados:** Proteger los enlaces para que los AdBlockers no destruyan el tracking de ventas.
*   **Landings Dinámicas (SSR):** No tenemos `/categoria/proteinas-aisladas`. Si no hay landings estructuradas, no hay SEO *Inbound*.
*   **Rich Snippets (JSON-LD):** Que nuestros productos enseñen estrellitas de reseñas y el precio en verde en la primera página de Google.
*   **Aceptar las Cookies Legalmente:** Fundamental para que el Consent Mode v2 de Google permita a GA4 trackear legalmente en la UE.

## 3. ¿Qué tipo de páginas podemos escalar (SEO Programático)?
Dada nuestra BBDD, podemos (y debemos) generar las siguientes landings automáticas en Next.js para copar las búsquedas informacionales y transaccionales:
*   `/comparar/{slug-1}-vs-{slug-2}`: (Ej. *"HSN Evowhey VS MyProtein Impact Whey"*). Un clásico de SEO transaccional de muy alta conversión.
*   `/mejor/{categoria}`: (Ej. *"Mejor Creatina Monohidrato 2026"*). Rankings dinámicos basados en nuestro `clics_count` (Top 10 automáticos).
*   `/barato/{categoria}`: (Ej. *"Proteína Vegana Más Barata"*). Lista ordenada estrictamente por nuestro Ratio de Oro (`precio_por_kg`).
*   `/perfil/{username}/stack/{id}`: URLs compartibles generadas por los usuarios. Esto crea **User Generated Content (UGC)** y nos trae tráfico *long-tail*.

## 4. ¿Qué tipo de contenido podemos generar a partir de nuestros datos? (Redes Sociales)
El algoritmo y el catálogo nos dan oro para **TikTok, Instagram Reels y YouTube Shorts**:
*   **Formatos "Verdad vs Mentira":** Usar nuestro comparador de % de proteína. "Te crees que la marca X es barata, pero mira su % de proteína real en TusSuplementos..."
*   **Formato "El Chollo de la Semana":** Grabar la pantalla enseñando el Top 1 de nuestra Newsletter generado por el Filtro Antimonopolio.
*   **Formato "Review de Sabores":** Usar los datos de nuestra tabla `ResenaSabor`. "¿Cuál es el mejor sabor de la Proteína Y? La comunidad de TusSuplementos dice que es..."
*   **Compartir Stacks (Rutinas):** "Este es mi Stack de volumen por menos de 40€ al mes. Búscalo en mi perfil de TusSuplementos".

## 5. ¿Qué eventos y métricas podemos (y debemos) medir?
Para optimizar el CPA (Coste por Adquisición) y entender qué red social funciona mejor, necesitamos medir:
*   `view_item`: Cuando alguien entra a `/producto/[slug]`.
*   `add_to_wishlist`: Cuando alguien clica el corazón (favorito).
*   `click_affiliate` (CRÍTICO): Cuando clican "Ver Oferta". (Actualmente el backend cuenta clics globales, pero necesitamos que GA4 sepa si ese clic vino de un TikTok o de un Tweet).
*   `checkin_daily`: Para medir la salud y retención de la comunidad.

## 6. ¿Qué funcionalidades pueden aumentar la conversión de afiliación?
*   **Alertas de Precio (Tracker):** Permitir al usuario poner un target: "Avísame cuando esto baje de 20€/Kg". (Manda un email directo -> Alta tasa de conversión por intención de compra previa).
*   **Cupones Exclusivos Inyectables:** Que el "Modo Versus" muestre: *"Tienda A: 25€. Tienda B: 30€ (24€ con código TUSSUPLES)"*.
*   **Métricas de "Ahorras X€ al año":** Transmitir urgencia e impacto real comparando el Precio/Kg.

## 7. Ventajas Competitivas Reales frente a:

### A. Tiendas tradicionales (ej. HSN, Prozis)
*   Ellos tienen conflicto de interés; nunca te dirán que su competidor es más barato hoy. Nosotros **somos agnósticos e imparciales**, lo que genera confianza ciega en la comunidad.

### B. Blogs de suplementación
*   Los blogs son estáticos. Escriben "La mejor proteína 2024" y el artículo se queda desactualizado en un mes. TusSuplementos es **100% dinámico y en tiempo real**. El "Mejor X" cambia solo cada vez que corre el CRON a las 06:00 AM.

### C. Comparadores de precio genéricos (ej. KuantoKusta, Google Shopping)
*   Son incapaces de entender el contexto nutricional. Compararán un saco de 2kg de "Gainer" (barato, lleno de azúcar) con 2kg de "Isolate" (caro, puro).
*   Nuestro **Cerebro NLP (utils.py)** entiende que son categorías y calidades distintas, y las clasifica y compara por separado basándose en su % de proteína real. Además, nuestra capa comunitaria (Perfiles, Stacks) crea una tribu, mientras que Shopping es solo un motor de búsqueda frío.
