from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

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

    # Foreign Keys (Claves foráneas): Le dicen al producto a qué marca y categoría pertenece
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    # Relaciones: permiten a Python navegar entre las tablas fácilmente
    marca = relationship("Marca", back_populates="productos")
    categoria = relationship("Categoria", back_populates="productos")