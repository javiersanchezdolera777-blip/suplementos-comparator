from pydantic import BaseModel, ConfigDict

# Esquema para responder con una Marca
class MarcaResponse(BaseModel):
    id: int
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)

# Esquema para responder con una Categoría
class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)

# Esquema para responder con un Producto completo
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    precio: float
    imagen_url: str
    afiliado_url: str
    
    # Aquí anidamos los esquemas anteriores para que el producto incluya su marca y categoría
    marca: MarcaResponse
    categoria: CategoriaResponse
    
    # Esta línea mágica permite que Pydantic lea directamente los modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)