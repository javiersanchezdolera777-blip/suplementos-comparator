# 6. FUNCIONAMIENTO DEL CATÁLOGO

## Origen de los Productos (ETL Pipeline)
El catálogo de TusSuplementos es un repositorio vivo que se nutre mediante un proceso ETL (Extract, Transform, Load) totalmente automatizado. No existe carga manual de productos por parte de administradores a través de un panel de control CMS.

Actualmente, los datos provienen de tres vías/tiendas, integradas en el backend bajo la carpeta `backend/ingestores/`:
1.  **HSN (`hsn.py`):** Un scraper programado (BS4/Python) que parsea directamente el HTML y metadatos JSON-LD de la web oficial de HSN. Es el ingestor más complejo, con un embudo de 4 fases para aislar marcas reales dentro de su marketplace.
2.  **Farma2Go (`pharma2go.py`):** Cliente que procesa un *Datafeed* estructurado (XML/JSON) proporcionado por la red de afiliación Tradedoubler.
3.  **SportLive (`sportlive.py`):** Cliente que procesa un *Datafeed* de la misma red de afiliación.

Todos heredan de una clase abstracta `BaseIngestor` (`backend/ingestores/base.py`) que estandariza las normas de inserción, limpieza de marcas fantasma y manejo de base de datos.

## Transformación y Cerebro NLP (`utils.py`)
Antes de ser inyectado a la base de datos, el producto "crudo" pasa por el "Cerebro Central NLP", un potente motor léxico (`backend/ingestores/utils.py`).

Este motor es la piedra angular del catálogo y se encarga de:
*   **Deducción de Categorías:** Aplica lógica en cascada (ej. si la descripción incluye "aislado de suero" -> Categoría: "Proteínas", Tipo: "Isolate").
*   **Limpieza de Ruido Comercial:** Traduce formatos comerciales crípticos a nombres limpios para la interfaz del usuario (`normalizar_descripcion_ui`).
*   **Extracción de Sabores y Alérgenos:** Lee arrays y descripciones masivas, buscando variaciones como "0% lactosa", "gluten free", "sin gluten" para instanciar en `True` las banderas booleanas `sin_gluten` y `sin_lactosa`.

## Gestión de Variantes (Sabores/Formatos)
Actualmente, el sistema **no trata las variantes como SKUs independientes**.
*   **Formato/Envase:** Cada formato distinto (ej. Bote 500g vs Saco 2kg) entra como un producto distinto, porque los Datafeeds y scrapers suelen servirlos como entidades separadas con distintos precios base.
*   **Sabores:** Si una tienda expone los sabores como un Array o menú desplegable bajo la misma URL, el ingestor captura el array y lo inyecta como un campo JSON `sabor` dentro de la tabla Producto. El motor NLP descifra qué sabor es.

## Inyección a BBDD (Upsert Masivo)
El bucle de inyección funciona bajo un patrón de "Upsert" (Update o Insert):
1.  Identifica un producto por un identificador único (generalmente un hash o el `slug` generado a partir del título y tienda).
2.  Si **existe**: Aplica `UPDATE` a todas sus columnas (`precio`, `precio_anterior`, metadatos) usando el método seguro `.get()`.
3.  Si **no existe**: Aplica `INSERT` creando el nuevo objeto SQLAlchemy.
4.  La persistencia se ejecuta acumulando el historial de memoria y disparando un único `db.commit()` masivo al final del lote para proteger la base de datos de bloqueos (locks).

## Sincronización y Actualizaciones
La automatización se rige por CRON Jobs de GitHub Actions (`.github/workflows/cron_precios.yml`).
*   **Frecuencia:** Se ejecuta de forma autónoma cada 6 horas (4 veces al día).
*   **Gestión de Agotados:** TusSuplementos aplica un borrado estricto ("Soft-delete" encubierto) en tiendas directas como HSN. En los feeds, si un producto ya no aparece en el XML de Tradedoubler, dejará de actualizarse.

## Histórico de Precios y Detección de Ofertas
*   El modelo `Producto` actual tiene una "memoria plana": `precio_anterior` y `precio`.
*   El backend detecta una oferta **al vuelo** (ON-THE-FLY) si `precio < precio_anterior`.
*   **Filtro Antimonopolio:** El script de notificaciones (`newsletter_semanal.py`) filtra qué chollos son reales aplicando umbrales categóricos calculados desde PostgreSQL: exige un -30% para que una Proteína se considere chollo, pero un -50% para "Otros".
*   **Problema Actual/Limitación:** No existe una tabla `historico_precios` dedicada que rastree los precios diarios de un SKU para pintar una gráfica. El `precio_anterior` (MSRP) es dictado ciegamente por lo que envía la tienda en su Datafeed, el cual a veces manipulan artificialmente (falsos descuentos). El Roadmap de Negocio advierte de la urgencia de construir un motor de histórico de precios propietario.

## Problemas de Escalabilidad Identificados
1.  **Explosión de SKUs Duplicados:** Puesto que un mismo bote de "Creatina Monohidrato 500g" vendido por HSN es un Producto, y vendido por SportLive es *otro Producto distinto* en la BBDD actual, la escalabilidad UX es mala (el usuario vería el bote dos veces en lugar de una ficha unificada "Ver precios en 2 tiendas"). El roadmap requiere refactorización hacia un modelo Relacional Multi-tienda V2 (Alembic).
2.  **Cuello de botella de scraping en directo:** A medida que se sumen tiendas como Bulk o MyProtein que bloquean spiders, la arquitectura actual de scraping sincrónico desde IPs de GitHub Actions podría fallar masivamente. Se requerirán proxies rotativos o APIs dedicadas.
