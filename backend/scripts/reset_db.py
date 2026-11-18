import os
import sys

# Aseguramos que la raíz del backend esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from security_guards import validate_destructive_script_execution
import models

# BLINDAJE DE SEGURIDAD: Prohibido ejecutar en Neon o producción.
# Solo permitido en PostgreSQL local de pruebas (*_test) con flag explícito.
validate_destructive_script_execution(
    engine=engine,
    script_name="reset_db.py",
    flag_name="ALLOW_DESTRUCTIVE_RESET",
    allow_non_test=False,
)

print(f"⚠️  Borrando tablas en base de datos local de test ({engine.url.database})...")
models.Base.metadata.drop_all(bind=engine)

print("🏗️  Creando las tablas desde cero...")
models.Base.metadata.create_all(bind=engine)

print("✅  ¡Base de datos de pruebas reseteada! Está vacía y lista para llenarse.")
