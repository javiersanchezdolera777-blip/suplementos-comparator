import os
import sys

# Aseguramos que la raíz del backend esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BLINDAJE DE SEGURIDAD PRE-IMPORTACIÓN:
# La validación se ejecuta ANTES de importar database.py para impedir cualquier
# efecto secundario DDL o setval() en bases de datos remotas.
from security_guards import enforce_local_test_environment, validate_destructive_script_execution

enforce_local_test_environment("reset_db.py", "ALLOW_DESTRUCTIVE_RESET")

from database import engine
import models

validate_destructive_script_execution(
    engine=engine,
    script_name="reset_db.py",
    flag_name="ALLOW_DESTRUCTIVE_RESET",
)

print(f"⚠️  Borrando tablas en base de datos local de test ({engine.url.database})...")
models.Base.metadata.drop_all(bind=engine)

print("🏗️  Creando las tablas desde cero...")
models.Base.metadata.create_all(bind=engine)

print("✅  ¡Base de datos de pruebas reseteada! Está vacía y lista para llenarse.")
