from database import engine, SessionLocal
from sqlalchemy import MetaData
import models

print("Reflejando esquema de la base de datos actual...")
meta = MetaData()
meta.reflect(bind=engine)

print("Destruyendo todas las tablas (incluso las que no están en el código)...")
meta.drop_all(bind=engine)
print("Tablas destruidas.")

print("Recreando esquema monolítico original...")
models.Base.metadata.create_all(bind=engine)
print("Base de datos recreada.")
