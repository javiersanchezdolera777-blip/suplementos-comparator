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
@app.get("/api/productos", response_model=schemas.ProductosPaginados)
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

    # ¡Importante! Esto se hace ANTES de aplicar el offset y el limit
    total_resultados = query.count()
        
    # 3. Aplicamos la paginación para sacar solo los productos de la página actual
    productos = query.offset(skip).limit(limit).all()
    
    # 4. Devolvemos el "sobre" con el total y la lista de productos
    return {
        "total_resultados": total_resultados,
        "productos": productos
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