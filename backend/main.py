from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException  # <-- Añade HTTPException

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
    categoria: Optional[str] = None,
    marca: Optional[str] = None,
    objetivo: Optional[str] = None,
    sabor: Optional[str] = None,
    orden_precio: Optional[str] = None,
    # --- NUEVO: Parámetro para buscar texto ---
    busqueda: Optional[str] = None,
    # ----------------------------------------
    db: Session = Depends(get_db)
):
    query = db.query(models.Producto)
    
    # 1. Filtros exactos
    if categoria:
        query = query.join(models.Categoria).filter(models.Categoria.nombre == categoria)
    if marca:
        query = query.join(models.Marca).filter(models.Marca.nombre == marca)
    if objetivo:
        query = query.filter(models.Producto.objetivo == objetivo)
    if sabor:
        query = query.filter(models.Producto.sabor == sabor)
        
    # 2. BUSCADOR DE TEXTO LIBRE (¡NUEVO!)
    if busqueda:
        # Los '%' significan que el texto puede estar en cualquier parte de la frase
        termino = f"%{busqueda}%"
        query = query.filter(
            or_(
                models.Producto.nombre.ilike(termino),
                models.Producto.descripcion.ilike(termino)
            )
        )
        
    # 3. Lógica de ordenación
    if orden_precio == "asc":
        query = query.order_by(models.Producto.precio.asc())
    elif orden_precio == "desc":
        query = query.order_by(models.Producto.precio.desc())
        
    # 4. Ejecutar búsqueda
    productos = query.offset(skip).limit(limit).all()
    return productos


@app.get("/api/categorias", response_model=List[schemas.CategoriaResponse])
def obtener_categorias(db: Session = Depends(get_db)):
    # Vamos a la base de datos y le pedimos todas las categorías
    categorias = db.query(models.Categoria).all()
    return categorias

# --- RUTA DE PRODUCTO INDIVIDUAL (FICHA DE PRODUCTO) ---
@app.get("/api/productos/{producto_id}", response_model=schemas.ProductoResponse)
def obtener_producto_individual(producto_id: int, db: Session = Depends(get_db)):
    """
    Busca un único producto por su ID. 
    Ideal para que el frontend dibuje la página de detalles del producto.
    """
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    
    # Si el producto no existe en la base de datos, devolvemos un error 404
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    return producto