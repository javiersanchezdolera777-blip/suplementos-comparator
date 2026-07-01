# 🚀 Guía de Contexto del Proyecto: Comparador de Suplementos V2

Este documento contiene todo el contexto necesario para que cualquier agente de IA pueda entender el proyecto actual, su arquitectura, objetivos y tecnologías. **Si eres un agente de IA leyendo esto, asimila toda esta información antes de proponer código o soluciones.**

---

## 1. 🎯 Objetivo Principal del Proyecto
El objetivo es construir y desplegar **"El mayor comparador de suplementos de España"**.
El modelo de negocio se basa en la monetización a través de redes de afiliación (como Awin, TradeDoubler y CJ Affiliate). Para poder operar con los *Data Feeds* reales de las marcas, primero necesitamos ser aprobados por estas plataformas. 

Por ello, el proyecto está dividido en dos grandes fases de desarrollo.

---

## 2. 🗂️ Estructura del Repositorio y Entorno
El proyecto se aloja en un entorno Windows bajo la ruta base: `C:\Users\Javier\Desktop\app_suplementos\`

Actualmente, el directorio contiene las siguientes carpetas principales:
*   `frontend/`: Donde residirá la aplicación web moderna para los usuarios.
*   `backend/`: Donde residirá la API REST profesional.
*   `legacy_v1/`: Contiene una versión anterior (basada en scripts de web scraping en Python y SQLite) que sirve únicamente como referencia histórica.
*   `plan_de_trabajo_v2.md`: Documento original con la repartición de tareas.

---

## 3. 🛠️ Fases de Desarrollo

### Fase 1: La "Fachada" (MVP Rápido para Aprobación)
El objetivo inmediato es tener una web con apariencia profesional, desplegada (idealmente en Vercel) y funcional, para que las redes de afiliados aprueben la solicitud del proyecto.

*   **Frontend (Next.js):** Creación del diseño base.
*   **Diseño UI/UX:**
    *   Un "Hero" (cabecera) impactante con el eslogan: *"El mayor comparador de suplementos de España"*.
    *   Un catálogo visual (Grid de productos).
*   **Datos "Mock":** Uso de un archivo `mock_products.json` con 10-15 productos de prueba (proteínas, creatinas, etc.) para simular que la tienda ya tiene integración de datos.
*   **Requisitos Legales:** Páginas estáticas obligatorias para las plataformas (*Quiénes Somos*, *Aviso Legal*, *Política de Privacidad*).

### Fase 2: Arquitectura Web V2 (El Motor Real)
Una vez aprobados (o en paralelo), se debe construir la infraestructura real que consumirá los *Data Feeds* de afiliados.

*   **Backend (FastAPI):** Desarrollo de una API REST ultra-rápida.
*   **Base de Datos:** Diseño robusto con SQLAlchemy.
*   **Frontend Dinámico:** Sustitución de los datos "Mock" por llamadas reales (`fetch`/`axios`) a la API de FastAPI. Implementación de barra de búsquedas y filtros por categoría, marca o precio sin recargas de página.

---

## 4. 💻 Stack Tecnológico (V2)

**Frontend (Carpeta `frontend/`):**
*   **Framework:** Next.js (App Router recomendado) / React.
*   **Lenguaje:** TypeScript / JavaScript (Priorizar modernidad y tipado si es posible).
*   **Estilos:** CSS Modules / Vanilla CSS o Tailwind CSS (según preferencia final, priorizando un diseño Premium, dinámico, con modo oscuro y animaciones fluidas).

**Backend (Carpeta `backend/`):**
*   **Framework:** FastAPI (Python).
*   **ORM:** SQLAlchemy.
*   **Base de datos:** Por definir (SQLite para desarrollo, migrable a PostgreSQL en producción).

---

## 5. 🗄️ Modelos de Datos (Propuesta para SQLAlchemy)

Para preparar la lógica de la V2, la base de datos debe soportar al menos estas entidades principales:

1.  **Categoría (`Category`):**
    *   `id` (PK), `name` (ej. "Proteína", "Creatina"), `slug`, `description`.
2.  **Marca (`Brand`):**
    *   `id` (PK), `name` (ej. "MyProtein", "HSN"), `logo_url`, `website_url`.
3.  **Producto (`Product`):**
    *   `id` (PK), `name`, `description`, `price`, `image_url`, `affiliate_url` (Link de redirección con el token de Awin/TradeDoubler), `brand_id` (FK), `category_id` (FK).

---

## 6. 🎨 Directrices de Diseño y UX
Es fundamental que el frontend tenga **Estética Premium**. No sirven diseños "básicos" o MVPs feos.
*   **Tipografía Moderna:** Usar fuentes limpias (ej. Inter, Roboto, Outfit).
*   **Colores y Contraste:** Paletas de colores armoniosas, uso inteligente del espacio en blanco o "Dark Mode" elegante (Glassmorphism, sombras sutiles).
*   **Interacciones:** Micro-animaciones al pasar el ratón (hover), transiciones suaves al filtrar, para que la web se sienta "viva".
*   **SEO Técnico:** Uso correcto de etiquetas HTML5 semánticas (`<header>`, `<main>`, `<article>`), metadatos y un solo `<h1>` por página.

---

## 7. 🤖 Instrucciones para el Agente de IA

Cuando trabajes en este proyecto, sigue estas reglas estrictamente:
1.  **Ubica el código donde corresponde:** Todo lo visual y de React va en `frontend/`. Toda la lógica de Python y APIs va en `backend/`. No toques `legacy_v1/` a menos que se te pida extraer algo.
2.  **Prioriza el código limpio:** Crea componentes pequeños y reutilizables en el frontend.
3.  **Asume el rol actual:** El usuario actual está ejecutando tareas de la **Fase 1 (Desarrollador 1)**. Céntrate en Next.js, Mock Data y diseño estético en este momento.
4.  **Si hay dudas:** Pregunta antes de instalar librerías pesadas o cambiar el Stack.
