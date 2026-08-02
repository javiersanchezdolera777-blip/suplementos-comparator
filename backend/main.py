from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import case, desc, or_
from typing import List, Optional
from datetime import datetime
from fastapi import Query  # ✅ Correcto

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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tussuplementos.es",
        "https://www.tussuplementos.es",
    ], 
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
# --- RUTA PRINCIPAL DE PRODUCTOS ---
@app.get("/api/productos", response_model=schemas.PaginatedProducts)
def obtener_productos(
    skip: int = 0, 
    # Soportamos tanto el parámetro antiguo (singular) como el de multiselección (plural)
    categoria: Optional[str] = None,
    categorias: Optional[str] = Query(None),
    marca: Optional[str] = None,
    marcas: Optional[str] = Query(None),
    objetivo: Optional[str] = None,
    objetivos: Optional[str] = Query(None),
    sabor: Optional[str] = None,
    sabores: Optional[str] = Query(None),
    formato: Optional[str] = None,
    formatos: Optional[str] = Query(None),
    
    es_vegano: Optional[bool] = None,
    sello_calidad: Optional[str] = None,
    tipo_proteina: Optional[str] = None,
    tipo_creatina: Optional[str] = None,
    perfil_aminoacidos: Optional[str] = None,
    tipo_vitamina: Optional[str] = None,
    orden_precio: Optional[str] = None,
    busqueda: Optional[str] = None,
    q: Optional[str] = Query(None, description="Alias de búsqueda"),
    db: Session = Depends(get_db),
    porcentaje_proteina: Optional[int] = Query(None, description="Filtra por porcentaje de proteína (ej. 80)"),
    solo_ofertas: Optional[bool] = Query(False, description="Muestra solo productos con descuento real"), 
    ordenar_por: str = Query("relevancia", description="Orden de los resultados: relevancia, precio_kg_asc, etc."),
    page: int = Query(1, ge=1),
    limit: int = Query(100, le=200)
):
    # Join inicial maestro para evitar conflictos
    query = db.query(models.Producto).join(models.Categoria, isouter=True).join(models.Marca, isouter=True)
    
    # 1. Filtros de Categoría
    cat_str = categorias or categoria
    if cat_str and cat_str.lower() != "todos":
        lista_cats = [c.strip() for c in cat_str.split(",") if c.strip()]
        if lista_cats:
            query = query.filter(models.Categoria.nombre.in_(lista_cats))

    # 2. Filtros de Marca
    marca_str = marcas or marca
    if marca_str:
        lista_marcas = [m.strip() for m in marca_str.split(",") if m.strip()]
        if lista_marcas:
            query = query.filter(models.Marca.nombre.in_(lista_marcas))

    # 3. Filtro Porcentaje Proteína
    if porcentaje_proteina is not None:
        query = query.filter(models.Producto.porcentaje_proteina >= porcentaje_proteina)

    # 4. Filtros Básicos (Formatos, Vegano, Sellos)
    formato_str = formatos or formato
    if formato_str:
        lista_formatos = [f.strip() for f in formato_str.split(",") if f.strip()]
        if lista_formatos:
            query = query.filter(models.Producto.formato.in_(lista_formatos))

    if es_vegano is not None:
        query = query.filter(models.Producto.es_vegano == es_vegano)
    if solo_ofertas:
        query = query.filter(
            models.Producto.precio_anterior.isnot(None),
            models.Producto.precio_anterior > models.Producto.precio
        )

    if sello_calidad:
        query = query.filter(models.Producto.sello_calidad.ilike(f"%{sello_calidad}%"))
        
    # 5. Sub-filtros
    if tipo_proteina: query = query.filter(models.Producto.tipo_proteina.ilike(f"%{tipo_proteina}%"))
    if tipo_creatina: query = query.filter(models.Producto.tipo_creatina.ilike(f"%{tipo_creatina}%"))
    if perfil_aminoacidos: query = query.filter(models.Producto.perfil_aminoacidos.ilike(f"%{perfil_aminoacidos}%"))
    if tipo_vitamina: query = query.filter(models.Producto.tipo_vitamina.ilike(f"%{tipo_vitamina}%"))
        
    # 6. Buscador de texto libre
    busqueda_final = busqueda or q
    if busqueda_final:
        termino = f"%{busqueda_final}%"
        query = query.filter(
            or_(
                models.Producto.nombre.ilike(termino),
                models.Producto.descripcion.ilike(termino)
            )
        )
        
    # 7. ORDENACIÓN
    if orden_precio == "asc":
        query = query.order_by(models.Producto.precio.asc())
    elif orden_precio == "desc":
        query = query.order_by(models.Producto.precio.desc())
    elif ordenar_por == "precio_kg_asc":
        query = query.order_by(models.Producto.precio_por_kg.asc().nulls_last())
    elif ordenar_por == "descuento_desc":
        descuento = (models.Producto.precio_anterior - models.Producto.precio) / models.Producto.precio_anterior
        query = query.order_by(desc(descuento).nulls_last())
    elif ordenar_por == "relevancia":
        marcas_top = ['Optimum Nutrition', 'Dymatize', 'HSN', 'MuscleTech', 'Scitec Nutrition', 'California Gold Nutrition', 'Drasanvi', 'BSN', 'Cellucor', 'Nutrex']
        categorias_top = ['Proteínas', 'Creatinas', 'Pre-Entrenos', 'Aminoácidos']

        marca_score = case((models.Marca.nombre.in_(marcas_top), 10), else_=0)
        categoria_score = case((models.Categoria.nombre.in_(categorias_top), 5), else_=0)

        query = query.order_by(
            desc(marca_score + categoria_score),
            desc(models.Producto.id)
        )

    # 8. Extraer y filtrar Sabores y Objetivos (Arrays Multiselección)
    # ¡AQUÍ HACEMOS LA EXTRACCIÓN A MEMORIA DE PYTHON!
    productos_raw = query.all()

    sabor_str = sabores or sabor
    sabores_lista = [s.strip().lower() for s in sabor_str.split(",") if s.strip()] if sabor_str else []

    objetivo_str = objetivos or objetivo
    objetivos_lista = [o.strip().lower() for o in objetivo_str.split(",") if o.strip()] if objetivo_str else []

    def cumple_filtros_arrays(producto):
        # ¿Cumple el sabor?
        if sabores_lista:
            valor_sabor = getattr(producto, "sabor", None)
            if isinstance(valor_sabor, list):
                if not any(str(item).lower() in sabores_lista for item in valor_sabor): return False
            elif isinstance(valor_sabor, str):
                if not any(s in valor_sabor.lower() for s in sabores_lista): return False
            else: return False
            
        # ¿Cumple el objetivo?
        if objetivos_lista:
            valor_obj = getattr(producto, "objetivo", None)
            if isinstance(valor_obj, list):
                if not any(str(item).lower() in objetivos_lista for item in valor_obj): return False
            elif isinstance(valor_obj, str):
                if not any(o in valor_obj.lower() for o in objetivos_lista): return False
            else: return False
            
        return True

    if sabores_lista or objetivos_lista:
        productos_filtrados = [p for p in productos_raw if cumple_filtros_arrays(p)]
    else:
        productos_filtrados = productos_raw

    # 9. Paginación Final
    total_resultados = len(productos_filtrados)
    offset_real = skip if skip > 0 else (page - 1) * limit
    productos = productos_filtrados[offset_real : offset_real + limit]

    return {
        "total_resultados": total_resultados,
        "productos": productos
    }
# --- RUTA DE PRODUCTO INDIVIDUAL POR ID ---
@app.get("/api/productos/{producto_id}", response_model=schemas.ProductResponse)
def obtener_producto_individual(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# --- RUTA DE PRODUCTO INDIVIDUAL POR SLUG ---
@app.get("/api/productos/slug/{slug}", response_model=schemas.ProductResponse)
def obtener_producto_por_slug(slug: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.slug == slug).first()
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