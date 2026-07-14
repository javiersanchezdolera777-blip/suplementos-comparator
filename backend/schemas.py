from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
from enum import Enum

# --- 1. NUESTRAS ETIQUETAS OFICIALES (GUARDIANES) ---
class SaborEnum(str, Enum):
    fresa = "Fresa"
    vainilla = "Vainilla"
    chocolate = "Chocolate"
    neutro = "Sin sabor"
    limon = "Limón"
    frutas = "Frutas del bosque"

class FormatoEnum(str, Enum):
    polvo = "Polvo"
    capsulas = "Cápsulas"
    liquido = "Líquido"
    barrita = "Barrita"

class ObjetivoEnum(str, Enum):
    volumen = "Volumen Muscular"
    definicion = "Pérdida de Peso"
    salud = "Salud y Bienestar"
    rendimiento = "Rendimiento Deportivo"

# --- 2. LOS ESQUEMAS DE RESPUESTA ---
class MarcaResponse(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    precio: float
    imagen_url: str
    afiliado_url: str
    
    # Usamos nuestros guardianes aquí. Si la BD escupe un sabor raro, Pydantic avisará.
    sabor: Optional[SaborEnum] = None
    formato: Optional[FormatoEnum] = None
    objetivo: Optional[ObjetivoEnum] = None
    
    # Nuestro diccionario JSON dinámico para cosas específicas (Creapure, Whey, etc.)
    caracteristicas: Optional[Dict[str, Any]] = None
    
    marca: MarcaResponse
    categoria: CategoriaResponse
    
    model_config = ConfigDict(from_attributes=True)