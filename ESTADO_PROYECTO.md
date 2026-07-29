# ⚡ Suparator - Informe de Estado del Proyecto y Arquitectura Actual

> **Documento de Sincronización para Inteligencia Artificial (Gemini Agent / Equipo)**  
> **Fecha de Actualización:** 23 de Julio, 2026  
> **Estado:** 42 Productos Oficiales | Backend & Frontend Sincronizados | PR #23 & PR #24 Integradas en `main`

---

## 📌 1. Visión General del Proyecto

**Suparator** es la plataforma comparadora de suplementación deportiva líder en España (proteínas, creatinas, aminoácidos, vitaminas, etc.). Su objetivo es analizar, clasificar y comparar en tiempo real ofertas de tiendas oficiales (Tradedoubler / Afiliación), permitiendo al usuario filtrar por especificaciones técnicas avanzadas (tipo de proteína, sello de calidad como Creapure, opciones veganas, formato, sabores) y redirigir con enlaces de afiliado.

---

## 🛠️ 2. Stack Tecnológico

| Capa | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Frontend** | Next.js (App Router v16+), React 19, Tailwind CSS, TypeScript | Interfaz moderna, responsive, ultrarrápida, orientada a SEO y UX Premium. |
| **Backend** | FastAPI (Python 3.11+), SQLAlchemy ORM, Pydantic v2 | API RESTful asíncrona, robusta, altamente tipada e integrada con validación estricta. |
| **Base de Datos** | PostgreSQL (Neon DB en Producción) / SQLite (`suplementos.db` en Local) | Soporte para campos relacionales, arrays de sabores, JSON y filtrado dinámico. |
| **Autenticación** | JWT (JSON Web Tokens) & Google OAuth 2.0 | Sistema de usuarios y gestión de suplementos favoritos. |
| **Ingestión** | Python Pipeline (`ingestar_tradedoubler.py`) | Parsing automático, cálculo de precio/kg, limpieza de marcas, slugs SEO y filtrado de accesorios. |

---

## 🗂️ 3. Estructura y Mapa de Archivos del Proyecto

