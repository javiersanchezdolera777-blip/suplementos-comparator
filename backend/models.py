from sqlalchemy import ARRAY, Column, Integer, String, Float, ForeignKey, Boolean, JSON, DateTime, Date, Table, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ==========================================
# --- TABLAS PUENTE (MANY-TO-MANY) ---
# ==========================================

# Tabla invisible para que los usuarios puedan seguirse entre sí
seguidores = Table(
    'seguidores', Base.metadata,
    Column('seguidor_id', Integer, ForeignKey('perfiles.id', ondelete="CASCADE"), primary_key=True),
    Column('seguido_id', Integer, ForeignKey('perfiles.id', ondelete="CASCADE"), primary_key=True)
)

# Tabla invisible para meter varios productos dentro de un mismo Stack
stack_producto = Table(
    'stack_producto', Base.metadata,
    Column('stack_id', Integer, ForeignKey('stacks.id', ondelete="CASCADE"), primary_key=True),
    Column('producto_id', Integer, ForeignKey('productos.id', ondelete="CASCADE"), primary_key=True)
)

# ==========================================
# --- MODELOS PRINCIPALES (CATÁLOGO) ---
# ==========================================

class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

    productos = relationship("Producto", back_populates="marca")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)
    precio_anterior = Column(Float, nullable=True)
    imagen_url = Column(String)
    afiliado_url = Column(String)

    tienda = Column(String, nullable=True)
    slug = Column(String, index=True) 
    peso_gramos = Column(Integer, nullable=True) 
    precio_por_kg = Column(Float, nullable=True) 
    clics_count = Column(Integer, default=0)    
    publicado_telegram = Column(Boolean, default=False) 
    
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    
    categoria = relationship("Categoria")
    marca = relationship("Marca")

    objetivo = Column(JSON, nullable=True)
    sabor = Column(JSON, default=list)
    formato = Column(String, nullable=True)                    
    es_vegano = Column(Boolean, default=False)   
    sin_gluten = Column(Boolean, default=False, nullable=True, index=True)
    sin_lactosa = Column(Boolean, default=False, nullable=True, index=True)
    sello_calidad = Column(String)               

    tipo_proteina = Column(String)               
    porcentaje_proteina = Column(Integer)        
    tipo_creatina = Column(String)               
    perfil_aminoacidos = Column(String)          
    tipo_vitamina = Column(String)               

    # Relación inversa con las reseñas de la comunidad
    resenas = relationship("ResenaSabor", back_populates="producto")


# ==========================================
# --- MODELOS DE USUARIO Y AUTENTICACIÓN ---
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  
    fecha_ultimo_retargeting = Column(DateTime, nullable=True) 
    
    favoritos = relationship("Favorito", back_populates="usuario")
    historial_vistas = relationship("HistorialVistas", back_populates="usuario")
    
    # NUEVO: Enlace 1 a 1 con su Perfil Social
    perfil = relationship("Perfil", back_populates="usuario", uselist=False, cascade="all, delete-orphan")


class Favorito(Base):
    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="favoritos")
    producto = relationship("Producto")

class SuscripcionNewsletter(Base):
    __tablename__ = "suscripciones_newsletter"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

class HistorialVistas(Base):
    __tablename__ = "historial_vistas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    ultima_vista = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="historial_vistas")
    producto = relationship("Producto")


# ==========================================
# --- NUEVA CAPA SOCIAL & COMUNIDAD 🌟 ---
# ==========================================

class Perfil(Base):
    """
    El escaparate público del usuario. 
    Se separa del 'Usuario' para mantener el email y password privados.
    """
    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Identidad
    username = Column(String, unique=True, index=True, nullable=False)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    suplemento_favorito = Column(String, nullable=True) # Ej: "Creatina Creapure", "Whey de Vainilla"
    
    # Gamificación global
    puntos_totales = Column(Integer, default=0)
    racha_actual = Column(Integer, default=0)
    objetivo_etapa = Column(String, default="Mantenimiento") # Puede ser: "Volumen", "Definición", "Mantenimiento"

    # Relaciones
    usuario = relationship("Usuario", back_populates="perfil")
    stacks = relationship("Stack", back_populates="creador", cascade="all, delete-orphan")
    resenas = relationship("ResenaSabor", back_populates="perfil", cascade="all, delete-orphan")
    checkins = relationship("CheckDiario", back_populates="perfil", cascade="all, delete-orphan")
    
    
    # Sistema de seguidores (Self-referential Many-to-Many)
    seguidos = relationship(
        "Perfil",
        secondary=seguidores,
        primaryjoin=id==seguidores.c.seguidor_id,
        secondaryjoin=id==seguidores.c.seguido_id,
        backref="seguidores_asociados"
    )


class Stack(Base):
    """
    Agrupaciones de productos. Ej: "Stack de Definición 2026", "Mi Combo Pre-Entreno"
    """
    __tablename__ = "stacks"

    id = Column(Integer, primary_key=True, index=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    es_publico = Column(Boolean, default=True) # Por si quieren guardar un stack privado

    creador = relationship("Perfil", back_populates="stacks")
    # Los productos que están dentro de este Stack
    productos = relationship("Producto", secondary=stack_producto)


class ResenaSabor(Base):
    """
    Para que los usuarios confirmen que han probado un sabor y lo puntúen.
    """
    __tablename__ = "resenas_sabores"

    id = Column(Integer, primary_key=True, index=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    
    sabor_probado = Column(String, nullable=False) # Ej: "Chocolate Avellana"
    nota = Column(Integer, nullable=False) # Del 1 al 10
    comentario = Column(Text, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    perfil = relationship("Perfil", back_populates="resenas")
    producto = relationship("Producto", back_populates="resenas")


class CheckDiario(Base):
    """
    El ritual diario. Un registro de que hoy te has tomado tus suplementos.
    """
    __tablename__ = "checks_diarios"

    id = Column(Integer, primary_key=True, index=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id", ondelete="CASCADE"), nullable=False)
    # Guardamos solo la fecha (sin hora) para saber si hizo el check del día
    fecha = Column(Date, default=datetime.utcnow().date, nullable=False)
    puntos_ganados = Column(Integer, default=10)

    perfil = relationship("Perfil", back_populates="checkins")