from database import engine
import models

print("⚠️  Borrando absolutamente todas las tablas en Neon...")
models.Base.metadata.drop_all(bind=engine)

print("🏗️  Creando las tablas desde cero con la estructura perfecta...")
models.Base.metadata.create_all(bind=engine)

print("✅  ¡Base de datos reseteada! Está vacía y lista para llenarse.")