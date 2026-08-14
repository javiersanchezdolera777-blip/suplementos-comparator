# Estado Actual del Proyecto

## Dominio y Entorno Operativo
*   **Dominio Oficial Activo:** [https://tussuplementos.es](https://tussuplementos.es)
*   **Backend URL:** Desplegado en Render (o similar configurado).
*   **Frontend URL:** Desplegado en Vercel.

## Estado de la Base de Datos
*   **Motor:** PostgreSQL (Neon DB).
*   **Catálogo Actual:** HSN completamente integrado.
*   **Volumen:** Más de 800 productos clasificados e ingestados correctamente.
*   **Limpieza:** Las marcas huérfanas de pruebas anteriores han sido purgadas de la tabla maestra de `marcas`. La normalización agrupa todas las gamas de HSN bajo el paraguas de HSN y aísla las marcas externas reales (ej. *NOW Foods*, *Swanson*).

## Tareas Completadas (Checklist Reciente)
- [x] Refactorización masiva del `utils.py` (Cerebro NLP de catalogación).
- [x] Actualización del bloque de extracción de precios y marcas dinámicas en `hsn.py` (JSON-LD prioritario y Fallback HTML).
- [x] Configuración estricta de borrado y reinicio (`tienda == "HSN"`) en el script de ingestión.
- [x] Resolución de colisiones NLP graves ("espiNACa", "Colágeno Hidrolizado" vs "Proteínas").
- [x] Purgado de marcas huérfanas y filtro en `GET /api/marcas` para no mostrar marcas con stock nulo.
- [x] Despliegue de los cambios críticos a la rama `main` en GitHub (Pull Request #59).

## Tareas Pendientes Inmediatas (Next Steps)
- [ ] Ejecutar ingestores pendientes para MyProtein y Prozis.
- [ ] Implementar el rediseño del UI/UX en el frontend (Mejoras visuales y Dark Mode).
- [ ] Añadir filtro funcional de "Alérgenos" (Gluten/Lactosa).
