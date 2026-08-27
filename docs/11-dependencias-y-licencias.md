# 14. DEPENDENCIAS Y LICENCIAS

Se ha realizado una auditoría estática de los archivos `package.json` (Frontend) y `requirements.txt` (Backend). No se detectan dependencias con licencias altamente restrictivas (como AGPL-3.0) que pudiesen obligar a abrir el código fuente (Open Source) del modelo de negocio de TusSuplementos. La mayoría operan bajo licencias permisivas (MIT, Apache 2.0, BSD).

## Backend (`requirements.txt`)

| Dependencia | Versión (Aprox) | Uso / Función | Licencia | Riesgo / Consideración |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI** | 0.100+ | Framework web (API REST). | MIT | 🟢 Ninguno. Estándar de la industria. |
| **SQLAlchemy** | 2.0+ | ORM de Base de Datos. | MIT | 🟢 Ninguno. Versión 2.0 asegura tipado fuerte. |
| **Pydantic** | 2.0+ | Validación de esquemas y datos. | MIT | 🟢 Ninguno. Muy veloz (escrito en Rust). |
| **psycopg2-binary**| 2.9+ | Driver de conexión a PostgreSQL. | LGPL | 🟢 `psycopg2` puro asume compilación nativa. El binario está bien para V1, pero a largo plazo y gran escalabilidad, se sugiere pasar a `asyncpg` nativo. |
| **passlib[bcrypt]**| 1.7+ | Hashing de contraseñas de usuario. | BSD | 🟢 Ninguno. Criptografía segura. |
| **python-jose** | 3.3+ | Firma y verificación de tokens JWT. | MIT | 🟡 Librería algo desactualizada en mantenimiento. Evaluar paso a `PyJWT` si surgen CVEs. |
| **requests** | 2.31+ | Peticiones HTTP a Telegram/Feeds. | Apache 2.0 | 🟢 Ninguno. |
| **beautifulsoup4**| 4.12+ | Scraper HTML para HSN. | MIT | 🟢 Ninguno. |
| **lxml** | 4.9+ | Parser ultra-rápido para BeautifulSoup. | BSD | 🟢 Ninguno. Requiere librerías C en el host. |
| **resend** | Última | SDK oficial para emails de Resend. | MIT | 🟢 Ninguno. |
| **google-auth** | Última | Validación de credenciales OAuth2. | Apache 2.0 | 🟢 Ninguno. Oficial de Google. |

## Frontend (`package.json`)

| Dependencia | Versión | Uso / Función | Licencia | Riesgo / Consideración |
| :--- | :--- | :--- | :--- | :--- |
| **Next.js** | 16.2.x | Framework de React (App Router). | MIT | 🟢 Creador de Vercel, optimización nativa. |
| **React / React DOM**| 19.2.x | Motor UI de frontend. | MIT | 🟢 Versión muy vanguardista (Canary/RC). Asegurar estabilidad de features 19. |
| **Tailwind CSS** | v4 | Sistema de utilidades CSS. | MIT | 🟢 Ninguno. Migrado a v4 con PostCSS. |
| **Zustand** | 5.0+ | State Manager (Modo Versus, Auth). | MIT | 🟢 Excelente elección, más ligero que Redux. |
| **react-hot-toast**| 2.6+ | Alertas emergentes no intrusivas. | MIT | 🟢 Ninguno. |
| **@react-oauth/google**| 0.13+ | Botón y SDK de Login con Google. | MIT | 🟢 Ninguno. |
| **sharp** | 0.34+ | Optimizador de imágenes de Vercel. | Apache 2.0 | 🟡 **Cuidado:** Requiere explicitamente que `allowScripts` esté en `true` (ya configurado) para compilar los binarios en Vercel y no reventar la RAM. |

## Conclusión de Auditoría Legal
El proyecto es **completamente seguro a nivel de propiedad intelectual**. 
No hace uso de tecnologías GPL puras que pudieran contaminar la base de código. Se puede seguir desarrollando como un proyecto de código cerrado y comercial sin infringir los acuerdos de licenciamiento de los paquetes OSS (Open Source Software) integrados.
