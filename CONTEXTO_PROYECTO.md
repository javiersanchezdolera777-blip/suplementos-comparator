# 🚀 Guía de Contexto del Proyecto: Suparator (Comparador de Suplementos V2)

Este documento contiene el estado actual, arquitectura, y objetivos del proyecto. **Si eres un agente de IA leyendo esto, asimila toda esta información antes de proponer código o soluciones.**

---

## 1. 🎯 Objetivo Principal del Proyecto
El objetivo es construir y desplegar **"El mayor comparador de suplementos de España"** llamado **Suparator**.
El modelo de negocio se basa en afiliación (CPA) a través de redes como Awin y TradeDoubler. La plataforma permite a los usuarios buscar, filtrar y comparar suplementos deportivos (proteínas, creatina, pre-entrenos) redirigiéndolos a los e-commerces originales con enlaces de afiliado.

---

## 2. 🗂️ Estructura del Equipo y del Repositorio
El proyecto está alojado localmente en `C:\Users\Javier\Desktop\app_suplementos\`.
El equipo está formado por:
*   **Javier:** Desarrollador Frontend (Next.js), gestor de negocio y afiliación.
*   **Diego Sánchez Cano:** Desarrollador Backend (Python/FastAPI) y bases de datos.

Carpetas principales:
*   `frontend/`: Aplicación web moderna (Next.js 13+ App Router, Tailwind CSS). Desplegada en **Vercel** (`https://suplementos-comparator.vercel.app`).
*   `backend/`: API REST (FastAPI, SQLAlchemy, SQLite/PostgreSQL). Desplegada en **Render** (`https://suplementos-comparator.onrender.com`).
*   `legacy_v1/`: Versión antigua deprecada basada en web scraping (solo para referencia).

---

## 3. 🚦 Estado Actual del Desarrollo (¡Estamos en la Fase 2 Avanzada!)

**✅ Fase 1 (MVP "Fachada"): COMPLETADA.** 
La web fue construida con datos mock para ser aprobados por las redes de afiliados. Se consiguió la aprobación de marcas clave como Bulk España a través de Awin.

**🚀 Fase 2 (Motor Real y Conexión Backend-Frontend): EN CURSO.**
Actualmente estamos integrando el frontend con el backend en producción.

**Estado del Backend (Diego):**
*   API operativa en Render.
*   Base de datos configurada con modelos de Producto, Categoría y Marca.
*   Nuevos superpoderes de la API:
    *   `/api/config/filtros`: Devuelve diccionarios para rellenar menús desplegables.
    *   Filtros dinámicos en la URL: `?categoria=...&sabor=...&formato=...&objetivo=...`
    *   Ordenación por precio: `?orden_precio=asc/desc`
    *   Búsqueda de texto libre: `?busqueda=creatina` (busca en nombre y descripción).
    *   Ruta individual: `/api/productos/{id}`
*   *Nota de datos:* A la espera de los Datafeeds oficiales (CSV) de Bulk y HSN para hacer un `seed` masivo en la base de datos de producción. Actualmente tiene unos pocos productos muy detallados (ver `mock_products.json` modificado) para probar los filtros.

**Estado del Frontend (Javier):**
*   Conectado con éxito a la API de Render mediante variable de entorno o fallback a la URL de Render.
*   La UI (`Catalog.tsx`) necesita actualizarse para consumir los endpoints de búsqueda, ordenación y los diccionarios de filtros (`/api/config/filtros`) creados por Diego.
*   Se ha verificado la propiedad del dominio en Awin (mediante archivo HTML en `public/`).

---

## 4. 💻 Stack Tecnológico

**Frontend (`frontend/`):**
*   **Framework:** Next.js (App Router).
*   **Lenguaje:** TypeScript / React.
*   **Estilos:** Tailwind CSS con estética Premium (Dark mode elegante, Glassmorphism, UI fluida).

**Backend (`backend/`):**
*   **Framework:** FastAPI (Python).
*   **ORM:** SQLAlchemy.
*   **Hosting:** Render (Plan gratuito: la API tarda ~50s en despertar en la primera petición si está inactiva).

---

## 5. 🗄️ Modelo de Datos Actual

Los productos en la base de datos ahora incluyen muchísima granularidad para permitir filtros avanzados. Un producto típico tiene:
*   `nombre`, `descripcion`, `precio`, `imagen_url`, `afiliado_url`.
*   Relaciones: `categoria` (ej. Proteína) y `marca` (ej. Optimum Nutrition).
*   Filtros específicos: `sabor` (ej. Chocolate), `formato` (ej. Polvo), `objetivo` (ej. Volumen Muscular).
*   `caracteristicas`: Objeto JSON con detalles técnicos (origen, procesado, sin lactosa, etc.).

---

## 6. 🤖 Instrucciones y Reglas para el Agente de IA

Cuando trabajes en este proyecto a partir de ahora, asume el siguiente contexto:
1.  **Trabajas codo a codo con Javier en el Frontend.** Diego se encarga del backend. Las respuestas deben centrarse en cómo implementar la UI de Next.js para consumir la API de Diego.
2.  **La API está en producción.** Usa siempre rutas relativas o variables de entorno (`process.env.NEXT_PUBLIC_API_URL`) para hacer `fetch`.
3.  **No añadas sistema de inicio de sesión (Auth).** Se ha decidido por negocio no poner barreras a los usuarios; el objetivo es que comparen y cliquen rápido en el enlace de afiliado.
4.  **Estética "Wow".** Todo componente que diseñes para el frontend debe lucir moderno, premium, con buenas animaciones y preparado para un mercado profesional.
5.  **Comunicación fluida.** Escribe de forma clara, directa y motivadora, recordando que es un proyecto conjunto entre Javier (Front) y Diego (Back).
