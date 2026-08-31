# 7. SISTEMA DE COMPARACIÓN (MODO VERSUS)

## Descripción General
Una de las funcionalidades core de la plataforma es el "Modo Versus", un comparador técnico que permite enfrentar hasta 4 productos simultáneamente en una tabla unificada y responsiva. El objetivo de este comparador es eliminar el ruido del marketing y enfrentar métricas estandarizadas puras.

## Qué puede comparar el usuario
Actualmente, el Modo Versus permite visualizar y comparar:
*   **Identidad:** Marca y Tienda que vende el producto.
*   **Jerarquía de Precios:** Precio actual frente a Precio Original (con cálculo del % de descuento).
*   **"El Ratio de Oro":** El Precio por Kilogramo (`precio_por_kg`). Esta es la métrica más importante de la plataforma.
*   **Alérgenos:** Etiquetas NLP de `sin_gluten`, `sin_lactosa` y `vegano`.
*   **Macronutrientes clave (Limitado):** `% de Proteína` (si el motor NLP logró deducirlo del título o si el ingestor lo parseó de HSN).
*   **Disponibilidad de Sabores:** Cantidad de sabores extraídos.
*   **Formato y Presentación:** (ej. Polvo 2kg, 120 cápsulas).

## Arquitectura del Comparador

### 1. Motor de Estandarización de Precio (Backend)
El cálculo matemático del *Precio por KG* se procesa en `backend/ingestores/utils.py` (función `calcular_metricas_precio`).
1.  **Detección de Peso (`peso_gramos`):** El sistema escanea el nombre del producto, la presentación o el feed en crudo (ej. "Whey Protein 2 Kg", "Creatina 500g", "2.2 lbs"). Convierte todas las métricas de peso físicas (kg, g, lbs) a una unidad estándar: **Gramos**.
2.  **Cálculo del Precio por Kg:**
    ```python
    precio_por_kg = round((precio / peso_gramos) * 1000, 2)
    ```
3.  **Filtros de Cordura Matemática:** Si por algún error de extracción el precio/kg da un resultado aberrante (ej. 10.000€/kg) o inferior a un umbral ilógico (ej. 1€/kg), el sistema lo setea como `None` para evitar manipular el ranking de ofertas.

### 2. Estado en el Cliente (Frontend)
El estado temporal del Modo Versus se maneja íntegramente en el navegador mediante **Zustand** (`frontend/src/store/store.ts` o equivalente implementado).
*   Se almacena un Array de `slugs` (máximo 4).
*   Un botón flotante ("X en VS") persistente en la interfaz recuerda al usuario que tiene elementos listos para comparar.
*   Al abrir el modal/pantalla de Versus, el frontend dispara una petición al endpoint `GET /api/productos/comparar` pasando el array de IDs o Slugs.
*   El backend responde con el bloque exacto de productos en un solo Request, y un componente React `<table>` dibuja dinámicamente las columnas. El código está optimizado para ocultar filas de características donde ningún producto tiene datos (ej. si ninguno tiene *% de proteína*, la fila entera desaparece).

## Limitaciones Actuales y Escalabilidad
1.  **Precisión Nutricional (Macros):** A diferencia del *precio_por_kg*, el comparador **no** puede calcular ni comparar Calorías, Carbohidratos o Precio por Dosis/Servicio. Extraer tablas nutricionales de tiendas heterogéneas que no siguen un estándar JSON-LD estricto es un desafío extremo sin recurrir a un modelo LLM costoso o parsers muy frágiles (scraping de HTML de tablas nutricionales).
2.  **Límites Físicos en Móvil:** Para evitar una UX rota, el frontend restringe la comparación a un límite estricto (generalmente 2 o 3 columnas en móvil y 4 en escritorio).
3.  **Comparación Inter-Tienda:** Si un usuario quiere comparar "Proteína HSN vs Proteína MyProtein", la experiencia es excelente. Pero si quiere comparar el mismo bote exacto de "Optimum Nutrition Gold Standard" vendido en HSN vs vendido en Farma2Go, el comparador los tratará como dos productos desconectados con dos columnas, en lugar de agruparlos en una "Ficha Maestra" que unifique precios de un solo SKU (Roadmap Multitienda V2).
