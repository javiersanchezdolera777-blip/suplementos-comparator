import models
from database import engine

print("Iniciando operación quirúrgica en la Base de Datos...")

# 1. Borramos SOLO la tabla de productos (los favoritos que dependan de ellos se borrarán en cascada gracias a nuestro ondelete="CASCADE")
models.Producto.__table__.drop(engine, checkfirst=True)

# 2. Recreamos la tabla de productos (ahora se creará con las nuevas columnas)
models.Base.metadata.create_all(bind=engine)

print("✅ Tabla de productos actualizada con los nuevos sub-filtros. ¡Usuarios a salvo!")