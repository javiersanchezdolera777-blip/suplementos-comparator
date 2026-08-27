# Documentación Técnica Integral: TusSuplementos

Bienvenido a la documentación oficial y auditoría técnica del proyecto **TusSuplementos** (`tussuplementos.com`). 

Esta carpeta contiene una radiografía exhaustiva y veraz del estado actual del código, la infraestructura y el modelo de negocio, diseñada para que consultores externos, CTOs y expertos en Growth/SEO puedan entender el sistema al 100% sin necesidad de bucear en el código fuente de las capas de Next.js o FastAPI.

## Índice de Documentos

El análisis se ha dividido en los siguientes módulos especializados:

### Visión General y Arquitectura
*   [00-resumen-ejecutivo.md](./00-resumen-ejecutivo.md) - Propuesta de valor, usuario objetivo y estado general de las funcionalidades.
*   [01-arquitectura.md](./01-arquitectura.md) - Mapa completo del sistema, relación frontend-backend y árbol de directorios.

### Capas Tecnológicas y Bases de Datos
*   [02-frontend.md](./02-frontend.md) - Stack de Next.js (App Router), Tailwind V4, estado del CSR y SSR.
*   [03-backend.md](./03-backend.md) - FastAPI, enrutadores, CRONs y tabla completa de endpoints API.
*   [04-base-de-datos.md](./04-base-de-datos.md) - Esquema relacional PostgreSQL (Neon DB), entidades sociales y de catálogo.

### Reglas de Negocio Core (El "Motor")
*   [05-catalogo-y-productos.md](./05-catalogo-y-productos.md) - Funcionamiento del Cerebro NLP (`utils.py`), Ingestores y bucle Upsert.
*   [06-comparador.md](./06-comparador.md) - Arquitectura del "Modo Versus" y cálculos del Ratio de Oro (€/Kg).
*   [08-analitica.md](./08-analitica.md) - Diagnóstico del funnel, Google Analytics 4 y medición de CTR interna.
*   [09-afiliacion.md](./09-afiliacion.md) - Implementación actual de Tradedoubler/HSN y problemas de AdBlockers.

### SEO, Rendimiento e Infraestructura
*   [07-rutas-y-seo.md](./07-rutas-y-seo.md) - Inventario de URLs públicas, estado del renderizado y fallos de indexación críticos.
*   [12-infraestructura.md](./12-infraestructura.md) - Mapa Cloud: Vercel, Render, Neon y flujos de GitHub Actions.
*   [13-rendimiento-y-escalabilidad.md](./13-rendimiento-y-escalabilidad.md) - Cuellos de botella en la base de datos y búsqueda difusa (trigramas).

### Seguridad y Cumplimiento
*   [10-seguridad.md](./10-seguridad.md) - Auditoría de variables de entorno, autenticación JWT Híbrida y vulnerabilidades detectadas.
*   [11-dependencias-y-licencias.md](./11-dependencias-y-licencias.md) - Auditoría de licencias de librerías Python/NPM.

### Conclusiones Estratégicas y Roadmap
*   [14-riesgos.md](./14-riesgos.md) - Mapa de calor consolidado de vulnerabilidades (Técnicas, SEO, Usabilidad).
*   [15-roadmap-tecnico.md](./15-roadmap-tecnico.md) - Las 10 Fortalezas, las 10 Debilidades y las mejoras obligatorias antes de lanzar.
*   [16-informe-final-para-estrategia.md](./16-informe-final-para-estrategia.md) - Insights puros de negocio, formatos de RRSS sugeridos y ventajas competitivas.

---

## Las 10 Conclusiones Más Importantes del Proyecto

Para los directivos o inversores con poco tiempo, aquí están las 10 claves fundamentales del estado actual de TusSuplementos:

1.  **Backend "Bulletproof" (A prueba de balas):** El motor de procesamiento, ingesta (Scraping/Feeds) y categorización de PostgreSQL/FastAPI es de nivel corporativo. Funciona solo, no requiere intervención manual y es el mayor activo tecnológico de la empresa.
2.  **Cerebro NLP (Moat Defensivo):** La estandarización de proteínas y creatinas para eludir el marketing de las marcas (aislando alérgenos y formatos de manera automatizada) es una ventaja competitiva brutal frente a los comparadores generalistas tipo Google Shopping.
3.  **Vulnerabilidad de Seguridad Detectada:** Existe un fallo crítico (`SECRET_KEY` de encriptación JWT hardcodeada en el código fuente de Github) que debe parchearse **inmediatamente** moviéndola al `.env`.
4.  **Agujero Negro SEO:** El proyecto tiene un frontend atractivo pero es ciego para Google. Faltan Landings de Categorías estáticas (SSR) y marcado Schema.org (`Product`). Si se lanza hoy, dependerá 100% de tráfico social/pago, no rankeará en orgánico (Inbound).
5.  **Fuga de Conversiones (Afiliados):** Enviar tráfico directo mediante enlaces de `tradedoubler.com` impresos en el HTML provocará que el 40% de los usuarios con AdBlockers/Brave Browser no puedan comprar. Requiere la construcción urgente de un "Cloaker" interno (`/out/slug`).
6.  **Deuda Técnica (UX del Catálogo):** Actualmente, si 3 tiendas venden un bote idéntico, aparecen 3 botes repetidos en la web. La UX no escalará. Se necesita acometer pronto la arquitectura Multi-tienda V2 (1 Producto -> N Ofertas).
7.  **Comunidad y Retención Brillantes:** La arquitectura de "El IG de los Suplementos" (Perfiles, Seguidores, Stacks compartibles y Check-ins) dota al comparador de una retención (LTV) atípica en el sector de afiliación.
8.  **Métricas Ciegas para Marketing:** El sistema sabe qué productos son populares gracias a clics internos, pero no tiene configurados los disparadores nativos (eventos personalizados) hacia Google Analytics 4, imposibilitando auditar el ROI del tráfico externo.
9.  **Filtro Antimonopolio Efectivo:** La idea de exigir mayores descuentos a categorías basura para que un producto merezca llamarse "Chollo" protege la confianza del usuario y la legitimidad del canal de Telegram.
10. **Listo para V1, Lejos para V2:** El proyecto puede empezar a facturar mañana mismo con unos ligeros retoques SEO y de seguridad. Sin embargo, escalar a >50.000 productos y >10 tiendas exigirá refactorizar el sistema de paginación de BBDD y montar Colas de Scraping Asíncronas (Celery).
