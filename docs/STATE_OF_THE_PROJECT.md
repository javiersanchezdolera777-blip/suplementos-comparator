# Estado Actual del Proyecto (STATE OF THE PROJECT)

*Fecha de Auditoría: 15 de Agosto de 2026*

Este documento sirve como la fuente de verdad absoluta sobre lo que está implementado, lo que está en pruebas y las áreas de mejora detectadas tras una auditoría exhaustiva de la arquitectura Full-Stack (Next.js + FastAPI + PostgreSQL).

---

## 🟢 Core Completado y en Producción

### 1. Backend y Base de Datos (FastAPI + Neon DB)
- **Autenticación (Google Auth / JWT):** Implementación sólida en `main.py` (`POST /api/auth/google`). Valida tokens de Google, crea/recupera usuarios en BD y emite un JWT firmado (`access_token`) con el framework de seguridad propietario (`security.py`).
- **Sistema de Favoritos (Wishlist):** CRUD completo y protegido por JWT. Rutas `POST`, `GET` y `DELETE` funcionales bajo `/api/favoritos`. Utiliza eliminación en cascada (`ON DELETE CASCADE`) para mantener la integridad referencial.
- **Buscador Inteligente (Fuzzy Search & NLP):** Motor semántico (`busqueda.py`) con diccionario bidireccional multilingüe y soporte de tildes. Totalmente integrado en el endpoint predictivo `/api/productos/live-search`.
- **Arquitectura de Modelos:** `models.py` robusto con control de clics (`clics_count`), control de notificaciones (`publicado_telegram`), control de historial de precio (`precio_anterior`) y metadatos nutricionales en JSON (objetivos, sabores, sellos de calidad).

### 2. Frontend (Next.js 14 App Router + Tailwind CSS)
- **Modo Claro Institucional:** UI/UX estabilizada y responsive. Diseño premium orientado a conversión.
- **SearchOmnibox:** Buscador predictivo en tiempo real (debounced a 200ms) con diseño amplio, mostrando 4 resultados premium con miniaturas de alta calidad y gestión defensiva de errores (fallback images).
- **Panel de Favoritos:** Página `/favoritos` conectada al `AuthContext` global. Pide Login al usuario anónimo y muestra el grid de productos guardados consultando a la API segura.
- **Filtros de Alérgenos:** Implementados en el Frontend (`FilterSidebar.tsx`) y soportados nativamente por el backend (`es_vegano`, `sin_gluten`, `sin_lactosa`).

### 3. DevOps y Automatización (Core)
- **Pipelines en Producción:** El orquestador de precios (`actualizador_precios.py`) está funcional en GitHub Actions (`cron_precios.yml`) a las 05:00 UTC operando de forma desatendida sobre la base de datos real.

---

## 🟡 En Desarrollo / Pendiente de Verificación

- **[⏳] Bot de Telegram para Chollos (`send_telegram_deals.py`):** El código ha sido blindado con *Strict CI/CD Error Handling* (Sale con Exit 1 si fallan los Secrets o la API). Queda confirmar mediante la ejecución desatendida programada en `.github/workflows/telegram_deals.yml` que el entorno virtual inyecta correctamente el `TELEGRAM_BOT_TOKEN` y publica chollos de forma efectiva.

---

## 🔴 Deuda Técnica y Bugs Conocidos

- **Vulnerabilidad de Migraciones:** No hay un sistema de control de versiones de la base de datos (como Alembic). Actualmente se usa `Base.metadata.create_all(bind=engine)`, lo que puede ser peligroso para futuras modificaciones estructurales en un entorno de producción con miles de usuarios.
- **Dependencia de Scripts Bloqueantes:** La orquestación del backend asume que el scraping o la conexión a BD no excederán tiempos límites. Faltan *timeouts* consistentes en los scrapers de origen (`hsn.py`, etc.).
- **Scraping Incompleto:** La base de datos tiene marcas como HSN preparadas, pero la ingesta de MyProtein y Prozis (requeridas en el Roadmap original) aún no está conectada al CRON principal.

---

## 💡 Mejoras Futuras Inmediatas (Next Actions)

1. **Expansión del Catálogo (Scraping):** Habilitar los conectores de MyProtein y Prozis en el flujo de automatización diario. Un comparador pierde sentido sin variedad de tiendas.
2. **Alertas Personalizadas (Favoritos):** Modificar el backend para que, cuando el CRON de precios detecte una rebaja, envíe un email transaccional (vía Resend o SendGrid) a los usuarios que tengan ese producto en `/favoritos`.
3. **Caché de Catálogo (Redis/Memcached):** La ruta principal `/api/productos` podría sufrir latencias elevadas si el tráfico escala. Se recomienda cachear la respuesta por 10-15 minutos.
4. **Login Alternativo (Apple/Email):** Ampliar el `AuthContext` actual. Muchos usuarios móviles de iOS prefieren *Sign in with Apple* sobre Google.
