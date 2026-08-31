# 13. SEGURIDAD Y VARIABLES DE ENTORNO

## Variables de Entorno (.env)
El proyecto requiere una orquestación estricta de variables de entorno, separadas físicamente entre Frontend (Vercel) y Backend (Render).

### Frontend (`frontend/.env.local`)
| Variable | Propósito | Nivel de Riesgo |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Define dónde ataca el `fetch` (ej. `http://localhost:8000`). | Bajo (Es pública). |
| `NEXT_PUBLIC_GA_ID` | Identificador de Google Analytics. | Bajo (Es pública). |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Client ID de OAuth. | Bajo (Expuesto en red). |

### Backend (`backend/.env`)
| Variable | Propósito | Nivel de Riesgo |
| :--- | :--- | :--- |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL (Neon DB). | 🔴 Crítico. |
| `GOOGLE_CLIENT_ID` | Idéntico al del front, para *Audience Match*. | Bajo. |
| `TELEGRAM_BOT_TOKEN` | Token para publicar en el canal. | 🔴 Crítico. |
| `TELEGRAM_CHAT_ID` | ID del canal destino. | Medio. |
| `RESEND_API_KEY` | Llave maestra para enviar emails. | 🔴 Crítico. |
| `FRONTEND_URL` | Configura el CORS y la generación de enlaces en emails. | Bajo. |

> [!WARNING]
> **Protección en Producción:** Ninguna de las variables del Backend debe ser commiteada en GitHub. El archivo `backend/.env` debe estar en el `.gitignore`.

## Autenticación y Autorización
TusSuplementos no gestiona contraseñas crudas. Se apoya en una arquitectura de **Token Híbrido**:
1.  **Google OAuth:** El usuario inicia sesión en el frontend mediante el SDK oficial de Google. El frontend recibe un Token de Identidad de Google.
2.  **Validación Backend:** El frontend envía este token a `/api/auth/google`. El backend verifica criptográficamente que el token fue emitido por Google y que la *Audience* coincide con el `GOOGLE_CLIENT_ID` local.
3.  **JWT Interno:** Si es válido, el backend genera un JWT propio firmado con la librería `python-jose`.

### 🔴 VULNERABILIDAD CRÍTICA DETECTADA: `SECRET_KEY` HARDCODEADA
En la auditoría del archivo `backend/security.py`, se ha detectado el siguiente fallo de seguridad grave:
```python
# 2. Configuración del JWT
# Nota: En un entorno real puro, el SECRET_KEY se guarda en el archivo .env
SECRET_KEY = "super_secreto_para_suplementos_comparator_api"
```
**Impacto:** Cualquier atacante con acceso al código fuente público (GitHub) o que pueda leer este archivo, puede generar "Pulseras VIP" (JWTs) válidas para cualquier cuenta, incluyendo administradores, saltándose el login de Google.
**Recomendación Inmediata:** Migrar `SECRET_KEY` al archivo `.env` mediante `os.getenv("JWT_SECRET_KEY")` y cambiar la semilla actual inmediatamente en producción.

## Protección contra Bots (Scraping) y Rate Limiting
*   **Falta de Rate Limiting:** FastAPI no tiene instalado `slowapi` ni middleware de rate limit. Un atacante podría lanzar un bucle `while True` contra `/api/productos` e inflar la factura de Render/Neon. Esto debe delegarse a la CDN (Cloudflare) o implementarse a nivel código.

## Validación de Inputs (Inyección)
*   **SQL Injection:** Protegido por diseño. El uso de SQLAlchemy 2.0 parametriza internamente todas las queries. Pydantic sanitiza los tipos en los endpoints.
*   **Cross-Site Scripting (XSS):** Protegido en gran medida por Next.js y React, que escapan el HTML de las descripciones de forma predeterminada (salvo que se use `dangerouslySetInnerHTML`, lo cual solo se ha detectado en el script controlado de TradeTracker).

## CORS (Cross-Origin Resource Sharing)
*   Está configurado en `main.py`. Es fundamental que `origins` en producción apunte estrictamente a `https://www.tussuplementos.com` y no permita wildcard `["*"]` para mutaciones POST/DELETE, con el fin de evitar ataques CSRF cruzados.
