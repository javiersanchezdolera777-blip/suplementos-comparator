from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

# Importamos nuestras piezas
import models
import schemas
from database import engine, SessionLocal

# Orden de construcción (ya la conoces)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Suplementos")

# Nuestro carrito de la compra (ya lo conoces)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NUEVOS ENDPOINTS OFICIALES ---

@app.get("/api/productos", response_model=List[schemas.ProductoResponse])
def obtener_productos(db: Session = Depends(get_db)):
    # Vamos a la base de datos y le pedimos todos los productos
    productos = db.query(models.Producto).all()
    return productos

@app.get("/api/categorias", response_model=List[schemas.CategoriaResponse])
def obtener_categorias(db: Session = Depends(get_db)):
    # Vamos a la base de datos y le pedimos todas las categorías
    categorias = db.query(models.Categoria).all()
    return categorias