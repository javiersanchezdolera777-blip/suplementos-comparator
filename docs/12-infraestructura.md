# 15. DESPLIEGUE E INFRAESTRUCTURA

El stack tecnológico de TusSuplementos se apoya en un conjunto de servicios Cloud y metodologías Serverless, logrando un despliegue altamente escalable y casi sin mantenimiento de servidores (NoOps).

## Mapa de Infraestructura Cloud

| Componente | Proveedor / Servicio | Rol |
| :--- | :--- | :--- |
| **Frontend** | Vercel | Alojamiento del framework Next.js. Ejecuta el Edge CDN, la optimización de imágenes (sharp) y sirve el SSR/CSR. |
| **Backend** | Render | Servidor web que expone el puerto para Uvicorn/FastAPI. Permite despliegues directos desde GitHub y mantiene activa la API. |
| **Base de Datos** | Neon DB | Base de datos PostgreSQL Serverless. Soporta ramas de desarrollo separadas para no contaminar producción. |
| **Dominio** | Proveedor de dominios | `tussuplementos.com` como dominio canónico principal (asociado en Vercel) y `.es` configurado con redirección 301. |
| **Automatización**| GitHub Actions | Motores de orquestación (CRONs) que levantan contenedores temporales de Ubuntu, instalan dependencias y ejecutan scripts Python pesados. |

## Orquestación Automática (GitHub Actions)
Toda la operativa asíncrona del negocio (actualización de precios y publicación en redes) reside en `.github/workflows/`:

1.  **Pipeline de Precios (`cron_precios.yml`):**
    *   **Horario:** CRON `0 */6 * * *` (Cada 6 horas / 4 veces al día).
    *   **Acción:** Levanta una instancia Ubuntu-latest, instala Python 3.11 y ejecuta `backend/scripts/reset_cooldown.py` y luego `backend/actualizador_precios.py`.
    *   **Inyección:** Extrae `DATABASE_URL` y secretos de GitHub y se los inyecta al contenedor temporal.
2.  **Publicador de Chollos Telegram (`telegram_deals.yml`):**
    *   **Horario:** CRON `0 8,18 * * *` (10:00 y 20:00 hora de España).
    *   **Acción:** Ejecuta el motor de análisis antimonopolio y empuja los mensajes a la API de Telegram vía POST.

## Flujo de Despliegue (CI/CD)
Actualmente, el despliegue a producción es semiautomático basado en eventos de `push` a la rama `main` en GitHub.

1.  **Commit a GitHub:** El desarrollador sube los cambios (ej. merge de `feature/ui-ux-premium` a `main`).
2.  **Vercel Auto-Deploy (Frontend):** Vercel detecta cambios en la carpeta `frontend/`, ejecuta `npm run build` y redespliega la caché perimetral en pocos segundos.
3.  **Render Auto-Deploy (Backend):** Render detecta cambios en `backend/`, ejecuta el build de dependencias (pip) y reinicia el servicio Uvicorn sin downtime perceptible.

## Recomendaciones y Riesgos
*   **Logs y Monitorización:** Actualmente el backend imprime logs por consola (`print(...)`). Render permite verlos en directo, pero si ocurre un fallo silencioso a medianoche en el CRON, GitHub Actions lo marcará en rojo. Sería recomendable usar un servicio como Sentry para *Error Tracking* centralizado.
*   **Backups:** Neon DB ofrece historial (Point-in-Time Recovery), lo que permite revertir la base de datos a como estaba hace minutos u horas en caso de que un scraper inyecte precios corruptos (por ejemplo, 0.00€) y destruya el catálogo accidentalmente.
*   **DDoS y WAF:** Los Endpoints de Render están expuestos a internet. A escala masiva, convendría interponer Cloudflare frente a la API de Render para aplicar un cortafuegos de aplicaciones web (WAF) y mitigar raspadores de la competencia.
