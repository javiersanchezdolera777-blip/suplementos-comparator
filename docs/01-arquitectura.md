# 2. MAPA COMPLETO DE LA ARQUITECTURA

## Visión General del Sistema
TusSuplementos es un monolito dividido en dos aplicaciones principales independientes (Frontend y Backend) orquestadas mediante servicios Cloud gestionados y una capa de base de datos relacional. No es una arquitectura de microservicios compleja, sino una aplicación de dos capas fuertemente acopladas por contrato de API (JSON), diseñada para escalabilidad en lectura y resiliencia en la ingesta de datos.

## Árbol de Directorios del Repositorio

El repositorio está organizado en dos carpetas raíz principales, además de configuraciones de CI/CD en `.github/`:

```text
/
├── .github/                 # Workflows de CI/CD (GitHub Actions)
│   └── workflows/
│       ├── cron_precios.yml # Pipeline de actualización de precios (cada 6h)
│       └── telegram_deals.yml # Generador de Top 5 en Telegram (10:00 y 20:00)
├── backend/                 # API REST y Motor de Ingesta (FastAPI / Python)
│   ├── alembic/             # Migraciones de base de datos (previsto para v2)
│   ├── ingestores/          # Módulos de extracción web
│   │   ├── base.py          # Clase abstracta BaseIngestor
│   │   ├── hsn.py           # Scraper dedicado de HSN
│   │   ├── pharma2go.py     # Ingestor del feed Tradedoubler (Farma2Go)
│   │   ├── sportlive.py     # Ingestor del feed Tradedoubler (SportLive)
│   │   └── utils.py         # Cerebro Central NLP de clasificación
│   ├── scripts/             # Tareas programadas y utilidades
│   │   ├── reset_cooldown.py# Script que resetea las alertas de TG tras 7 días
│   │   └── reprocesar_nlp.py# Script para reetiquetar la BD sin rescrapear
│   ├── services/            # Servicios de negocio externos
│   │   └── email_service.py # Interfaz con Resend
│   ├── actualizador_precios.py # Pipeline orquestador maestro (Upsert)
│   ├── database.py          # Conexión SQLAlchemy a Neon DB
│   ├── main.py              # Enrutador principal de FastAPI (Endpoints)
│   ├── models.py            # Esquema ORM de PostgreSQL
│   ├── newsletter_semanal.py# Motor de envío a Telegram/Email
│   ├── requirements.txt     # Dependencias Python
│   ├── retargeting_vistas.py# Motor de recordatorios de carritos/vistas
│   └── schemas.py           # Validación Pydantic (Request/Responses)
├── docs/                    # Documentación técnica y arquitectura
├── frontend/                # Aplicación Web y UI (Next.js 16)
│   ├── public/              # Assets estáticos (Favicon, logos)
│   ├── src/
│   │   ├── app/             # App Router (Páginas y layouts de Next.js)
│   │   ├── components/      # Componentes UI de React (ProductCard, Catalog, Navbar)
│   │   ├── context/         # Contextos globales de React (AuthContext)
│   │   ├── data/            # Mockups o diccionarios estáticos
│   │   ├── store/           # Zustand state management (store.ts para Modo Versus)
│   │   └── utils/           # Utilidades frontend (formateadores, fetchers)
│   ├── next.config.ts       # Configuración del compilador de Next
│   ├── package.json         # Dependencias NPM (React 19, Tailwind v4)
│   └── tailwind.config.js   # (Implícito o gestionado vía PostCSS en v4)
└── README.md
```

## Relación Frontend - Backend

La comunicación entre ambas capas se realiza exclusivamente a través de HTTP/HTTPS utilizando APIs REST.
1. **Flujo de Datos (Lectura):** Cuando un usuario entra al frontend (Next.js), este renderiza el cascarón de la UI. Los componentes (ej. `Catalog.tsx`) realizan peticiones asíncronas con `fetch` a `/api/productos` en el backend (FastAPI).
2. **Flujo de Datos (Escritura):** Acciones como login, guardar un favorito, o registrar un check-in diario lanzan peticiones POST que el backend valida mediante Pydantic y guarda en PostgreSQL mediante SQLAlchemy.
3. **Autenticación (JWT Híbrido):** El frontend utiliza Google OAuth 2.0 para obtener un token de identidad de Google. Lo envía al backend, quien lo valida contra Google, comprueba que el usuario existe (o lo crea) y devuelve su propio JWT firmado (`access_token`) que el frontend guarda para autenticar futuras peticiones.

## Servicios Externos Integrados

El proyecto depende de los siguientes servicios SaaS de terceros:
*   **Vercel:** Hosting y Edge CDN para el frontend de Next.js. Provee las imágenes optimizadas y compila el SSR/CSR.
*   **Render:** Hosting del contenedor o servicio web del backend (FastAPI). Proporciona URL pública (`api.tussuplementos.com` o similar).
*   **Neon DB:** Proveedor de PostgreSQL Serverless. Soporta ramificación (branching) para entornos de desarrollo.
*   **Resend:** API de envío de correos transaccionales (usada en `email_service.py` para alertas y newsletters).
*   **Telegram Bot API:** Interfaz para el envío automático de notificaciones de chollos a un canal público de Telegram (`newsletter_semanal.py`).
*   **Google OAuth:** Proveedor de identidad para el login de usuarios.
*   **Redes de Afiliación (Tradedoubler, Awin):** Proveedores de los catálogos en crudo (XML/JSON/CSV) y generadores de los enlaces traqueados.

## Flujo de Vida de un Producto (Data Pipeline)
1. **Extracción (Scraping/API):** CRON jobs en GitHub Actions levantan el entorno Python y ejecutan `actualizador_precios.py`. Este invoca a los ingestores (HSN, Farma2Go).
2. **Normalización NLP:** Los datos extraídos en crudo se pasan por `utils.py` (Cerebro NLP). Se asientan variables como `es_vegano`, `tipo_proteina`, formato, se limpia el nombre y se extrae el sabor.
3. **Upsert (BBDD):** El ingestor comprueba la BBDD (Neon). Si el producto (slug) existe, hace UPDATE de precios y estado. Si no, hace INSERT. Todo mediante transacciones seguras (`db.commit()`).
4. **Disponibilidad:** El backend expone inmediatamente los nuevos datos en `/api/productos`.
5. **Notificación:** Si un producto bajó agresivamente de precio y pasa el *Filtro Antimonopolio*, `newsletter_semanal.py` lo detectará en su próxima barrida y lo enviará al canal de Telegram y correo.
6. **Consumo UI:** El usuario refresca la página, el frontend pinta los datos y resalta la oferta (Modo Top Ofertas).
