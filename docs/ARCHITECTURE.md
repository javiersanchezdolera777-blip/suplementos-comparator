# Arquitectura de "Tus Suplementos"

Este documento consolida la arquitectura tecnológica del proyecto, sirviendo como la única fuente de verdad operativa.

## Stack Tecnológico Completo

*   **Frontend:** Next.js App Router (React 19, TypeScript, Tailwind CSS). Alojado en **Vercel** (Dominio de producción: `https://www.tussuplementos.com` con redirección desde `.es`).
*   **Backend:** FastAPI (Python). Alojado en **Render**.
*   **Base de Datos:** PostgreSQL alojada en **Neon DB**. La arquitectura de datos implementa una estricta separación de entornos, utilizando la rama principal para Producción y una rama segregada (`dev-ofertas`) para Staging y Desarrollo.

## Estructura del Backend

El backend se estructura bajo un modelo de API REST rápida y eficiente, conectado a PostgreSQL mediante SQLAlchemy.

*   **Modelos de Base de Datos (`models.py`):**
    *   `Producto`: Almacena el catálogo consolidado (precio, formatos, macros, métricas por kg, tienda).
    *   `Marca`: Entidad maestra de las marcas. Agrupa distintas gamas bajo nombres paraguas unificados.
    *   `Categoria`: Categorías estandarizadas (Proteínas, Creatinas, Vitaminas, etc).
*   **Esquemas Pydantic v2 (`schemas.py`):** Definen la validación y serialización de los datos (respuesta paginada, modelos de productos, diccionarios de normalización).
*   **Endpoints Activos (`main.py`):**
    *   `GET /api/productos`: Endpoint maestro de catálogo con ordenación inteligente, búsqueda y filtros cruzados.
    *   `GET /api/config/filtros`: Entrega los valores disponibles dinámicamente.
    *   `GET /api/marcas`: Devuelve el catálogo de marcas filtrado estrictamente a aquellas que tienen stock activo (evitando fantasmas).
    *   `POST /api/click/{product_id}`: Tracking de popularidad.

## Pipeline ETL Híbrido

El sistema de ingestión se nutre de datos de múltiples tiendas, unificándolos bajo un sistema resiliente basado en un motor de extracción (Scraper/Feeds) y un Procesador NLP (Cerebro Central).

*   **Arquitectura `BaseIngestor` (`ingestor_generico.py`):** Clase abstracta que unifica y estandariza los flujos de carga, borrado, parseo y persistencia para cualquier nueva tienda.
*   **Extractor Resiliente HSN (`hsn.py`):** Scraper blindado con sistema de backoff (reintentos) y borrado hiper-estricto por tienda (`tienda == "HSN"`). Destaca por su algoritmo exhaustivo de validación de marcas en 4 Fases (JSON-LD, URL, HTML, Regex) diseñado para superar las limitaciones de temas dinámicos (como Hyvä Theme) y erradicar los falsos positivos por parámetros de rastreo (UTMs).
*   **Cerebro Central NLP (`utils.py`):** Motor avanzado de clasificación que centraliza toda la lógica de catalogación (categoría, formato, tipo, sabor). También incluye el análisis centralizado de alérgenos y dietas, estandarizando de manera robusta las etiquetas `es_vegano`, `sin_gluten` y `sin_lactosa` a través de todas las fuentes. Resuelve colisiones complejas (ej. "Colágeno Hidrolizado" -> Salud; "NAC" -> Aminoácidos).
*   **Filtro Antimonopolio y Umbrales Dinámicos:** El motor de ingesta incorpora inteligencia de negocio aplicando umbrales de descuento dinámicos por categoría en tiendas masivas como HSN (30% para Proteínas y Creatinas, 40% para Aminoácidos/Pre-entrenos, 50% para el resto). Esto evita saturar la sección de ofertas y fomenta la diversidad del catálogo.
*   **Gestión de Feeds de Afiliados:** Procesamiento de fuentes complejas como Tradedoubler (Farma2Go). Tras el diagnóstico de sus limitaciones operativas, se ha dictaminado la necesidad arquitectónica de implementar un **motor de historial de precios propio** (Price History Engine) a futuro, dado que los feeds de terceros no siempre proveen un precio base o MSRP consistente para identificar chollos reales.
*   **Normalización de Marcas (`schemas.py`):** Embudo estricto que agrupa marcas dispersas (ej. *Sport Series*, *Raw Series* -> *HSN*) y mantiene la pureza de marcas internacionales (*NOW Foods*, *Swanson*).

