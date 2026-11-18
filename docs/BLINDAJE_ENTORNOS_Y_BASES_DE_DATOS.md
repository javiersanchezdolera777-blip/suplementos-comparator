# Blindaje de Entornos, Bases de Datos y Scripts Destructivos (PR P0)

Este documento describe la arquitectura de seguridad implementada para garantizar el aislamiento estricto de las bases de datos en **Tus Suplementos**, impidiendo que cualquier prueba, benchmark o script de mantenimiento afecte accidentalmente a bases de datos de desarrollo o producción.

---

## 1. Mapa de Entornos y Bases de Datos

El proyecto cuenta con tres entornos claramente diferenciados:

| Entorno | Ubicación | Base de Datos | Variable de Configuración | Operaciones Permitidas |
| :--- | :--- | :--- | :--- | :--- |
| **Producción** | Neon (`production`) | `neondb` | Inyectada en Render y GitHub Actions | Exclusivamente consultas de la API pública y jobs autorizados de producción. **Nunca tests ni benchmarks.** |
| **Desarrollo Local** | Neon (`desarrollo-local-javi`) | `neondb` | `backend/.env` (`DATABASE_URL`) | Desarrollo del backend, pruebas de APIs en servidor local. **Nunca tests ni benchmarks destructivos.** |
| **Testing / Benchmarks** | PostgreSQL Local (`127.0.0.1:54329`) | `tus_suplementos_test` | `TEST_DATABASE_URL` | Ejecución de tests (`pytest`), benchmarks de rendimiento, creación de datasets sintéticos y `TRUNCATE CASCADE`. |

---

## 2. Componentes de Blindaje Implementados

### 2.1 Módulo Central: `backend/security_guards.py`
Proporciona validaciones deterministas e independientes de la plataforma:
- **`validate_test_database_url(url)`**:
  - Verifica que la URL no esté vacía.
  - Rechaza cualquier host remoto o que contenga `neon.tech` / `neon`.
  - Exige que el host sea local (`localhost`, `127.0.0.1`, `::1`).
  - Exige que la base de datos termine estrictamente en `_test`.
- **`get_active_database_url()`**:
  - Si el proceso detecta modo de testing (`TESTING=1`, `ENV=test`, `pytest`, o `TEST_DATABASE_URL` presente), **exige** que `TEST_DATABASE_URL` esté definido y sea válido.
  - Aborta inmediatamente si falta `TEST_DATABASE_URL`, impidiendo que `database.py` recurra accidentalmente al `.env` de desarrollo.
- **`validate_engine_for_testing(engine, check_destructive_flag, flag_name)`**:
  - Inspecciona el objeto SQLAlchemy `Engine` activo.
  - Verifica que su conexión física real apunte a un host local y a una base `*_test`.
  - Opcionalmente exige una variable de entorno de autorización (ej. `ALLOW_DESTRUCTIVE_TEST_DB=true`).
- **`validate_destructive_script_execution(engine, script_name, flag_name, allow_non_test)`**:
  - Si `allow_non_test=False`: prohíbe terminantemente la ejecución fuera de una base local `*_test` y exige el flag.
  - Si `allow_non_test=True`: permite la ejecución en bases de datos autorizadas de mantenimiento solo tras comprobar que el usuario ha exportado el flag correspondiente de forma consciente.

### 2.2 Conexión en `backend/database.py`
- Emplea `get_active_database_url()` al inicializarse.
- Muestra en consola el destino de la conexión con credenciales enmascaradas (`hide_password=True`) y la etiqueta de modo (`TESTING LOCAL` vs `DESARROLLO / PRODUCCIÓN`).

### 2.3 Blindaje en Pruebas (`backend/tests/conftest.py`)
- Fija `os.environ["TESTING"] = "1"` y `os.environ["ALLOW_DESTRUCTIVE_TEST_DB"] = "true"`.
- Valida `TEST_DATABASE_URL` con `validate_test_database_url()`.
- Tras importar `main`, ejecuta una doble validación sobre `main.engine` antes de permitir cualquier fixture o petición.

### 2.4 Generador Sintético (`backend/tests/seed_data.py`)
- La función `seed(engine, ...)` ahora valida el engine recibido antes de ejecutar cualquier sentencia SQL.
- Si el engine no es local o no termina en `_test`, o si falta `ALLOW_DESTRUCTIVE_TEST_DB=true`, aborta inmediatamente con `RuntimeError` antes de `TRUNCATE CASCADE`.

### 2.5 Benchmark Aislado (`backend/tests/run_benchmark.py`)
- Configura las protecciones antes de importar `main`, `seed_data` o los modelos.
- Requiere `TEST_DATABASE_URL`. Si no existe, imprime un mensaje de error explicativo y sale con código 2 sin cargar la aplicación ni conectarse a bases remotas.
- Valida `main.engine` tras la importación.

---

## 3. Inventario y Control de Scripts Destructivos

Todos los scripts con potencial destructivo o de modificación masiva cuentan ahora con guardias automáticos:

| Script | Riesgo Original | Nivel de Restricción | Flag Requerido |
| :--- | :--- | :--- | :--- |
| `backend/scripts/scratch_drop_all.py` | `meta.drop_all()` destructivo total | **Solo base de datos local `*_test`** | `ALLOW_DESTRUCTIVE_SCRATCH=true` |
| `backend/scripts/reset_db.py` | `models.Base.metadata.drop_all()` | **Solo base de datos local `*_test`** | `ALLOW_DESTRUCTIVE_RESET=true` |
| `backend/scripts/fusionar_duplicados.py` | Fusión y borrado de clones de productos | Mantenimiento asistido | `ALLOW_MAINTENANCE_FUSION=true` |
| `backend/scripts/limpiar_historicos_duplicados.py` | Purga masiva en `precios_historicos` | Mantenimiento asistido (con `--execute`) | `ALLOW_MAINTENANCE_PURGE_HISTORICOS=true` |
| `backend/scripts/limpiar_suscriptor.py` | Borrado de usuarios/suscriptores por email | Mantenimiento asistido | `ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR=true` |
| `backend/scripts/limpiar_basura.py` | Borrado de productos sin enlace o imagen | Mantenimiento asistido | `ALLOW_MAINTENANCE_PURGE_BASURA=true` |

---

## 4. Guía de Uso Seguro para Desarrolladores

### Para ejecutar los tests unitarios:
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python -m pytest backend/tests -v
```

### Para ejecutar el benchmark comparativo:
```powershell
# En Windows PowerShell
$env:TEST_DATABASE_URL = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
python backend/tests/run_benchmark.py
```

### Para ejecutar un script de mantenimiento en caso necesario:
```powershell
# El script indicará qué base de datos y host se verán afectados y exigirá el flag:
$env:ALLOW_MAINTENANCE_PURGE_HISTORICOS = "true"
python backend/scripts/limpiar_historicos_duplicados.py --execute
```
