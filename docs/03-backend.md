# 4. BACKEND

## Tecnologías Principales
*   **Framework:** FastAPI (Python 3.11+).
*   **Servidor ASGI:** Uvicorn.
*   **ORM:** SQLAlchemy (2.0+).
*   **Autenticación:** JWT (JSON Web Tokens) usando `python-jose` y OAuth de Google (`google-auth`).
*   **Peticiones HTTP Internas:** `requests` (para interacciones con resend, telegram).

## Arquitectura General
El backend de TusSuplementos es un monolito estructurado alrededor de la API RESTful. Sigue un patrón de arquitectura MVC-lite donde los controladores están directamente acoplados a las rutas (`main.py`) pero la capa de datos recae en SQLAlchemy (`models.py`) y la validación en Pydantic (`schemas.py`).

No hay arquitectura limpia o de capas abstractas complejas (Hexagonal o Clean Architecture), lo cual favorece la velocidad de desarrollo pero acopla fuertemente los endpoints a los modelos de SQLAlchemy.

## Tabla de Endpoints API Rest

A continuación, el mapa actual de rutas expuestas por el servidor FastAPI:

| Endpoint | Método | Función | Autenticación | Estado |
| -------- | ------ | ------- | ------------- | ------ |
| `/api/productos` | GET | Catálogo maestro (paginación, orden, NLP, filtros antimonopolio) | Opcional | 🟢 Operativo |
| `/api/productos/live-search` | GET | Búsqueda predictiva con tolerencia a fallos (trigramas/unaccent) | Pública | 🟢 Operativo |
| `/api/productos/comparar` | GET | Motor "Modo Versus", recibe array de slugs/ids y devuelve listado 1:1 | Pública | 🟢 Operativo |
| `/api/productos/{slug}` | GET | Detalle de un producto individual | Pública | 🟢 Operativo |
| `/api/config/filtros` | GET | Recupera conteos dinámicos de marcas y categorías para el Sidebar UI | Pública | 🟢 Operativo |
| `/api/auth/google` | POST | Intercambia token OAuth de Google por un JWT interno del backend | Pública | 🟢 Operativo |
| `/api/login/swagger` | POST | Puerta trasera de desarrollo (OAuth2PasswordRequestForm) | Pública | 🟡 Testing |
| `/api/auth/me` | GET | Verifica sesión y recupera entidad `Usuario` del JWT actual | Requerida | 🟢 Operativo |
| `/api/perfil/crear` | POST | Crea un `@username` (perfil público) asociado al usuario autenticado | Requerida | 🟢 Operativo |
| `/api/perfil/{username}`| GET | Devuelve el escaparate social de un usuario (stacks, puntos, biografía) | Opcional | 🟢 Operativo |
| `/api/comunidad/seguir/{username}`| POST | Añade un seguidor a otro usuario (relación M:M en DB) | Requerida | 🟢 Operativo |
| `/api/stacks` | POST | Crea una nueva rutina (Stack) pública o privada | Requerida | 🟢 Operativo |
| `/api/stacks/{stack_id}/productos/{producto_id}` | POST | Añade un suplemento al Stack | Requerida | 🟢 Operativo |
| `/api/comunidad/checkin`| POST | Gamificación: Acredita puntos diarios e incrementa racha (Streak) | Requerida | 🟢 Operativo |
| `/api/favoritos` | GET/POST/DEL | CRUD de wishlist privada del usuario | Requerida | 🟢 Operativo |
| `/api/historial/{producto_id}` | POST | Traquea la vista de un producto (para retargeting posterior) | Requerida | 🟢 Operativo |
| `/api/newsletter/subscribe` | POST | Opt-in para lista de correos | Pública | 🟢 Operativo |
| `/api/click/{product_id}` | POST | Aumenta el CTR de un producto para el algoritmo de relevancia | Pública | 🟢 Operativo |

## Middlewares y Seguridad
*   **CORS:** Configurado mediante `CORSMiddleware` para permitir peticiones desde el `FRONTEND_URL` y dominios autorizados de desarrollo.
*   **Rate Limiting:** Actualmente **NO** se observa un mecanismo agresivo de Rate Limiting (ej. `slowapi`) explícito en los endpoints, delegando esta función a Cloudflare o Render.
*   **Validaciones:** Todo el *payload* y parámetros GET se filtran a través de Pydantic Models.

## Tareas en Segundo Plano y CRONs
El backend opera tareas pesadas y de persistencia de manera externa vía GitHub Actions que ejecutan scripts Python dedicados:
1.  **Actualizador de Precios (`actualizador_precios.py`):** Motor Upsert. Llama a los ingestores (HSN, Farma2go, Sportlive) y actualiza la base de datos PostgreSQL masivamente cada 6 horas.
2.  **Newsletter y Telegram (`newsletter_semanal.py`):** Ejecutado a las 10:00 y 20:00. Selecciona los mejores chollos aplicando algoritmos de descuento y empuja las notificaciones vía Email (Resend) y Canal de Telegram.
3.  **Reset de Cooldown (`scripts/reset_cooldown.py`):** Borra diariamente el cooldown de 7 días para que productos antiguos puedan volver a emitirse en Telegram si bajan de precio nuevamente.
4.  **Retargeting (`retargeting_vistas.py`):** Sistema automatizado para envíos de carritos/vistas abandonados vía Email (Resend).

## Notas Técnicas y Gestión de Errores
*   **Tolerancia a fallos:** El sistema utiliza *Upserts* por lotes masivos. Las peticiones a la DB se hacen de forma síncrona.
*   **Seguridad:** Uso correcto de dependencias robustas (`passlib[bcrypt]`, `google-auth`). Faltan mecanismos contra inyecciones SQL ciegas derivadas del paginador si no se tipan fuertemente en Pydantic, aunque SQLAlchemy ya sanitiza *bind parameters* de forma nativa.
