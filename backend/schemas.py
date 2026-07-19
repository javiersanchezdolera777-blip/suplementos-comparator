from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional
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

class ProductosPaginados(BaseModel):
    total_resultados: int
    productos: List[ProductoResponse]

# ==========================================
# --- MOLDES PARA USUARIOS Y SEGURIDAD ---
# ==========================================

class UsuarioCreate(BaseModel):
    """Datos que recibimos cuando alguien se registra"""
    email: str
    password: str

class UsuarioResponse(BaseModel):
    """Datos que devolvemos (¡Nunca devolvemos la contraseña!)"""
    id: int
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Formato oficial en el que se envían los JWT según el estándar de internet"""
    access_token: str
    token_type: str