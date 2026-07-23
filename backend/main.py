from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

# Importamos nuestras piezas
import models
import schemas
from database import engine, SessionLocal
import security

# Orden de construcción
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Suplementos")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINT ULTRALIGERO PARA KEEP-ALIVE ---
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "suparator-api"
    }


# --- RUTA: DICCIONARIO DE FILTROS COMPLETOS ---
@app.get("/api/config/filtros")
def obtener_filtros(db: Session = Depends(get_db)):
    marcas_db = db.query(models.Marca).all()
    categorias_db = db.query(models.Categoria).all()
    
    return {
        "brands": [m.nombre for m in marcas_db],
        "categories": [c.nombre for c in categorias_db],
        "flavors": [sabor.value for sabor in schemas.SaborEnum],
        "formats": [formato.value for formato in schemas.FormatoEnum],
        "goals": [objetivo.value for objetivo in schemas.ObjetivoEnum],
        "quality_seals": [sello.value for sello in schemas.SelloCalidadEnum],
        "protein_types": [tipo.value for tipo in schemas.TipoProteinaEnum],
        "creatine_types": [tipo.value for tipo in schemas.TipoCreatinaEnum],
        "amino_profiles": [perfil.value for perfil in schemas.PerfilAminoacidosEnum],
        "vitamin_types": [tipo.value for tipo in schemas.TipoVitaminaEnum]
    }

# --- RUTA PRINCIPAL DE PRODUCTOS ---
@app.get("/api/productos", response_model=schemas.PaginatedProducts)
def obtener_productos(
    skip: int = 0, 
    limit: int = 100, 
    categoria: Optional[str] = None,
    marca: Optional[str] = None,
    objetivo: Optional[str] = None,
    sabor: Optional[str] = None,
    formato: Optional[str] = None,
    es_vegano: Optional[bool] = None,
    sello_calidad: Optional[str] = None,
    tipo_proteina: Optional[str] = None,
    tipo_creatina: Optional[str] = None,
    perfil_aminoacidos: Optional[str] = None,
    tipo_vitamina: Optional[str] = None,
    orden_precio: Optional[str] = None,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Producto)
    
    # 1. Filtro de Categoría (El parche de "todos" por si Javiki lo manda en la URL)
    if categoria and categoria.lower() != "todos":
        if categoria.isdigit():
            query = query.filter(models.Producto.categoria_id == int(categoria))
        else:
            query = query.join(models.Categoria).filter(models.Categoria.nombre.ilike(f"%{categoria}%"))
    # 2. Filtro de Marca
    if marca:
        query = query.join(models.Marca).filter(models.Marca.nombre.ilike(f"%{marca}%"))
        
    # 3. Filtros Básicos
    if objetivo:
        query = query.filter(models.Producto.objetivo == objetivo)
    if formato:
        query = query.filter(models.Producto.formato == formato)
    if es_vegano is not None:
        query = query.filter(models.Producto.es_vegano == es_vegano)
    if sello_calidad:
        query = query.filter(models.Producto.sello_calidad == sello_calidad)
        
    # 4. Sub-filtros
    if tipo_proteina:
        query = query.filter(models.Producto.tipo_proteina == tipo_proteina)
    if tipo_creatina:
        query = query.filter(models.Producto.tipo_creatina == tipo_creatina)
    if perfil_aminoacidos:
        query = query.filter(models.Producto.perfil_aminoacidos == perfil_aminoacidos)
    if tipo_vitamina:
        query = query.filter(models.Producto.tipo_vitamina == tipo_vitamina)
        
    # 5. Buscador de texto libre
    if busqueda:
        termino = f"%{busqueda}%"
        query = query.filter(
            or_(
                models.Producto.nombre.ilike(termino),
                models.Producto.descripcion.ilike(termino)
            )
        )
        
    # 6. Ordenación
    if orden_precio == "asc":
        query = query.order_by(models.Producto.precio.asc())
    elif orden_precio == "desc":
        query = query.order_by(models.Producto.precio.desc())

    # 7. Filtrado seguro por Sabor (Soporta Array o String) y Paginación
    productos_raw = query.all()

    if sabor:
        sabor_lower = sabor.lower()
        def tiene_sabor(producto):
            valor = getattr(producto, "sabor", None)
            if isinstance(valor, list):
                return any(str(item).lower() == sabor_lower for item in valor)
            if isinstance(valor, str):
                return sabor_lower in valor.lower()
            return False

        productos_filtrados = [p for p in productos_raw if tiene_sabor(p)]
    else:
        productos_filtrados = productos_raw

    total_resultados = len(productos_filtrados)
    productos = productos_filtrados[skip:skip + limit]
    
    return {
        "total_resultados": total_resultados,
        "productos": productos
    }

