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
  - Exige exclusivamente el driver PostgreSQL (`postgresql://` o `postgresql+...`). Rechaza `sqlite`, `mysql`, etc.
  - Exige un hostname explícito de loopback (`localhost`, `127.0.0.1` o `::1`). Rechaza hostname vacío o nulo.
  - Rechaza cualquier host remoto o referencias a `neon.tech` / `neon`.
  - Rechaza cualquier parámetro en la query URL que pueda desviar la conexión física (`host`, `hostaddr`, `service`).
  - Exige que el nombre de la base de datos termine estrictamente en `_test`.
- **`enforce_local_test_environment(script_name, flag_name)`**:
  - **Guardia previo a la importación**: se ejecuta antes de importar `database.py` o los modelos.
  - Exige que `TEST_DATABASE_URL` apunte a una base local `*_test` y que el flag de autorización esté activo.
  - Impide que se ejecute cualquier sentencia DDL o ajuste de secuencias (`setval`) contra bases remotas durante la importación.
- **`validate_engine_for_testing(engine, check_destructive_flag, flag_name)`**:
  - Inspecciona el objeto SQLAlchemy `Engine` activo.
  - Exige que `engine.dialect.name == "postgresql"`.
  - Verifica que su conexión física real apunte a un hostname local explícito y a una base `*_test`.
  - Verifica que la query del engine no contenga parámetros de redirección (`host`, `hostaddr`, `service`).
  - Exige la variable de autorización explícita para operaciones destructivas.

### 2.2 Conexión en `backend/database.py`
- Emplea `get_active_database_url()` al inicializarse.
- Muestra en consola el destino de la conexión con credenciales enmascaradas (`hide_password=True`) y la etiqueta de modo (`TESTING LOCAL` vs `DESARROLLO / PRODUCCIÓN`).
- **Retirada de `CREATE EXTENSION pg_trgm` del arranque**: Se eliminó la creación dinámica de la extensión `pg_trgm` en tiempo de importación/arranque de la aplicación.
- **Gestión de extensiones vía Alembic**: La creación de `pg_trgm` queda formalmente encomendada a las migraciones versionadas de Alembic (`backend/alembic/versions/e1b2c3d4e5f6_add_pg_trgm_extension.py`).
- **Deuda técnica delimitada (`ensure_schema_compatibility`)**: Se constata que `database.py` todavía ejecuta `ensure_schema_compatibility()`, la cual conserva comprobaciones y operaciones de `ALTER TABLE` (columnas faltantes) y sincronización de secuencias (`setval`). Su retirada definitiva o migración íntegra hacia Alembic queda catalogada como una deuda técnica independiente para no ampliar de forma no controlada el alcance de este PR.

### 2.3 Diagnóstico Unívoco de Solo Lectura: `backend/scripts/ping_bd.py`
- Herramienta 100% de solo lectura que **no importa `database.py`** (evitando así cualquier ejecución de `ensure_schema_compatibility`).
- Selección determinista estricta mediante `argparse`: grupo mutuamente excluyente y obligatorio con `--test` (valida y conecta a `TEST_DATABASE_URL`) y `--dev` (conecta a `DATABASE_URL`).
- Rechaza argumentos desconocidos, rechaza la ausencia de ambos y rechaza la presencia simultánea de ambos. No existe ningún fallback automático.
- Realiza únicamente `SELECT 1` y conteos de tablas públicas, garantizando cero mutaciones, cero DDL y cero alteraciones de secuencias.

---

## 3. Inventario y Clarificación de Herramientas Conservadas

Todos los scripts de mantenimiento y reseteo están restringidos **estrictamente a PostgreSQL local de pruebas (`*_test`)**. Ningún flag permite su ejecución contra Neon dev o production en esta fase.

