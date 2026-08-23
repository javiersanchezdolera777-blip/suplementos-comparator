import os
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import case, desc, or_, func
from sqlalchemy import nulls_last
from typing import List, Optional
from datetime import datetime
from fastapi import Query  # ✅ Correcto

# Importamos nuestras piezas
import models
import schemas
from database import engine, SessionLocal
import security
from busqueda import expandir_terminos_busqueda

# Orden de construcción
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Suplementos")

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "https://www.tussuplementos.com",
    "https://tussuplementos.com",
    "https://www.tussuplementos.es",
    "https://tussuplementos.es",
    "https://suplementos-comparator.vercel.app",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
        "service": "suparator-api",
    }


# --- RUTA DE MARCAS (CON PRODUCTOS) ---
@app.get("/api/marcas", response_model=List[schemas.BrandResponse])
def listar_marcas(db: Session = Depends(get_db)):
    """Devuelve únicamente las marcas que tienen productos en catálogo."""
    return (
        db.query(models.Marca)
        .filter(models.Marca.productos.any())
        .order_by(models.Marca.nombre.asc())
        .all()
    )


# --- RUTA: DICCIONARIO DE FILTROS COMPLETOS ---
@app.get("/api/config/filtros")
def obtener_filtros(db: Session = Depends(get_db)):
    marcas_activas = (
        db.query(models.Marca)
        .join(models.Producto)
        .group_by(models.Marca.id)
        .having(func.count(models.Producto.id) > 0)
        .filter(models.Marca.nombre != "Desconocida")
        .order_by(models.Marca.nombre.asc())
        .all()
    )

    categorias_activas = (
        db.query(models.Categoria)
        .join(models.Producto)
        .group_by(models.Categoria.id)
        .having(func.count(models.Producto.id) > 0)
        .filter(~models.Categoria.nombre.in_(["Accesorios", "Otros"]))
        .order_by(models.Categoria.nombre.asc())
        .all()
    )

    # NUEVO: Sabores dinámicos (Solo devuelve los que tienen > 0 productos)
    sabores_db = (
        db.query(models.Producto.sabor).filter(models.Producto.sabor.isnot(None)).all()
    )
    sabores_activos = set()
    for s in sabores_db:
        if s[0] and isinstance(s[0], list):
            for sabor_individual in s[0]:
                sabores_activos.add(sabor_individual)

    flavors_dinamicos = [
        sabor.value for sabor in schemas.SaborEnum if sabor.value in sabores_activos
    ]

    return {
        "brands": [m.nombre for m in marcas_activas],
        "categories": [c.nombre for c in categorias_activas],
        "flavors": flavors_dinamicos,  # <-- Filtro Mágico aplicado
        "formats": [formato.value for formato in schemas.FormatoEnum],
        "goals": [objetivo.value for objetivo in schemas.ObjetivoEnum],
        "quality_seals": [sello.value for sello in schemas.SelloCalidadEnum],
        "protein_types": [tipo.value for tipo in schemas.TipoProteinaEnum],
        "creatine_types": [tipo.value for tipo in schemas.TipoCreatinaEnum],
        "amino_profiles": [perfil.value for perfil in schemas.PerfilAminoacidosEnum],
        "vitamin_types": [tipo.value for tipo in schemas.TipoVitaminaEnum],
    }


