from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Importamos nuestras piezas
import models
import schemas
from database import engine, SessionLocal

# Orden de construcción
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Suplementos")

# --- CONFIGURACIÓN DE CORS ---
# Ponemos "*" para que Vercel (el frontend de Javiki) no tenga bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nuestro carrito de la compra (ya lo conoces)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NUEVA RUTA: DICCIONARIO DE FILTROS ---
@app.get("/api/config/filtros")
def obtener_filtros():
    """
    Esta ruta le dice al Frontend (Next.js) qué botones de filtro tiene que dibujar.
    Saca los valores directamente de nuestro diccionario de schemas.py.
    """
    return {
        "sabores": [sabor.value for sabor in schemas.SaborEnum],
        "formatos": [formato.value for formato in schemas.FormatoEnum],
        "objetivos": [objetivo.value for objetivo in schemas.ObjetivoEnum]
    }


# --- RUTAS DE DATOS ---
@app.get("/api/productos", response_model=List[schemas.ProductoResponse])
def obtener_productos(
    skip: int = 0, 
    limit: int = 100, 
    # --- Parámetros de búsqueda opcionales ---
    categoria: Optional[str] = None,
    marca: Optional[str] = None,
    objetivo: Optional[str] = None,
    sabor: Optional[str] = None,
    # ----------------------------------------
    db: Session = Depends(get_db)
):
    # 1. Preparamos una búsqueda de TODOS los productos
    query = db.query(models.Producto)
    
    # 2. Si Javiki nos pide algo específico, reducimos la lista
    if categoria:
        query = query.join(models.Categoria).filter(models.Categoria.nombre == categoria)
    if marca:
        query = query.join(models.Marca).filter(models.Marca.nombre == marca)
    if objetivo:
        query = query.filter(models.Producto.objetivo == objetivo)
    if sabor:
        query = query.filter(models.Producto.sabor == sabor)
        
    # 3. Ejecutamos la búsqueda final y devolvemos los productos
    productos = query.offset(skip).limit(limit).all()
    return productos


@app.get("/api/categorias", response_model=List[schemas.CategoriaResponse])
def obtener_categorias(db: Session = Depends(get_db)):
    # Vamos a la base de datos y le pedimos todas las categorías
    categorias = db.query(models.Categoria).all()
    return categorias