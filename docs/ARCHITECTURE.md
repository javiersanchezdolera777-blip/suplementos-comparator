# Arquitectura de "Tus Suplementos"

Este documento consolida la arquitectura tecnológica del proyecto, sirviendo como la única fuente de verdad operativa.

## Stack Tecnológico Completo

*   **Frontend:** Next.js App Router (React 19, TypeScript, Tailwind CSS). Alojado en **Vercel** (Dominio de producción: `https://www.tussuplementos.com` con redirección desde `.es`).
*   **Backend:** FastAPI (Python). Alojado en **Render**.
*   **Base de Datos:** PostgreSQL alojada en **Neon DB**.

## Estructura del Backend

El backend se estructura bajo un modelo de API REST rápida y eficiente, conectado a PostgreSQL mediante SQLAlchemy.

*   **Modelos de Base de Datos (`models.py`):**
    *   `Producto`: Almacena el catálogo consolidado (precio, formatos, macros, métricas por kg, tienda).
    *   `Marca`: Entidad maestra de las marcas. Agrupa distintas gamas bajo nombres paraguas unificados.
    *   `Categoria`: Categorías estandarizadas (Proteínas, Creatinas, Vitaminas, etc).
*   **Esquemas Pydantic v2 (`schemas.py`):** Definen la validación y serialización de los datos (respuesta paginada, modelos de productos, diccionarios de normalización).
*   **Endpoints Activos (`main.py`):**
    *   `GET /api/productos`: Endpoint maestro de catálogo con ordenación inteligente, búsqueda y filtros cruzados.
    *   `GET /api/config/filtros`: Entrega los valores disponibles dinámicamente.
    *   `GET /api/marcas`: Devuelve el catálogo de marcas filtrado estrictamente a aquellas que tienen stock activo (evitando fantasmas).
    *   `POST /api/click/{product_id}`: Tracking de popularidad.

## Pipeline ETL Híbrido

El sistema de ingestión se nutre de datos de múltiples tiendas, unificándolos bajo un sistema resiliente basado en un motor de extracción (Scraper/Feeds) y un Procesador NLP (Cerebro Central).

*   **Arquitectura `BaseIngestor` (`ingestor_generico.py`):** Clase abstracta que unifica y estandariza los flujos de carga, borrado, parseo y persistencia para cualquier nueva tienda.
*   **Extractor Resiliente HSN (`hsn.py`):** Scraper blindado con sistema de backoff (reintentos), extracción dual (JSON-LD prioritario, HTML secundario) y borrado hiper-estricto por tienda (`tienda == "HSN"`).
*   **Cerebro Central NLP (`utils.py`):** Motor avanzado de clasificación que analiza nombres y descripciones para asignar categoría, formato, tipo de proteína, sabor y dietas (ej. vegano). Resuelve colisiones complejas (ej. "Colágeno Hidrolizado" -> Salud; "NAC" -> Aminoácidos).
*   **Normalización de Marcas (`schemas.py`):** Embudo estricto que agrupa marcas dispersas (ej. *Sport Series*, *Raw Series* -> *HSN*) y mantiene la pureza de marcas internacionales (*NOW Foods*, *Swanson*).

## Sistema de Ordenación por Relevancia

El orden por defecto del catálogo (cuando no se especifica precio ascendente o descendente) utiliza un algoritmo de relevancia mixto:

```python
# 1º Productos con más clics reales de usuarios
# 2º Orden natural de inyección (Página 1 de la tienda original)
query = query.order_by(
    models.Producto.clics_count.desc(),
    models.Producto.id.asc()
)
```