@app.get("/api/productos/live-search")
def live_search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    grupos_tokens = expandir_terminos_busqueda(q)
    if not grupos_tokens:
        return {"productos": []}

    try:
        # Usamos la misma estructura de consulta que el catálogo principal
        query = (
            db.query(models.Producto)
            .join(models.Categoria, isouter=True)
            .join(models.Marca, isouter=True)
        )

        for grupo in grupos_tokens:
            condiciones_token = []
            for term in grupo:
                patron = f"%{term}%"
                condiciones_token.append(models.Producto.nombre.ilike(patron))
                condiciones_token.append(models.Marca.nombre.ilike(patron))
                condiciones_token.append(models.Categoria.nombre.ilike(patron))
            query = query.filter(or_(*condiciones_token))

        # Añadimos puntuación semántica para ordenación
        text_score = func.similarity(models.Producto.nombre, q).label("text_score")
        resultados = (
            query.order_by(
                text_score.desc(),
                nulls_last(models.Producto.clics_count.desc()),
                models.Producto.id.asc(),
            )
            .limit(4)
            .all()
        )

        items = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "marca": p.marca.nombre if p.marca else "HSN",
                "categoria": p.categoria.nombre if p.categoria else "Suplementos",
                "imagen_url": p.imagen_url,
                "precio_minimo": float(p.precio) if p.precio is not None else None,
                "formato": p.formato,
            }
            for p in resultados
        ]
        return {"productos": items}

    except Exception as e:
        import traceback

        print(f"[Error Live Search]: {e}")
        traceback.print_exc()
        return {"productos": []}


