# Roadmap Actualizado del Proyecto

*Fecha de Revisión: 17 de Agosto de 2026*

Este Roadmap refleja el progreso real de la plataforma "Tus Suplementos" y define los próximos pasos estratégicos hacia la consolidación tecnológica del proyecto como un comparador multi-tienda avanzado.

---

## Sprint 1 (Quick Wins & UI) - [COMPLETADO ✅]
- [x] Implementar un logo visible y optimizado para móvil (isotipo responsive y favicon oficial).
- [x] Fix de la barra de búsqueda y optimización del menú responsive con bloqueo de scroll.
- [x] Estandarización de interfaz en Modo Claro Oficial de Alto Contraste.
- [x] Añadir filtros de alérgenos (Sin Gluten, Sin Lactosa, Vegano) en el frontend y backend.
- [x] Implementación de panel de Favoritos (Wishlist) y sistema de Autenticación con Google (JWT).

## Sprint 2 (Buscador Inteligente & Automatización) - [COMPLETADO ✅]
- [x] Motor Fuzzy Search (pg_trgm + unaccent) en PostgreSQL para tolerancia a erratas y tildes.
- [x] Endpoint ligero `/api/productos/live-search` con ranking de relevancia y normalización bidireccional de sinónimos.
- [x] SearchOmnibox interactivo en vivo con diseño premium de 4 resultados.
- [x] Pipeline de ejecución programada (CRON Scrapers / GitHub Actions) para actualización diaria de precios desatendida.
- [x] Bot de Chollos de Telegram desplegado con Strict CI/CD (Verificado funcionamiento autónomo en GitHub Actions).
- [x] Sistema de Relevancia (Ordenación por similitud de texto `pg_trgm` en el buscador).

---

## Sprint 3 (Notificaciones y Retención) - [COMPLETADO ✅]
Este Sprint se centró en la creación de un ecosistema de retención y alertas transaccionales, estableciendo el canal de comunicación directa con el usuario.

- [x] **Integración de Captación:** Diseño minimalista del Newsletter en el Footer UI y desarrollo del Endpoint en Base de Datos (Upsert).
- [x] **Configuración de Email Transaccional:** Integración de la API de Resend y configuración de DNS en Vercel para correos fiables y seguros.
- [x] **Motor de Alertas Agrupadas:** Sistema inteligente para notificar bajadas de precio de Productos Favoritos agrupando las ofertas en un solo correo para evitar el spam.
- [x] **Sistema de Tracking y Retargeting Anti-Spam:** Historial de Vistas silencioso con retargeting automático de los últimos productos visitados, protegido por una regla estricta de 7 días entre correos.
- [x] **Newsletter Semanal Híbrida:** Lógica algorítmica de "Top 5 Chollos" (priorizando suplementos core como Proteínas y Creatinas por descuento absoluto), difundido simultáneamente vía Email y Telegram.
- [x] **Orquestación Centralizada:** Delegación de todos los CRON jobs (Actualizador de Precios, Newsletter y Retargeting) en GitHub Actions de forma desatendida.

---

## Sprint 4 (El Comparador Multi-Tienda y Tablas de Análisis) - [NUEVO SPRINT ACTIVO 🔵]
El siguiente gran hito evolutivo transforma la plataforma de un catálogo unificado a un **comparador multi-tienda real**, permitiendo a los usuarios enfrentar productos idénticos vendidos por diferentes proveedores y comparar suplementos a nivel técnico y nutricional.

- **[ ] 4.1 Arquitectura Multi-Tienda (Gestión de Vendedores):**
  - Refactorizar el modelo de datos en PostgreSQL para implementar una jerarquía Padre-Hijo. Separar el "Producto Base" (ej. 100% Whey Gold Standard 2kg) de sus "Ofertas por Tienda" (relacionando las ofertas de HSN, Amazon, Miravia, Prozis, etc., al mismo producto core).
  - Migración de datos estructurada usando Alembic para preservar la integridad del catálogo actual.

- **[ ] 4.2 Lógica de Precios Inteligente:**
  - **Backend:** Desarrollar consultas agregadas que devuelvan el "Precio más barato" (Lowest Price) de entre todas las tiendas vinculadas a un producto.
  - **Frontend (Catálogo):** Mostrar dinámicamente el precio mínimo disponible en el grid.
  - **Frontend (Ficha de Producto):** Rediseñar la vista de detalle (`/producto/[slug]`) para renderizar un módulo comparativo con la lista de todas las tiendas, sus precios respectivos (ordenados de menor a mayor) y los enlaces de compra hacia cada plataforma de afiliación.

- **[ ] 4.3 UI/UX - Tablas de Análisis y Comparativa Técnica:**
  - **Mecanismo de Selección:** Implementar un botón "Añadir a comparativa" (estado global en React o localStorage) accesible desde las tarjetas del catálogo y la ficha técnica.
  - **Vista Comparador (Head-to-Head):** Crear una nueva página o modal expandible (`/comparar`) que despliegue una tabla técnica comparando de 2 a 4 suplementos frente a frente.
  - **Métricas a Comparar:**
    - Ratio económico: Precio por Kg / Precio por Dosis.
    - Perfil Nutricional (Macros): Proteínas, Kcal, Grasas, Hidratos de Carbono por 100g.
    - Aminograma y Sellos de Calidad: Destacar certificaciones premium (Creapure®, Lacprodan®, Kyowa®, AlzChem®).

---

## Sprint 5 (Expansión de Catálogo y SEO) - [PLANIFICADO ⚪]
- [ ] Conectar y estabilizar los ingestores de **MyProtein**, **Prozis** y **Miravia** al CRON diario de actualizaciones para alimentar el comparador multi-tienda.
- [ ] Inyección dinámica de Schema.org JSON-LD (Product, AggregateOffer) para optimización técnica.
- [ ] Estrategia de SEO programático (Landing pages automáticas por marca, categoría y objetivo).
- [ ] Caché de servidor (Redis/Memcached) para el endpoint principal de catálogo garantizando latencias <100ms.
- [ ] Creación de perfiles de usuario públicos ("Stack habitual / Instagram de suplementos").

## Sprint 6 (Comunidad, Gamificación y "Tamagotchi del Gym") - [NUEVO SPRINT ACTIVO 🚀]
Tras preparar el núcleo social en el backend, el esfuerzo se centra en construir el frontend para la mayor herramienta de retención de la plataforma.

- **[ ] 6.1 Dashboard "Mi Zona":** Construcción de la vista de perfil de usuario (`/comunidad/[username]`). Integración visual del sistema de Seguidores y puntos de Experiencia (XP) totales.
- **[ ] 6.2 El "Tamagotchi del Gym" (Componente UI):**
  - Desarrollo del componente React (`GymMascota.tsx`) que gestiona la evolución visual del usuario.
  - Lógica condicional anclada a los datos del backend: La mascota cambia de forma (Flaco/Gordito -> Fuerte -> Monstruo) cruzando la `XP` acumulada por los check-ins y el `objetivo_etapa` (Volumen o Definición).
- **[ ] 6.3 Fabricación de Assets Visuales:** Generación (vía IA) de los 6 sprites en formato `.png` (estilo vectorial, fondo transparente) para las fases de la mascota.
- **[ ] 6.4 Sistema de Stacks:** Maquetación de la cuadrícula de Stacks, reutilizando los componentes `ProductCard` del catálogo para permitir añadir productos favoritos a "Rutinas Públicas".