# --- RUTA DE PRODUCTO INDIVIDUAL ---
@app.get("/api/productos/{producto_id}", response_model=schemas.ProductResponse)
def obtener_producto_individual(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


# ==========================================
# --- RUTAS DE AUTENTICACIÓN Y USUARIOS ---
# ==========================================

@app.post("/api/registro", response_model=schemas.UsuarioResponse)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este email ya está registrado")
        
    password_cifrada = security.obtener_password_hash(usuario.password)
    nuevo_usuario = models.Usuario(email=usuario.email, hashed_password=password_cifrada)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/api/login", response_model=schemas.Token)
def iniciar_sesion(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    user_db = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if not user_db or not security.verificar_password(usuario.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
        
    access_token = security.crear_token_acceso(data={"sub": user_db.email})
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credenciales_exception = HTTPException(
        status_code=401, detail="No se pudo validar las credenciales", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credenciales_exception
    except security.jwt.JWTError:
        raise credenciales_exception
        
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario is None:
        raise credenciales_exception
    return usuario

class GoogleToken(BaseModel):
    token: str

@app.post("/api/auth/google")
def login_con_google(google_data: GoogleToken, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(
            google_data.token, 
            google_requests.Request(), 
            "318282148406-908hoi15scu4vcc8v9lhqfkislin10cb.apps.googleusercontent.com"
        )
        
        email = idinfo['email']
        usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        
        if not usuario:
            usuario = models.Usuario(email=email, hashed_password="login_google")
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            
        access_token = security.crear_token_acceso(data={"sub": usuario.email})
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        print(f"🛑 EL MOTIVO EXACTO DEL RECHAZO ES: {e}")
        raise HTTPException(status_code=401, detail="Token de Google inválido")

# ==========================================
# --- RUTAS DE FAVORITOS (PRIVADAS) ---
# ==========================================

@app.post("/api/favoritos")
def añadir_favorito(
    favorito: schemas.FavoritoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual) 
):
    producto = db.query(models.Producto).filter(models.Producto.id == favorito.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    favorito_existente = db.query(models.Favorito).filter(
        models.Favorito.usuario_id == usuario_actual.id,
        models.Favorito.producto_id == favorito.producto_id
    ).first()
    
    if favorito_existente:
        return {"mensaje": "El producto ya está en tus favoritos"}
        
    nuevo_favorito = models.Favorito(usuario_id=usuario_actual.id, producto_id=favorito.producto_id)
    db.add(nuevo_favorito)
    db.commit()
    return {"mensaje": "Producto añadido a favoritos correctamente"}

@app.get("/api/favoritos", response_model=List[schemas.FavoriteResponse])
def obtener_favoritos(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    return db.query(models.Favorito).filter(models.Favorito.usuario_id == usuario_actual.id).all()

@app.delete("/api/favoritos/{producto_id}")
def eliminar_favorito(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    favorito = db.query(models.Favorito).filter(
        models.Favorito.usuario_id == usuario_actual.id,
        models.Favorito.producto_id == producto_id
    ).first()
    
    if not favorito:
        raise HTTPException(status_code=404, detail="El producto no está en tus favoritos")
        
    db.delete(favorito)
    db.commit()
    return {"mensaje": "Producto eliminado de favoritos"}