# --- RUTA PRINCIPAL DE PRODUCTOS ---
@app.get("/api/productos", response_model=schemas.PaginatedProducts)
def obtener_productos(
    request: Request,
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
    sin_gluten: Optional[bool] = Query(None),
    sin_lactosa: Optional[bool] = Query(None),
    sello_calidad: Optional[str] = None,
    tipo_proteina: Optional[str] = None,
    tipo_creatina: Optional[str] = None,
    perfil_aminoacidos: Optional[str] = None,
    tipo_vitamina: Optional[str] = None,
    busqueda: Optional[str] = None,
    q: Optional[str] = Query(None, description="Alias de búsqueda"),
    db: Session = Depends(get_db),
    porcentaje_proteina: Optional[int] = Query(
        None, description="Filtra por porcentaje de proteína (ej. 80)"
    ),
    solo_ofertas: Optional[bool] = Query(
        False, description="Muestra solo productos con descuento real"
    ),
    orden: str = Query(
        "relevancia",
        description="Orden de resultados: relevancia, precio_asc, precio_desc, descuento",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(100, le=200),
):
    # Join inicial maestro para evitar conflictos
    query = (
        db.query(models.Producto)
        .join(models.Categoria, isouter=True)
        .join(models.Marca, isouter=True)
    )

    # 1. Filtros de Categoría
    cat_str = categorias or categoria
    if cat_str and cat_str.lower() != "todos":
        lista_cats = [c.strip() for c in cat_str.split(",") if c.strip()]
        if lista_cats:
            query = query.filter(models.Categoria.nombre.in_(lista_cats))

    # 2. Filtros de Marca
    marca_str = marcas or marca
    if marca_str:
        lista_marcas_lower = [
            m.strip().lower() for m in marca_str.split(",") if m.strip()
        ]
        if lista_marcas_lower:
            query = query.filter(
                func.lower(models.Marca.nombre).in_(lista_marcas_lower)
            )

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
    if sin_gluten is True:
        query = query.filter(models.Producto.sin_gluten.is_(True))
    if sin_lactosa is True:
        query = query.filter(models.Producto.sin_lactosa.is_(True))
    if solo_ofertas:
        query = query.filter(
            models.Producto.precio_anterior.isnot(None),
            models.Producto.precio_anterior > models.Producto.precio,
        )

    if sello_calidad:
        query = query.filter(models.Producto.sello_calidad.ilike(f"%{sello_calidad}%"))

    # 5. Sub-filtros
    if tipo_proteina:
        query = query.filter(models.Producto.tipo_proteina.ilike(f"%{tipo_proteina}%"))
    if tipo_creatina:
        query = query.filter(models.Producto.tipo_creatina.ilike(f"%{tipo_creatina}%"))
    if perfil_aminoacidos:
        query = query.filter(
            models.Producto.perfil_aminoacidos.ilike(f"%{perfil_aminoacidos}%")
        )
    if tipo_vitamina:
        query = query.filter(models.Producto.tipo_vitamina.ilike(f"%{tipo_vitamina}%"))

    # 6. Buscador de texto libre con Expansión Semántica
    busqueda_final = busqueda or q
    if busqueda_final:
        grupos_tokens = expandir_terminos_busqueda(busqueda_final)
        for grupo in grupos_tokens:
            condiciones_token = []
            for term in grupo:
                patron = f"%{term}%"
                condiciones_token.append(models.Producto.nombre.ilike(patron))
                condiciones_token.append(models.Marca.nombre.ilike(patron))
                condiciones_token.append(models.Categoria.nombre.ilike(patron))
            query = query.filter(or_(*condiciones_token))

    # 7. ORDENACIÓN (Con Alias y Nulls Last)
    sort_final = (
        request.query_params.get("orden_precio")
        or request.query_params.get("ordenar_por")
        or request.query_params.get("sort")
        or orden
    )

    if sort_final in ["precio_asc", "price_asc", "asc"]:
        query = query.order_by(models.Producto.precio.asc())
    elif sort_final in ["precio_desc", "price_desc", "desc"]:
        query = query.order_by(models.Producto.precio.desc())
    elif sort_final == "descuento":
        query = query.order_by(
            (models.Producto.precio_anterior - models.Producto.precio).desc()
        )
    else:
        # ORDEN POR DEFECTO: RELEVANCIA INTELIGENTE
        if busqueda_final:
            text_score = func.similarity(models.Producto.nombre, busqueda_final).label(
                "text_score"
            )
            query = query.order_by(
                text_score.desc(),
                nulls_last(
                    models.Producto.clics_count.desc()
                ),  # <-- Obliga a que los Nulls vayan al final
                models.Producto.id.asc(),
            )
        else:
            query = query.order_by(
                nulls_last(
                    models.Producto.clics_count.desc()
                ),  # <-- Evita discrepancias Local vs Prod
                models.Producto.id.asc(),
            )

    # 8. Extraer y filtrar Sabores y Objetivos (Arrays Multiselección)
    # ¡AQUÍ HACEMOS LA EXTRACCIÓN A MEMORIA DE PYTHON!
    productos_raw = query.all()

    sabor_str = sabores or sabor
    sabores_lista = (
        [s.strip().lower() for s in sabor_str.split(",") if s.strip()]
        if sabor_str
        else []
    )

    objetivo_str = objetivos or objetivo
    objetivos_lista = (
        [o.strip().lower() for o in objetivo_str.split(",") if o.strip()]
        if objetivo_str
        else []
    )

    def cumple_filtros_arrays(producto):
        # ¿Cumple el sabor?
        if sabores_lista:
            valor_sabor = getattr(producto, "sabor", None)
            if isinstance(valor_sabor, list):
                if not any(str(item).lower() in sabores_lista for item in valor_sabor):
                    return False
            elif isinstance(valor_sabor, str):
                if not any(s in valor_sabor.lower() for s in sabores_lista):
                    return False
            else:
                return False

        # ¿Cumple el objetivo?
        if objetivos_lista:
            valor_obj = getattr(producto, "objetivo", None)
            if isinstance(valor_obj, list):
                if not any(str(item).lower() in objetivos_lista for item in valor_obj):
                    return False
            elif isinstance(valor_obj, str):
                if not any(o in valor_obj.lower() for o in objetivos_lista):
                    return False
            else:
                return False

        return True

    if sabores_lista or objetivos_lista:
        productos_filtrados = [p for p in productos_raw if cumple_filtros_arrays(p)]
    else:
        productos_filtrados = productos_raw

    # 9. Paginación Final
    total_resultados = len(productos_filtrados)
    offset_real = skip if skip > 0 else (page - 1) * limit
    productos = productos_filtrados[offset_real : offset_real + limit]

    return {"total_resultados": total_resultados, "productos": productos}


# ==========================================
# --- RUTA DE COMPARADOR MULTITIENDA ---
# ==========================================
@app.get("/api/productos/comparar", response_model=List[schemas.ProductResponse])
def comparar_productos(
    ids: str = Query(
        ...,
        description="IDs de los productos a comparar, separados por comas (ej. 10,45,102)",
    ),
    db: Session = Depends(get_db),
):
    try:
        # 1. Convertimos la cadena "10,45,102" en una lista de enteros únicos
        lista_ids = list(
            set(
                [
                    int(id_str.strip())
                    for id_str in ids.split(",")
                    if id_str.strip().isdigit()
                ]
            )
        )
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Formato de IDs inválido. Deben ser números."
        )

    # 2. Barrera de Seguridad (Máximo 4 productos para no saturar la UI ni la DB)
    if not lista_ids:
        raise HTTPException(
            status_code=400, detail="Debes proporcionar al menos un ID válido."
        )
    if len(lista_ids) > 4:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes comparar un máximo de 4 productos a la vez.",
        )

    # 3. Consulta súper optimizada usando el operador in_() de SQLAlchemy
    productos = (
        db.query(models.Producto).filter(models.Producto.id.in_(lista_ids)).all()
    )

    if not productos:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ninguno de los productos solicitados.",
        )

    # 4. Opcional pero recomendado: Ordenamos los resultados para que coincidan con el orden de los IDs solicitados
    productos.sort(key=lambda p: lista_ids.index(p.id) if p.id in lista_ids else 99)

    return productos