## Sistema de Ordenación por Relevancia

El orden por defecto del catálogo (cuando no se especifica precio ascendente o descendente) utiliza un algoritmo de relevancia mixto:

```python
# 1º Productos con más clics reales de usuarios
# 2º Orden natural de inyección (Página 1 de la tienda original)
query = query.order_by(
    models.Producto.clics_count.desc(),
    models.Producto.id.asc()
)
```

## Estrategia DevOps y CRONs
- **Aislamiento de BD:** Establecer obligatoriamente bases de datos separadas (Local vs Neon DB) para el desarrollo de la Multitienda.
- **Ingesta No Destructiva (Upsert):** Prohibido el uso de `delete()` global. Los productos agotados/desaparecidos cambiarán a `activo=False` para ocultarlos sin vaciar la web (Gestión Avanzada de Stock).
- **Persistencia Resiliente:** El sistema obliga a realizar volcados forzosos (commits) por lotes y al final de cada ejecución, garantizando que ninguna actualización en memoria se pierda en cierres abruptos o fallos de red.
- **CRON de Precios:** Recuperar/verificar el CRON que actualiza precios 4 veces al día.
- **CRON Monitor de Scrapers:** Crear un script centinela que avise si la estructura DOM de una tienda o el Datafeed cambia, para detectar roturas proactivamente.

## Sistema de Notificaciones y Engagement

El ecosistema de comunicaciones está diseñado bajo un modelo SaaS premium, enfocado en maximizar el CTR (Click-Through Rate) y mantener una alta entregabilidad (Deliverability).

*   **Arquitectura de Notificaciones (Email):** Todo el tráfico saliente (Correos de Bienvenida, Alertas de Precio y Resumen de Favoritos) está centralizado de manera estricta en `services/email_service.py`. Se utilizan plantillas HTML/CSS inline con identidad corporativa, asegurando la inclusión dinámica de imágenes (inyectadas desde `actualizador_precios.py`) y jerarquías visuales orientadas a conversión.
*   **Retargeting Automatizado:** El módulo `retargeting_vistas.py` emplea estructuras de datos unificadas (`Set()`) para garantizar que el usuario reciba recomendaciones únicas de su historial. Dispone de trazas de depuración de primer nivel (captura y volcado directo del *response* de la API de Resend) e implementa un riguroso *cooldown* anti-spam de 7 días.
*   **Canal Telegram "VIP":** Transición hacia notificaciones altamente interactivas a través de Botones Inline nativos de Telegram (`reply_markup`). El formato del texto (`parse_mode="HTML"`) destaca los chollos y aplica estilos limpios adaptados a lectura rápida en móvil.
*   **Seguridad, Estabilidad y Resiliencia:** 
    *   **Patrón Fail-Fast:** Los scripts y servicios de notificación validan de forma agresiva sus tokens (ej: `RESEND_API_KEY`) al inicio del ciclo de vida; si faltan, interrumpen la ejecución explícitamente (`sys.exit(1)`) para evitar fallos silenciosos en producción.
    *   **Filtros de Cordura Matemática:** El cálculo del "Ratio de Oro" (€/kg) se blinda validando rangos lógicos (entre 2€ y 100€), descartando errores de precio o gramaje arrastrados del scraping.
    *   **Garantía Visual:** El pipeline `actualizador_precios.py` inyecta sistemáticamente `imagen_url` en la cola de alertas, previniendo el colapso visual de los correos automáticos.

