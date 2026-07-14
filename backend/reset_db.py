from database import engine
import models

print("Destruyendo las tablas antiguas...")
models.Base.metadata.drop_all(bind=engine)

print("Creando las tablas con el nuevo diseño (sabor, formato, JSON, objetivo)...")
models.Base.metadata.create_all(bind=engine)

print("✅ Base de datos reseteada con éxito. ¡Lista para los nuevos filtros!")