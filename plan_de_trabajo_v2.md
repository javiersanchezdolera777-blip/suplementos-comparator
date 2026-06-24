# Plan de Acción y Reparto de Tareas (Proyecto V2)

Para cumplir vuestros dos grandes objetivos (crear la fachada para Awin y montar la arquitectura V2 profesional), propongo este reparto de trabajo donde **ambos vais a tocar tanto el código de la web como la lógica**.

Podéis decidir quién será el **Desarrollador 1** y quién el **Desarrollador 2**.

---

## 🏗️ Fase 1: La "Fachada" (Aprobación Rápida)
*Objetivo: Tener una web básica, funcional y bonita online en Vercel para que las plataformas de afiliación (Awin, TradeDoubler) vean que sois un proyecto serio.*

### Desarrollador 1: Estructura Frontend y Diseño Base
*   **Inicializar Next.js** en la carpeta `frontend/`.
*   **Diseño Principal (UI):** Crear el "Hero" (la cabecera) impactante que diga: *"El mayor comparador de suplementos de España"*.
*   **Páginas Clave para Afiliados:** Desarrollar el *Footer* (pie de página) y las páginas estáticas obligatorias para que os aprueben: *Quiénes Somos*, *Aviso Legal* y *Política de Privacidad*.

### Desarrollador 2: Mock Data (Datos Falsos) y Catálogo Visual
*   **Creación de Mock Data:** Crear un archivo `mock_products.json` con 10-15 productos de prueba bien estructurados (proteínas, creatinas de distintas marcas, precios, fotos sacadas de internet).
*   **Catálogo Visual:** Programar en Next.js la cuadrícula (`Grid`) de productos que lea de ese JSON falso y muestre las tarjetas de los productos en la web para que parezca que la tienda ya funciona.

---

## 🚀 Fase 2: Arquitectura Web V2 (El Motor Real)
*Objetivo: Empezar a construir el comparador real y robusto mientras esperáis la aprobación de las redes de afiliados.*

### Desarrollador 1: Backend (API REST) y Base de Datos
*   **Inicializar FastAPI** en la carpeta `backend/`.
*   **Diseño de la Base de Datos:** Crear los modelos profesionales (con SQLAlchemy o similar) definiendo exactamente cómo será un `Producto`, una `Marca` y una `Categoría`.
*   **Creación de Endpoints:** Programar las rutas de la API (por ejemplo: `GET /api/products`, `GET /api/categories`) utilizando los datos de prueba hasta que tengáis acceso a los *Data Feeds* reales.

### Desarrollador 2: Frontend Dinámico (Conexión y Lógica)
*   **Conexión API:** Modificar la "Fachada" para que deje de leer el archivo local JSON y pase a consumir la API real que está construyendo el Desarrollador 1 usando `fetch` o `axios`.
*   **Lógica de Filtros y Búsqueda:** Desarrollar los componentes dinámicos en React/Next.js: barra de búsqueda, sistema de filtrado por categoría, marca o precio, asegurando que las recargas sean ultrarrápidas.

---

## 💼 Tareas de Gestión (Para ambos)
Mientras programáis, debéis encargaros de la burocracia:
1.  **Inscripciones:** Uno de vosotros se da de alta en Awin, el otro en TradeDoubler y CJ Affiliate. Mandad la URL en cuanto la "Fachada" esté subida.
2.  **Investigación de Feeds:** Cuando os acepten, vuestra primera misión en la plataforma de afiliados es encontrar la sección de **Product Data Feeds** y averiguar en qué formato os van a enviar los catálogos (si es un XML, un CSV o una API REST).