| Script | Propósito y Naturaleza | Entorno Permitido | Pre-requisito / Flag Requerido |
| :--- | :--- | :--- | :--- |
| `backend/scripts/orquestador.py` | Pipeline multi-tienda y alertas | GitHub Actions (`cron_precios.yml`) | Automatizado en CI/CD con secrets de producción |
| `backend/scripts/reset_cooldown.py` | Reseteo semanal de cooldown de alertas | GitHub Actions (`cron_precios.yml`) | Automatizado en CI/CD con secrets de producción |
| `backend/scripts/ping_bd.py` | Diagnóstico de conectividad (SELECT 1) | Local / CLI manual (`--test` o `--dev`) | 100% Solo lectura (sin DDL ni setval) |
| `backend/scripts/reset_db.py` | Reseteo de esquema desde cero en pruebas | **Exclusivamente local `*_test`** | `ALLOW_DESTRUCTIVE_RESET=true` |
| `backend/scripts/fusionar_duplicados.py` | **Utilidad legacy por coincidencia de slug** (NO es el motor de matching de la futura arquitectura) | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_FUSION=true` |
| `backend/scripts/limpiar_historicos_duplicados.py` | Sanitización de redundancias en históricos | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_PURGE_HISTORICOS=true` (con `--execute`) |
| `backend/scripts/limpiar_suscriptor.py` | **Herramienta restringida a testing** (NO es el mecanismo operativo de supresión RGPD en producción) | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR=true` |
| `backend/scripts/reprocesar_nlp.py` | **Herramienta de experimentación local** (NO debe utilizarse sobre producción hasta resolver la semántica de atributos) | **Exclusivamente local `*_test`** | `ALLOW_MAINTENANCE_REPROCESAR_NLP=true` |

> [!CAUTION]
> **Prohibición Total de Operaciones Remotas:** Los scripts de mantenimiento conservados no admiten ejecución contra bases remotas ni ramas de Neon. Si se intenta ejecutar sin una base local `*_test`, abortan antes de importar módulos de conexión.

---

## 4. Guía de Ejecución para Desarrolladores

### 4.1 Ejecutar Tests Unitarios (Pytest)
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python -m pytest backend/tests -v
```

### 4.2 Ejecutar Benchmark de Rendimiento (Paginación y Anti-OOM)
Para ejecutar el benchmark comparativo con regeneración de datos sintéticos, se requieren ambas variables de entorno:
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_DESTRUCTIVE_TEST_DB = "true"
python backend/tests/run_benchmark.py
```

### 4.3 Diagnóstico de Conectividad (Solo Lectura)
Requiere indicar el flag unívoco del entorno que se desea comprobar:
```powershell
# Para diagnosticar la base local de pruebas (TEST_DATABASE_URL):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python backend/scripts/ping_bd.py --test

# Para diagnosticar la base de desarrollo (DATABASE_URL de backend/.env):
python backend/scripts/ping_bd.py --dev
```

### 4.4 Reseteo de Esquema Local de Pruebas
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_DESTRUCTIVE_RESET = "true"
python backend/scripts/reset_db.py
```

### 4.5 Ejecución de Herramientas de Mantenimiento en Base Local de Pruebas
Todos los scripts exigen `TEST_DATABASE_URL` y su flag específico:

```powershell
# Fusión de duplicados (legacy por slug):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_FUSION = "true"
python backend/scripts/fusionar_duplicados.py

# Purga de históricos duplicados (simulación dry-run):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python backend/scripts/limpiar_historicos_duplicados.py --dry-run

# Purga de históricos duplicados (ejecución real en base local):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_PURGE_HISTORICOS = "true"
python backend/scripts/limpiar_historicos_duplicados.py --execute

# Re-procesamiento NLP (experimentación local):
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_REPROCESAR_NLP = "true"
python backend/scripts/reprocesar_nlp.py

# Limpieza de suscriptor en testing:
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
$env:ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR = "true"
python backend/scripts/limpiar_suscriptor.py "test_user@example.com"
```
