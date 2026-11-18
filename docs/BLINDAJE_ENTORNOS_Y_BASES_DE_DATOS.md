# Blindaje de Entornos, Bases de Datos y Scripts de Mantenimiento (PR P0)

Este documento describe la arquitectura de seguridad implementada para garantizar el aislamiento estricto de las bases de datos en **Tus Suplementos**, impidiendo que cualquier prueba, benchmark o script de mantenimiento afecte a bases de datos de desarrollo o producción.

---

## 1. Mapa de Entornos y Bases de Datos

El proyecto cuenta con tres entornos claramente diferenciados:

| Entorno | Ubicación | Base de Datos | Variable de Configuración | Operaciones Permitidas |
| :--- | :--- | :--- | :--- | :--- |
| **Producción** | Neon (`production`) | `neondb` | Inyectada en Render y GitHub Actions | Consultas públicas de la API y jobs autorizados de CI/CD. **Prohibido ejecutar tests, benchmarks o scripts de mantenimiento.** |
| **Desarrollo Local** | Neon (`desarrollo-local-javi`) | `neondb` | `backend/.env` (`DATABASE_URL`) | Desarrollo interactivo del backend local. **Prohibido ejecutar tests, benchmarks o scripts de mantenimiento.** |
| **Testing / Mantenimiento** | PostgreSQL Local (`127.0.0.1:54329`) | `tus_suplementos_test` | `TEST_DATABASE_URL` | **Único entorno autorizado** para `pytest`, benchmarks, `seed_data`, reseteos y scripts de mantenimiento. |

---

## 2. Componentes de Blindaje Implementados

### 2.1 Módulo Central: `backend/security_guards.py`
Proporciona validaciones deterministas e independientes:
- **`validate_test_database_url(url)`**:
  - Verifica que la URL no esté vacía.
  - Rechaza cualquier host remoto o que contenga `neon.tech` / `neon`.
  - Exige que el host sea local (`localhost`, `127.0.0.1`, `::1`).
  - Exige que el nombre de la base de datos termine estrictamente en `_test`.
- **`enforce_local_test_environment(script_name, flag_name)`**:
  - **Guardia previo a la importación**: se ejecuta antes de importar `database.py` o los modelos.
  - Exige que `TEST_DATABASE_URL` apunte a una base local `*_test` y que el flag de autorización esté activo.
  - Impide que se ejecute cualquier sentencia DDL o ajuste de secuencias (`setval`) contra bases remotas durante la importación.
- **`get_active_database_url()`**:
  - Si el proceso detecta modo de testing (`TESTING=1`, `ENV=test`, `pytest`, o `TEST_DATABASE_URL` presente), **exige** que `TEST_DATABASE_URL` esté definido y sea válido.
  - Aborta inmediatamente si falta `TEST_DATABASE_URL`, impidiendo que `database.py` recurra accidentalmente al `.env` de desarrollo.
- **`validate_engine_for_testing(engine, check_destructive_flag, flag_name)`**:
  - Inspecciona el objeto SQLAlchemy `Engine` activo.
  - Verifica que su conexión física real apunte a un host local y a una base `*_test`.
  - Exige la variable de autorización explícita para operaciones destructivas.

### 2.2 Conexión en `backend/database.py`
- Emplea `get_active_database_url()` al inicializarse.
- Muestra en consola el destino de la conexión con credenciales enmascaradas (`hide_password=True`) y la etiqueta de modo (`TESTING LOCAL` vs `DESARROLLO / PRODUCCIÓN`).
- En `ensure_schema_compatibility()`, comprueba y añade la extensión `pg_trgm` de forma idempotente (`CREATE EXTENSION IF NOT EXISTS pg_trgm`), asegurando que cualquier base de datos nueva disponga de la capacidad para funciones de similitud trigram.

### 2.3 Diagnóstico de Solo Lectura: `backend/scripts/ping_bd.py`
- Herramienta 100% de solo lectura que **no importa `database.py`**.
- Realiza únicamente `SELECT 1` y conteos de tablas públicas, garantizando cero mutaciones, cero DDL y cero alteraciones de secuencias.

---

## 3. Inventario y Control de Scripts Conservados

Todos los scripts de mantenimiento y reseteo están restringidos **estrictamente a PostgreSQL local de pruebas (`*_test`)**. Ningún flag permite su ejecución contra Neon dev o production en esta fase.

| Script | Propósito | Entorno Permitido | Pre-requisito / Flag Requerido |
| :--- | :--- | :--- | :--- |
| `backend/scripts/orquestador.py` | Pipeline multi-tienda y alertas | GitHub Actions (`cron_precios.yml`) | Automatizado en CI/CD con secrets de producción |
| `backend/scripts/reset_cooldown.py` | Reseteo semanal de cooldown de alertas | GitHub Actions (`cron_precios.yml`) | Automatizado en CI/CD con secrets de producción |
| `backend/scripts/ping_bd.py` | Diagnóstico de conectividad (SELECT 1) | Local / CLI manual | 100% Solo lectura (sin DDL ni setval) |
| `backend/scripts/reset_db.py` | Reseteo de esquema desde cero | **Exclusivamente local `*_test`** | `ALLOW_DESTRUCTIVE_RESET=true` |
| `backend/scripts/fusionar_duplicados.py` | Fusión relacional de clones | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_FUSION=true` |
| `backend/scripts/limpiar_historicos_duplicados.py` | Sanitización de histórico de precios | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_PURGE_HISTORICOS=true` (con `--execute`) |
| `backend/scripts/limpiar_suscriptor.py` | Supresión de email por baja / RGPD | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR=true` |
| `backend/scripts/reprocesar_nlp.py` | Re-etiquetado NLP retroactivo | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_REPROCESAR_NLP=true` |

> [!CAUTION]
> **Operaciones Remotas Prohibidas:** Los scripts de mantenimiento conservados no admiten ejecución contra bases remotas ni ramas de Neon. Si se intenta ejecutar sin una base local `*_test`, abortan inmediatamente antes de importar módulos de conexión.

---

## 4. Guía de Ejecución para Desarrolladores

### 4.1 Ejecutar Tests Unitarios (Pytest)
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python -m pytest backend/tests -v
```

### 4.2 Ejecutar Benchmark de Rendimiento
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python backend/tests/run_benchmark.py
```

### 4.3 Ejecutar Diagnóstico de Conectividad (Solo Lectura)
```powershell
# En Windows PowerShell (prueba la BD activa en .env o TEST_DATABASE_URL)
python backend/scripts/ping_bd.py
```

### 4.4 Ejecutar Reseteo de Base de Datos Local de Pruebas
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_DESTRUCTIVE_RESET = "true"
python backend/scripts/reset_db.py
```

### 4.5 Ejecutar Scripts de Mantenimiento en Base Local de Pruebas
Todos los scripts de mantenimiento exigen `TEST_DATABASE_URL` y su flag específico:

```powershell
# Fusión de duplicados:
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_FUSION = "true"
python backend/scripts/fusionar_duplicados.py

# Purga de históricos duplicados (dry-run):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python backend/scripts/limpiar_historicos_duplicados.py --dry-run

# Purga de históricos duplicados (ejecución real):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_PURGE_HISTORICOS = "true"
python backend/scripts/limpiar_historicos_duplicados.py --execute

# Re-procesamiento NLP:
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_REPROCESAR_NLP = "true"
python backend/scripts/reprocesar_nlp.py

# Supresión de suscriptor RGPD:
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR = "true"
python backend/scripts/limpiar_suscriptor.py "usuario@ejemplo.com"
```
