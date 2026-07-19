from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
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
import security

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

# --- NUEVA RUTA: DICCIONARIO DE FILTROS COMPLETOS ---
@app.get("/api/config/filtros")
def obtener_filtros(db: Session = Depends(get_db)):
    """
    Esta ruta recopila TODOS los filtros posibles para que Javiki dibuje los menús.
    Mezcla datos reales de la BD (Marcas/Categorías) con listas fijas (Sabores/Objetivos).
    """
    # 1. Vamos a Neon (BD) a buscar las Marcas y Categorías reales
    marcas_db = db.query(models.Marca).all()
    categorias_db = db.query(models.Categoria).all()
    
    # 2. Extraemos solo el nombre (texto) de cada una
    nombres_marcas = [m.nombre for m in marcas_db]
    nombres_categorias = [c.nombre for c in categorias_db]

    # 3. Lo empaquetamos TODO junto en INGLÉS para el Frontend
    return {
        "brands": nombres_marcas,                                       # Viene de la BD
        "categories": nombres_categorias,                               # Viene de la BD
        "flavors": [sabor.value for sabor in schemas.SaborEnum],        # Viene de schemas.py
        "formats": [formato.value for formato in schemas.FormatoEnum],  # Viene de schemas.py
        "goals": [objetivo.value for objetivo in schemas.ObjetivoEnum]  # Viene de schemas.py
    }


# --- RUTAS DE DATOS ---
# Quitamos el response_model para poder devolver los datos en inglés libremente
@app.get("/api/productos")
def obtener_productos(
    skip: int = 0, 
    limit: int = 100, 
    categoria: Optional[str] = None,
    marca: Optional[str] = None,
    objetivo: Optional[str] = None,
    sabor: Optional[str] = None,
    orden_precio: Optional[str] = None,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Producto)
    
    # 1. Filtros exactos (Intactos)
    if categoria:
        query = query.join(models.Categoria).filter(models.Categoria.nombre == categoria)
    if marca:
        query = query.join(models.Marca).filter(models.Marca.nombre == marca)
    if objetivo:
        query = query.filter(models.Producto.objetivo == objetivo)
    if sabor:
        query = query.filter(models.Producto.sabor == sabor)
        
    # 2. BUSCADOR DE TEXTO LIBRE (Intacto)
    if busqueda:
        termino = f"%{busqueda}%"
        query = query.filter(
            or_(
                models.Producto.nombre.ilike(termino),
                models.Producto.descripcion.ilike(termino)
            )
        )
        
    # 3. Lógica de ordenación (Intacta)
    if orden_precio == "asc":
        query = query.order_by(models.Producto.precio.asc())
    elif orden_precio == "desc":
        query = query.order_by(models.Producto.precio.desc())

    # ¡Importante! Esto se hace ANTES de aplicar el offset y el limit
    total_resultados = query.count()
    
    # -----------------------------------------------------------------
    # FIX 1: CONTROL DE TABLA VACÍA / SIN RESULTADOS (Evita Error 500)
    # -----------------------------------------------------------------
    if total_resultados == 0:
        return {"total_resultados": 0, "productos": []}
        
    # 3. Aplicamos la paginación
    productos = query.offset(skip).limit(limit).all()
    
    # -----------------------------------------------------------------
    # FIX 2: MAPEO DE ESPAÑOL A INGLÉS PARA JAVIKI
    # -----------------------------------------------------------------
    productos_mapeados = []
    for p in productos:
        productos_mapeados.append({
            "id": p.id,
            "name": p.nombre,              # Traducción
            "description": p.descripcion,  # Traducción
            "price": p.precio,             # Traducción
            "image_url": p.imagen_url,     # Traducción
            # Dejamos estos en español o inglés dependiendo de cómo los pida él en el Frontend
            "brand": p.marca.nombre if hasattr(p, 'marca') and p.marca else None, 
            "category": p.categoria.nombre if hasattr(p, 'categoria') and p.categoria else None,
            "goal": p.objetivo,
            "flavor": p.sabor
        })
    
    # 4. Devolvemos el "sobre" con el total y la lista mapeada en inglés
    return {
        "total_resultados": total_resultados,
        "productos": productos_mapeados
    }
        


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

# ==========================================
# --- RUTAS DE AUTENTICACIÓN Y USUARIOS ---
# ==========================================

@app.post("/api/registro", response_model=schemas.UsuarioResponse)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Comprobamos si el email ya existe
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este email ya está registrado")
        
    # 2. Ciframos la contraseña (¡Nunca la guardamos en texto plano!)
    password_cifrada = security.obtener_password_hash(usuario.password)
    
    # 3. Guardamos el nuevo usuario en Neon
    nuevo_usuario = models.Usuario(email=usuario.email, hashed_password=password_cifrada)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