# --- RUTA DE PRODUCTO INDIVIDUAL POR ID ---
@app.get("/api/productos/{producto_id}", response_model=schemas.ProductResponse)
def obtener_producto_individual(producto_id: int, db: Session = Depends(get_db)):
    producto = (
        db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
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


# --- RUTA DE TRACKING DE CLICS DE AFILIADOS ---
@app.post("/api/click/{product_id}")
def track_click(product_id: int, db: Session = Depends(get_db)):
    # Incrementa el contador de clics del producto
    producto = (
        db.query(models.Producto).filter(models.Producto.id == product_id).first()
    )
    if producto:
        producto.clics_count = (producto.clics_count or 0) + 1
        db.commit()
        return {"status": "ok", "clics": producto.clics_count}
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# ==========================================
# --- RUTAS DE AUTENTICACIÓN Y USUARIOS ---
# ==========================================


@app.post("/api/registro", response_model=schemas.UsuarioResponse)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = (
        db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    )
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este email ya está registrado")

    password_cifrada = security.obtener_password_hash(usuario.password)
    nuevo_usuario = models.Usuario(
        email=usuario.email, hashed_password=password_cifrada
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@app.post("/api/login", response_model=schemas.Token)
def iniciar_sesion(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    user_db = (
        db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    )
    if not user_db or not security.verificar_password(
        usuario.password, user_db.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    access_token = security.crear_token_acceso(data={"sub": user_db.email})
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/swagger")
from fastapi.security import OAuth2PasswordRequestForm


@app.post("/api/login/swagger", include_in_schema=False)
def login_exclusivo_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Esta es una puerta trasera oculta solo para que funcione el candado verde de Swagger"""
    user_db = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == form_data.username)
        .first()
    )
    if not user_db or not security.verificar_password(
        form_data.password, user_db.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    access_token = security.crear_token_acceso(data={"sub": user_db.email})
    return {"access_token": access_token, "token_type": "bearer"}


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credenciales_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
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
        # Obtenemos el Client ID desde la variable de entorno
        client_id = os.getenv("GOOGLE_CLIENT_ID")

        idinfo = id_token.verify_oauth2_token(
            google_data.token,
            google_requests.Request(),
            client_id,  # ✅ Ahora usas la variable dinámica
        )

        email = idinfo["email"]
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
# --- RUTAS DE LA RED SOCIAL (PERFILES) ---
# ==========================================


@app.post("/api/perfil", response_model=schemas.PerfilResponse)
def crear_perfil(
    perfil_in: schemas.PerfilCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    # 1. Comprobar si el usuario ya tiene un perfil (Solo se permite 1 por cuenta)
    if usuario_actual.perfil:
        raise HTTPException(status_code=400, detail="Ya tienes un perfil creado.")

    # 2. Limpiamos el username (quitamos espacios y pasamos a minúsculas para evitar duplicados como "Pepe" y "pepe")
    username_limpio = perfil_in.username.strip().lower()
    if not username_limpio:
        raise HTTPException(
            status_code=400, detail="El nombre de usuario no puede estar vacío."
        )

    # 3. Comprobar si el username ya está pillado por otra persona
    perfil_existente = (
        db.query(models.Perfil)
        .filter(models.Perfil.username == username_limpio)
        .first()
    )
    if perfil_existente:
        raise HTTPException(
            status_code=400,
            detail="Este nombre de usuario ya está en uso. ¡Prueba con otro!",
        )

    # 4. Crear el perfil y vincularlo mágicamente al usuario que ha iniciado sesión
    nuevo_perfil = models.Perfil(
        usuario_id=usuario_actual.id,
        username=username_limpio,
        bio=perfil_in.bio,
        avatar_url=perfil_in.avatar_url,
        suplemento_favorito=perfil_in.suplemento_favorito,
    )

    # IMPORTANTE: Preservamos cómo el usuario escribió su nombre (ej: "FitBoy99")
    # pero guardamos la versión minúscula en la BD si queremos hacer búsquedas más seguras,
    # aunque en este caso guardaremos su versión original y usaremos .lower() en las búsquedas.
    nuevo_perfil.username = perfil_in.username.strip()

    db.add(nuevo_perfil)
    db.commit()
    db.refresh(nuevo_perfil)
    return nuevo_perfil


@app.get("/api/perfil/me", response_model=schemas.PerfilResponse)
def obtener_mi_perfil(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    """Devuelve el perfil social del usuario que tiene la sesión iniciada."""
    if not usuario_actual.perfil:
        raise HTTPException(
            status_code=404, detail="Aún no has configurado tu perfil social."
        )
    return usuario_actual.perfil


@app.get("/api/perfil/{username}", response_model=schemas.PerfilResponse)
def obtener_perfil_publico(username: str, db: Session = Depends(get_db)):
    """Visitar el perfil de otra persona (ej: tussuplementos.com/comunidad/pepe)"""
    # Buscamos ignorando mayúsculas y minúsculas gracias a ilike
    perfil = (
        db.query(models.Perfil)
        .filter(models.Perfil.username.ilike(username.strip()))
        .first()
    )
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado.")
    return perfil


# ==========================================
# --- RUTAS DE COMUNIDAD: SEGUIDORES ---
# ==========================================


@app.post("/api/comunidad/seguir/{username}")
def seguir_usuario(
    username: str,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    """Permite al usuario logueado seguir a otro perfil."""
    mi_perfil = usuario_actual.perfil
    if not mi_perfil:
        raise HTTPException(
            status_code=400, detail="Debes crear tu perfil social primero."
        )

    # Buscamos a la persona que queremos seguir
    perfil_objetivo = (
        db.query(models.Perfil)
        .filter(models.Perfil.username.ilike(username.strip()))
        .first()
    )
    if not perfil_objetivo:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Evitar que se siga a sí mismo (eso es muy triste)
    if mi_perfil.id == perfil_objetivo.id:
        raise HTTPException(
            status_code=400, detail="No puedes seguirte a ti mismo, narcisista."
        )

    # Comprobar si ya le sigue
    if perfil_objetivo in mi_perfil.seguidos:
        return {"mensaje": f"Ya sigues a {perfil_objetivo.username}."}

    # La magia de SQLAlchemy: Añadir a la lista es suficiente para actualizar la base de datos
    mi_perfil.seguidos.append(perfil_objetivo)
    db.commit()

    return {"mensaje": f"¡Ahora sigues a {perfil_objetivo.username}!"}


@app.delete("/api/comunidad/seguir/{username}")
def dejar_de_seguir_usuario(
    username: str,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    """Permite al usuario logueado dejar de seguir a otro perfil."""
    mi_perfil = usuario_actual.perfil
    if not mi_perfil:
        raise HTTPException(
            status_code=400, detail="Debes crear tu perfil social primero."
        )

    perfil_objetivo = (
        db.query(models.Perfil)
        .filter(models.Perfil.username.ilike(username.strip()))
        .first()
    )
    if not perfil_objetivo:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if perfil_objetivo not in mi_perfil.seguidos:
        raise HTTPException(
            status_code=400, detail=f"No sigues a {perfil_objetivo.username}."
        )

    mi_perfil.seguidos.remove(perfil_objetivo)
    db.commit()

    return {"mensaje": f"Has dejado de seguir a {perfil_objetivo.username}."}


# ==========================================
# --- RUTAS DE COMUNIDAD: STACKS (RUTINAS) ---
# ==========================================


@app.post("/api/stacks", response_model=schemas.StackResponse)
def crear_stack(
    stack_in: schemas.StackCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    """Crea un nuevo Stack vacío para el usuario (Ej: 'Definición 2026')."""
    mi_perfil = usuario_actual.perfil
    if not mi_perfil:
        raise HTTPException(
            status_code=400, detail="Debes crear tu perfil social primero."
        )

    nuevo_stack = models.Stack(
        perfil_id=mi_perfil.id,
        nombre=stack_in.nombre.strip(),
        descripcion=stack_in.descripcion,
        es_publico=stack_in.es_publico,
    )
    db.add(nuevo_stack)
    db.commit()
    db.refresh(nuevo_stack)

    return nuevo_stack


@app.post("/api/stacks/{stack_id}/productos/{producto_id}")
def anadir_producto_a_stack(
    stack_id: int,
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    """Mete un producto de la tienda dentro de un Stack tuyo."""
    mi_perfil = usuario_actual.perfil
    if not mi_perfil:
        raise HTTPException(
            status_code=400, detail="Debes crear tu perfil social primero."
        )

    # 1. Comprobamos que el stack existe y que es TUYO
    stack = (
        db.query(models.Stack)
        .filter(models.Stack.id == stack_id, models.Stack.perfil_id == mi_perfil.id)
        .first()
    )
    if not stack:
        raise HTTPException(
            status_code=404, detail="Stack no encontrado o no te pertenece."
        )

    # 2. Comprobamos que el producto que quieres añadir existe en el catálogo
    producto = (
        db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
    if not producto:
        raise HTTPException(
            status_code=404, detail="El producto no existe en el catálogo."
        )

    # 3. Comprobamos que no esté ya dentro para no duplicar
    if producto in stack.productos:
        return {"mensaje": "Este producto ya está en el Stack."}

    # Magia SQLAlchemy: Añadimos a la lista
    stack.productos.append(producto)
    db.commit()

    return {"mensaje": f"{producto.nombre} añadido a tu stack '{stack.nombre}'"}


@app.delete("/api/stacks/{stack_id}/productos/{producto_id}")
def quitar_producto_de_stack(
    stack_id: int,
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    """Saca un producto de tu Stack."""
    mi_perfil = usuario_actual.perfil
    if not mi_perfil:
        raise HTTPException(
            status_code=400, detail="Debes crear tu perfil social primero."
        )

    stack = (
        db.query(models.Stack)
        .filter(models.Stack.id == stack_id, models.Stack.perfil_id == mi_perfil.id)
        .first()
    )
    if not stack:
        raise HTTPException(
            status_code=404, detail="Stack no encontrado o no te pertenece."
        )

    producto = (
        db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
    if producto not in stack.productos:
        raise HTTPException(
            status_code=400, detail="El producto no está en este Stack."
        )

    stack.productos.remove(producto)
    db.commit()

    return {"mensaje": "Producto eliminado del Stack."}


# ==========================================
# --- RUTAS DE COMUNIDAD: GAMIFICACIÓN (CHECK-IN) ---
# ==========================================


@app.post("/api/comunidad/checkin")
def hacer_checkin_diario(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    """El ritual diario. Gana puntos y mantén tu racha de suplementación."""
    from datetime import date, timedelta

    mi_perfil = usuario_actual.perfil
    if not mi_perfil:
        raise HTTPException(
            status_code=400, detail="Debes crear tu perfil social primero."
        )

    hoy = date.today()
    ayer = hoy - timedelta(days=1)

    # 1. Escudo anti-trampas: Comprobar si ya hizo el check-in hoy
    check_hoy = (
        db.query(models.CheckDiario)
        .filter(
            models.CheckDiario.perfil_id == mi_perfil.id,
            models.CheckDiario.fecha == hoy,
        )
        .first()
    )

    if check_hoy:
        raise HTTPException(
            status_code=400,
            detail="¡Ya has hecho tu check-in hoy! Vuelve mañana para no perder tu racha.",
        )

    # 2. Sistema de Rachas: Comprobar si hizo el check-in ayer
    check_ayer = (
        db.query(models.CheckDiario)
        .filter(
            models.CheckDiario.perfil_id == mi_perfil.id,
            models.CheckDiario.fecha == ayer,
        )
        .first()
    )

    if check_ayer:
        mi_perfil.racha_actual += 1
    else:
        # Castigo por fallar un día: se reinicia la racha
        mi_perfil.racha_actual = 1

    # 3. Asignación de Puntos de Experiencia (XP)
    puntos_base = 10

    # ¡BONUS! Si alcanza un múltiplo de 7 días seguidos (una semana entera), le damos un premio gordo
    if mi_perfil.racha_actual > 0 and mi_perfil.racha_actual % 7 == 0:
        puntos_base += 50
        mensaje = f"¡INCREÍBLE! Has completado {mi_perfil.racha_actual} días seguidos. Toma 50 XP extra. 🔥"
    else:
        mensaje = "¡Check-in completado con éxito! Sigue así. 💪"

    mi_perfil.puntos_totales += puntos_base

    # 4. Registrar el check-in en el historial
    nuevo_check = models.CheckDiario(
        perfil_id=mi_perfil.id, fecha=hoy, puntos_ganados=puntos_base
    )

    db.add(nuevo_check)
    db.commit()
    db.refresh(mi_perfil)

    # Devolvemos el estado actual para que el frontend pinte los numeritos actualizados al instante
    return {
        "mensaje": mensaje,
        "puntos_ganados": puntos_base,
        "puntos_totales_actualizados": mi_perfil.puntos_totales,
        "racha_actualizada": mi_perfil.racha_actual,
    }


# ==========================================
# --- RUTAS DE FAVORITOS (PRIVADAS) ---
# ==========================================


@app.post("/api/favoritos")
def añadir_favorito(
    favorito: schemas.FavoritoCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    producto = (
        db.query(models.Producto)
        .filter(models.Producto.id == favorito.producto_id)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    favorito_existente = (
        db.query(models.Favorito)
        .filter(
            models.Favorito.usuario_id == usuario_actual.id,
            models.Favorito.producto_id == favorito.producto_id,
        )
        .first()
    )

    if favorito_existente:
        return {"mensaje": "El producto ya está en tus favoritos"}

    nuevo_favorito = models.Favorito(
        usuario_id=usuario_actual.id, producto_id=favorito.producto_id
    )
    db.add(nuevo_favorito)
    db.commit()
    return {"mensaje": "Producto añadido a favoritos correctamente"}


@app.get("/api/favoritos", response_model=List[schemas.FavoriteResponse])
def obtener_favoritos(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    return (
        db.query(models.Favorito)
        .filter(models.Favorito.usuario_id == usuario_actual.id)
        .all()
    )


@app.delete("/api/favoritos/{producto_id}")
def eliminar_favorito(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    favorito = (
        db.query(models.Favorito)
        .filter(
            models.Favorito.usuario_id == usuario_actual.id,
            models.Favorito.producto_id == producto_id,
        )
        .first()
    )

    if not favorito:
        raise HTTPException(
            status_code=404, detail="El producto no está en tus favoritos"
        )

    db.delete(favorito)
    db.commit()
    return {"mensaje": "Producto eliminado de favoritos"}


# ==========================================
# --- RUTAS DE NEWSLETTER ---
# ==========================================


@app.post("/api/newsletter/subscribe")
def suscribir_newsletter(
    suscripcion: schemas.NewsletterCreate, db: Session = Depends(get_db)
):
    email_limpio = suscripcion.email.lower().strip()
    registro = (
        db.query(models.SuscripcionNewsletter)
        .filter(models.SuscripcionNewsletter.email == email_limpio)
        .first()
    )

    if registro:
        if registro.activo:
            raise HTTPException(
                status_code=400, detail="Este email ya está suscrito a la newsletter"
            )
        else:
            registro.activo = True
            db.commit()

            from services.email_service import enviar_email_bienvenida

            enviar_email_bienvenida(email_limpio)

            return {"message": "¡Suscripción reactivada con éxito!"}

    nueva_suscripcion = models.SuscripcionNewsletter(email=email_limpio)
    db.add(nueva_suscripcion)
    db.commit()

    from services.email_service import enviar_email_bienvenida

    enviar_email_bienvenida(email_limpio)

    return {"message": "¡Suscripción completada con éxito!"}


# ==========================================
# --- RUTAS DE HISTORIAL (VISTOS RECIENTEMENTE) ---
# ==========================================


@app.post("/api/historial/{producto_id}")
def registrar_vista_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
):
    from datetime import datetime

    producto = (
        db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    historial = (
        db.query(models.HistorialVistas)
        .filter(
            models.HistorialVistas.usuario_id == usuario_actual.id,
            models.HistorialVistas.producto_id == producto_id,
        )
        .first()
    )

    if historial:
        historial.ultima_vista = datetime.utcnow()
    else:
        nuevo_historial = models.HistorialVistas(
            usuario_id=usuario_actual.id, producto_id=producto_id
        )
        db.add(nuevo_historial)

    db.commit()
    return {"status": "ok"}


# ==========================================
# --- RUTA DE COMPARADOR MULTITIENDA ---
# ==========================================
@app.get("/api/productos/comparar", response_model=List[schemas.ProductResponse])
def comparar_productos(
    ids: str = Query(
        ...,
        description="IDs de los productos a comparar, separados por comas (ej. 10,45,102)",
    ),
    db: Session = Depends(get_db),
):
    try:
        lista_ids = list(
            set(
                [
                    int(id_str.strip())
                    for id_str in ids.split(",")
                    if id_str.strip().isdigit()
                ]
            )
        )
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Formato de IDs inválido. Deben ser números."
        )

    if not lista_ids:
        raise HTTPException(
            status_code=400, detail="Debes proporcionar al menos un ID válido."
        )
    if len(lista_ids) > 4:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes comparar un máximo de 4 productos a la vez.",
        )

    productos = (
        db.query(models.Producto).filter(models.Producto.id.in_(lista_ids)).all()
    )

    if not productos:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ninguno de los productos solicitados.",
        )

    productos.sort(key=lambda p: lista_ids.index(p.id) if p.id in lista_ids else 99)
    return productos


# ==========================================
# --- ARRANQUE DEL SERVIDOR (RENDER) ---
# ==========================================
if __name__ == "__main__":
    import uvicorn
    import os

    # Render inyecta su propio puerto dinámico. Si no lo encuentra, usa el 8000.
    port = int(os.environ.get("PORT", 8000))

    # Pasamos el objeto 'app' directamente. El host "0.0.0.0" es obligatorio para Render.
    uvicorn.run(app, host="0.0.0.0", port=port)