## Ecosistema de Funcionalidades (V1)

*   **Motor NLP de Clasificación Quirúrgica:** Análisis léxico avanzado en tiempo de ingesta que detecta formatos (polvo, cápsulas, gominolas), sabores (diccionario gourmet), alérgenos y macronutrientes esenciales.
*   **Modo Versus (Comparador Cara a Cara):** UI premium para comparar hasta 4 productos simultáneamente, con mapeo inteligente de características y sincronización global de estado mediante Zustand.
*   **Ecosistema Social ("El IG de Suplementos"):** Perfiles de usuario (`@username`), red de seguidores, y publicación de *Stacks* (rutinas de suplementación).
*   **Gamificación Activa:** Check-ins diarios, rachas (streaks) y puntos de experiencia (XP) para fidelizar y retener usuarios.

## Roadmap de Producto / Features Pendientes
- **Migración a Multi-Tienda (Sprint 4):** Transición del catálogo plano a un esquema relacional donde `Producto` sea una entidad abstracta padre y los `Precios` residan en una tabla hija `Oferta` vinculada a `Tienda`. Esta migración requerirá el uso estricto de **Alembic** para gestionar las migraciones de base de datos de forma segura.
- **Algoritmo Antimonopolio:** Modificar la ordenación por defecto de `/api/productos` para evitar que HSN monopolice las primeras páginas del catálogo, fomentando la diversidad de marcas.
- **Optimizador de Afiliados:** Reducir la latencia de las redirecciones de Tradedoubler hacia SportLive/Farma2Go.
- **Nuevas Tiendas:** Integrar Aminha Farmacia y Bulk (vía Awin, requerirá scraper sin datafeed).

## Configuración de Entorno (Environment Variables)

Para garantizar la seguridad y la correcta conexión entre servicios, el proyecto utiliza variables de entorno. 

### Frontend (`frontend/.env.local` y Panel de Vercel)
- `NEXT_PUBLIC_API_URL`: URL base del backend (ej: `http://localhost:8000` en local, o la URL de Render en producción).
- `NEXT_PUBLIC_GA_ID`: ID de Google Analytics.
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: Identificador del cliente OAuth de Google para el Login.

### Backend (`backend/.env` y Panel de Render)
- `DATABASE_URL`: Cadena de conexión a la base de datos PostgreSQL (Neon DB).
- `GOOGLE_CLIENT_ID`: Debe ser **idéntico** al `NEXT_PUBLIC_GOOGLE_CLIENT_ID` del frontend. Se usa para verificar la integridad del token recibido (Audience Match).
- *Otras:* `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `RESEND_API_KEY`.

> [!WARNING]  
> **Guía de Despliegue Crítica:** Debes configurar todas estas variables de entorno en los paneles de control de tus respectivos hostings (Vercel para el Frontend y Render para el Backend) **ANTES** de realizar el primer despliegue. Si un despliegue se inicia sin las variables inyectadas, fallarán los builds o, peor aún, los endpoints de autenticación y base de datos rechazarán las conexiones.

## Autenticación y Seguridad (OAuth Google)

El proyecto utiliza una arquitectura de autenticación JWT híbrida. El frontend obtiene el token de Google y el backend lo valida e intercambia por un JWT propio.

> [!IMPORTANT]  
> **Añadir dominios a Google Cloud Console:** Si despliegas la aplicación en un nuevo dominio (o quieres probarla en un entorno distinto a localhost), es obligatorio ir a la [Google Cloud Console](https://console.cloud.google.com/), navegar a **API y Servicios > Credenciales**, seleccionar tu Cliente OAuth 2.0 y añadir el nuevo dominio a las listas de:
> - **Orígenes autorizados de JavaScript** (ej: `https://www.tussuplementos.com`)
> - **URI de redireccionamiento autorizados**