@app.post("/api/login", response_model=schemas.Token)
def iniciar_sesion(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Buscamos al usuario por su email
    user_db = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    
    # 2. Si no existe o la contraseña está mal, damos error genérico por seguridad
    if not user_db or not security.verificar_password(usuario.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
        
    # 3. ¡Todo correcto! Fabricamos la pulsera VIP (JWT)
    access_token = security.crear_token_acceso(data={"sub": user_db.email})
    
    # 4. Se la entregamos a Javiki en el formato oficial
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# --- EL PORTERO (Verificador de Tokens) ---
# ==========================================
# Esto le dice a FastAPI dónde se consiguen los tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """El portero: Lee el JWT, verifica que no esté caducado y saca al usuario de la BD"""
    credenciales_exception = HTTPException(
        status_code=401, detail="No se pudo validar las credenciales", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # Decodificamos la pulsera con nuestra palabra secreta
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

# ==========================================
# --- INICIO DE SESIÓN CON GOOGLE ---
# ==========================================
class GoogleToken(BaseModel):
    token: str

@app.post("/api/auth/google")
def login_con_google(google_data: GoogleToken, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(
            google_data.token, 
            google_requests.Request(), 
            "318282148406-908hoi15scu4vcc8v9lhqfkislin10cb.apps.googleusercontent.com" # <--- ¡Cámbialo aquí!
        )
        
        email = idinfo['email']
        
        # 2. Buscamos si el usuario ya existe en nuestra base de datos
        usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        
        # 3. Si es la primera vez que entra con Google, le creamos una cuenta sin contraseña
        if not usuario:
            usuario = models.Usuario(email=email, hashed_password="login_google")
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            
        # 4. Le fabricamos nuestra propia pulsera VIP para que use la web
# ... código anterior ...
        access_token = security.crear_token_acceso(data={"sub": usuario.email})
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        # ¡ESTO ES LO NUEVO! Imprimirá el error exacto en tu terminal negra
        print(f"🛑 EL MOTIVO EXACTO DEL RECHAZO ES: {e}")
        raise HTTPException(status_code=401, detail="Token de Google inválido")
    
# ==========================================
# --- RUTAS DE FAVORITOS (PRIVADAS) ---
# ==========================================

@app.post("/api/favoritos")
def añadir_favorito(
    favorito: schemas.FavoritoCreate, 
    db: Session = Depends(get_db),
    # AQUÍ ESTÁ LA MAGIA: Obligamos a que haya un token válido y sacamos al usuario
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual) 
):
    # 1. Comprobar si el producto existe en la base de datos
    producto = db.query(models.Producto).filter(models.Producto.id == favorito.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # 2. Comprobar si ya lo tiene en favoritos para no crear duplicados
    favorito_existente = db.query(models.Favorito).filter(
        models.Favorito.usuario_id == usuario_actual.id,
        models.Favorito.producto_id == favorito.producto_id
    ).first()
    
    if favorito_existente:
        return {"mensaje": "El producto ya está en tus favoritos"}
        
    # 3. Guardar el nuevo favorito vinculando el ID del usuario y el del producto
    nuevo_favorito = models.Favorito(usuario_id=usuario_actual.id, producto_id=favorito.producto_id)
    db.add(nuevo_favorito)
    db.commit()
    
    return {"mensaje": "Producto añadido a favoritos correctamente"}


@app.get("/api/favoritos")
def obtener_favoritos(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    # 1. Buscamos los favoritos SOLO del usuario que está haciendo la petición
    favoritos_db = db.query(models.Favorito).filter(models.Favorito.usuario_id == usuario_actual.id).all()
    
    # 2. Los mapeamos al inglés al vuelo para que el Frontend de Javiki no explote
    resultado = []
    for fav in favoritos_db:
        p = fav.producto
        resultado.append({
            "favorite_id": fav.id,
            "product_id": fav.producto_id,
            "product": {
                "id": p.id,
                "name": p.nombre,              
                "description": p.descripcion,  
                "price": p.precio,             
                "image_url": p.imagen_url,     
                "brand": p.marca.nombre if hasattr(p, 'marca') and p.marca else None, 
                "category": p.categoria.nombre if hasattr(p, 'categoria') and p.categoria else None,
                "goal": p.objetivo,
                "flavor": p.sabor
            }
        })
        
    return resultado


@app.delete("/api/favoritos/{producto_id}")
def eliminar_favorito(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    # Buscamos el favorito exacto de ese usuario
    favorito = db.query(models.Favorito).filter(
        models.Favorito.usuario_id == usuario_actual.id,
        models.Favorito.producto_id == producto_id
    ).first()
    
    if not favorito:
        raise HTTPException(status_code=404, detail="El producto no está en tus favoritos")
        
    # Lo eliminamos
    db.delete(favorito)
    db.commit()
    
    return {"mensaje": "Producto eliminado de favoritos"}