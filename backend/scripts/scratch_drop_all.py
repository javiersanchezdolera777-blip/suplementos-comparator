import os
import sys

# Aseguramos que la raíz del backend esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from security_guards import validate_destructive_script_execution
from sqlalchemy import MetaData
import models

# BLINDAJE DE SEGURIDAD: Solo se permite ejecutar en base de datos local de test
# y con flag de autorización explícita.
validate_destructive_script_execution(
    engine=engine,
    script_name="scratch_drop_all.py",
    flag_name="ALLOW_DESTRUCTIVE_SCRATCH",
    allow_non_test=False,
)

print(f"Reflejando esquema de la base de datos ({engine.url.database})...")
meta = MetaData()
meta.reflect(bind=engine)

print("Destruyendo todas las tablas...")
meta.drop_all(bind=engine)
print("Tablas destruidas.")

print("Recreando esquema monolítico original...")
models.Base.metadata.create_all(bind=engine)
print("Base de datos recreada con éxito.")