```text
app_suplementos/
├── backend/
│   ├── main.py                  # API Principal FastAPI: Endpoints de Productos, Filtros, Favoritos, Auth
│   ├── models.py                # Modelos ORM SQLAlchemy: Producto, Marca, Categoria, Usuario, Favorito
│   ├── schemas.py               # Schemas Pydantic & Enums: DTOs de respuesta en Inglés y validadores safe
│   ├── ingestar_tradedoubler.py # Pipeline de datos: Descarga feed, clasifica, calcula slugs y sube a BD
│   ├── reset_db.py              # Script de reseteo total de tablas de la base de datos
│   ├── seed.py                  # Script de siembra inicial / mock para tests locales
│   ├── database.py             # Configuración de conexiones SQLAlchemy (SQLite/Neon)
│   ├── security.py             # Funciones de hash de contraseñas y emisión de JWT
│   ├── .env                    # Configuración local (DATABASE_URL=sqlite:///./suplementos.db)
│   └── requirements.txt        # Dependencias de Python (FastAPI, SQLAlchemy, uvicorn, pydantic, etc.)
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx       # Root Layout de Next.js con AuthProvider
    │   │   ├── page.tsx         # Página de Inicio (Hero + Catalog)
    │   │   ├── favoritos/       # Vista de suplementos guardados por el usuario
    │   │   ├── legal/ privacy/ cookies/ about/ contact/ # Páginas estáticas informativas
    │   │   └── globals.css      # Estilos globales y utilidades Tailwind CSS
    │   ├── components/
    │   │   ├── Catalog.tsx      # Barra de Búsqueda (z-10), Sidebar de Filtros y Grid de Productos
    │   │   ├── ProductCard.tsx  # Tarjeta de producto + Modal de Vista Rápida (z-[9999], max-h-[85vh], decodeHTML)
    │   │   ├── Navbar.tsx       # Header Sticky (z-50) con Login/Logout y Favoritos (cursor-pointer)
    │   │   ├── LoginModal.tsx   # Modal de Autenticación con Google Auth y formulario
    │   │   └── Footer.tsx       # Pie de página responsive
    │   └── context/
    │       └── AuthContext.tsx  # Estado global de sesión y sync de IDs de Favoritos
    └── .env.local               # NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🗄️ 4. Modelo de Datos y Esquemas API

### 4.1. Modelo `Producto` (`backend/models.py`)
- `id`: Integer Primary Key.
- `nombre`: String (Indexado).
- `descripcion`: String.
- `precio`: Float.
- `imagen_url`: String.
- `afiliado_url`: String.
- `slug`: String (Indexado) — **Ruta dinámica SEO** (ej: `proteina-whey-isolate-sport-live`).
- `peso_gramos`: Integer (Opcional) — Ej. 1000 para 1 kg.
- `precio_por_kg`: Float (Opcional) — Calculado automáticamente en la ingesta.
- `categoria_id` / `marca_id`: Foreign Keys relacionales.
- `objetivo`: String (Volumen Muscular, Pérdida de Peso, Rendimiento, Salud).
- `sabor`: JSON / Array — Soporta **múltiples sabores por producto** (ej. `["Vainilla", "Chocolate"]`).
- `formato`: String (Polvo, Cápsulas, Líquido, Barrita).
- `es_vegano`: Boolean.
- `sello_calidad`: String (Creapure, Lacprodan, Kyowa, Isolac, Optipep).
- `tipo_proteina` / `tipo_creatina` / `perfil_aminoacidos` / `tipo_vitamina`: Sub-filtros específicos por categoría.

### 4.2. Schemas de Respuesta Pydantic (`backend/schemas.py`)
- Mapean los campos de la BD en español a nombres estandarizados en **Inglés para el Frontend**:
  - `nombre` ➔ `name`
  - `descripcion` ➔ `description`
  - `precio` ➔ `price`
  - `imagen_url` ➔ `image_url`
  - `afiliado_url` ➔ `affiliate_url`
  - `sabor` ➔ `flavor` (`List[str]` con validador `@field_validator` de tolerancia retrocompatible).
  - `es_vegano` ➔ `is_vegan`
  - `sello_calidad` ➔ `quality_seal`

---

## 🚀 5. Historial de Hitos Recientes e Integraciones

### 🔀 PR #23: Mejoras de Tradedoubler y Rutas SEO por Diego
- **Limpieza de Catálogo:** Se añadió filtro para excluir accesorios o merchandising (Shakers, botellas, camisetas), reduciendo el dataset a **42 productos de suplementación oficial**.
- **Slugs SEO:** Generación automática de `slug` mediante `generar_slug()` en la ingesta para soportar URLs amigables de Google.
- **Normalización:** Inclusión de `CategoriaEnum` y `normalizar_marca()`.

### 🎨 PR #24: Sprint UX/UI & Resiliencia del Modal
- **Solución Definitiva de Z-Index:** Overlay del modal ajustado a `fixed inset-0 z-[9999] bg-black/70 backdrop-blur-md`, flotando 100% por encima de la barra de búsqueda (`z-10`) y la Navbar (`z-50`).
- **Centrado en Viewport:** Tarjeta interna configurada con `max-h-[85vh] my-auto overflow-y-auto` para garantizar espacio vertical en cualquier pantalla.
- **Botón de Cierre 'X':** Reposicionado sin colisionar con el botón de Favoritos (que cuenta con margen de seguridad `pr-12`).
- **Sanitización HTML:** Creado helper `decodeHTML()` en `ProductCard.tsx` que convierte entidades como `&#8211;` ➔ `–` y `&amp;` ➔ `&`.
- **Auto-Reset de Descripción:** Creado helper `closeModal()` que resetea `isExpanded = false` al cerrar el modal, garantizando que vuelva a abrirse colapsado.
- **Interactividad:** Clase `cursor-pointer` agregada en todos los elementos interactivos del Modal y Navbar.

---

## 🎯 6. Próximos Pasos Recomendados para el Desarrollo

1. **Rutas Dinámicas SEO en Frontend (`/producto/[slug]`):**
   - Crear la página de producto individual en Next.js App Router (`frontend/src/app/producto/[slug]/page.tsx`).
   - Implementar Server-Side Rendering (SSR) / Metadata dinámico (`generateMetadata`) para optimizar el posicionamiento en buscadores (Google OpenGraph, Schema.org de Producto).

2. **Endpoints de Slug en Backend (`main.py`):**
   - Añadir endpoint `@app.get("/api/productos/slug/{slug}")` para consultar productos directamente por su slug.

3. **Paginación & Carga Infinita en Catálogo:**
   - Aprovechar los parámetros `skip` y `limit` ya soportados en `/api/productos` para añadir paginación o Scroll Infinito en `Catalog.tsx`.

4. **Comparador Lado a Lado (Side-by-Side):**
   - Añadir un estado de "Comparar" que permita seleccionar 2 o 3 suplementos y ver sus tablas comparativas de precio/kg y especificaciones.

---

> **Instrucciones para el Agente Gemini:**  
> Este documento representa la fuente de verdad del estado actual del repositorio. Utilízalo para orientar cualquier nueva modificación, refactorización o desarrollo de características.
