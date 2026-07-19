from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
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
    nombre = Column(String, index=True)
    descripcion = Column(String)
    precio = Column(Float)
    imagen_url = Column(String)
    afiliado_url = Column(String)
    sabor = Column(String, nullable=True)
    formato = Column(String, nullable=True)
    objetivo = Column(String, nullable=True)  # <-- NUEVA COLUMNA EN LA BD
    caracteristicas = Column(JSON, nullable=True)

    # Foreign Keys (Claves foráneas): Le dicen al producto a qué marca y categoría pertenece
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    # Relaciones: permiten a Python navegar entre las tablas fácilmente
    marca = relationship("Marca", back_populates="productos")
    categoria = relationship("Categoria", back_populates="productos")

    # --- SISTEMA DE USUARIOS Y FAVORITOS ---

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

