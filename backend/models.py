from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from database import Base

# ... El resto de tu código se queda exactamente igual ...
class Marca(Base):
    __tablename__ = "marcas" # El nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

    # Relación inversa: una marca puede tener muchos productos
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
    imagen_url = Column(String)
    afiliado_url = Column(String)

    # --- NUEVAS COLUMNAS ---
    slug = Column(String, index=True) 
    peso_gramos = Column(Integer, nullable=True) # Ej: 1000 para 1kg, 2000 para 2kg
    precio_por_kg = Column(Float, nullable=True) # <-- Columna real

    
    # --- RELACIONES BÁSICAS ---
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    
    categoria = relationship("Categoria")
    marca = relationship("Marca")

    # ==========================================
    # --- 🌍 FILTROS GLOBALES ---
    # ==========================================
    objetivo = Column(String)
    sabor = Column(JSON, default=list)
    formato = Column(String)                     # NUEVO: Polvo, Cápsulas, Líquido...
    es_vegano = Column(Boolean, default=False)   # NUEVO: True/False
    sello_calidad = Column(String)               # NUEVO: Creapure, Lacprodan, Kyowa...

    # ==========================================
    # --- 🔬 SUB-FILTROS ESPECÍFICOS ---
    # (Si no aplican al producto, se quedan en blanco/NULL)
    # ==========================================
    
    # 🥛 Para Proteínas
    tipo_proteina = Column(String)               # Whey, Isolate, Caseína, Vegetal...
    porcentaje_proteina = Column(Integer)        # Ej: 80 (para 80%), 90...
    
    # ⚡ Para Creatinas
    tipo_creatina = Column(String)               # Monohidrato, HCL, Kre-Alkalyn...
    
    # 🧬 Para Aminoácidos
    perfil_aminoacidos = Column(String)          # BCAA, EAA, Glutamina, Beta-Alanina...
    
    # 💊 Para Vitaminas y Minerales
    tipo_vitamina = Column(String)               # Multivitamínico, Vitamina C, Magnesio...


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # ¡Nunca guardamos contraseñas reales!
    favoritos = relationship("Favorito", back_populates="usuario")


class Favorito(Base):
    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    # El ID del usuario que hace clic en el corazón
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    # El ID del producto al que le ha dado like
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)

    # Relaciones para que Python pueda navegar entre las tablas fácilmente
    usuario = relationship("Usuario", back_populates="favoritos")
    producto = relationship("Producto")

