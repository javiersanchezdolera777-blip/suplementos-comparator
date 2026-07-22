from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, List, Optional
from enum import Enum

# ==========================================
# --- 1. ENUMS (GUARDIANES EN ESPAÑOL PARA LA BD) ---
# ==========================================
class CategoriaEnum(str, Enum):
    proteinas = "Proteínas"
    creatinas = "Creatinas"
    aminoacidos = "Aminoácidos"
    vitaminas = "Vitaminas y Minerales"
    pre_entrenos = "Pre-Entrenos"
    alimentacion = "Alimentación Saludable"
    accesorios = "Accesorios"
    salud = "Salud y Bienestar"
    otros = "Otros"

class SaborEnum(str, Enum):
    fresa = "Fresa"
    vainilla = "Vainilla"
    chocolate = "Chocolate"
    neutro = "Sin sabor"
    limon = "Limón"
    frutas = "Frutas del bosque"
    cookies = "Cookies & Cream"
    platano = "Plátano"
    cafe = "Café / Capuchino"

class FormatoEnum(str, Enum):
    polvo = "Polvo"
    capsulas = "Cápsulas"
    liquido = "Líquido"
    barrita = "Barrita"
    gominolas = "Gominolas"

class ObjetivoEnum(str, Enum):
    volumen = "Volumen Muscular"
    definicion = "Pérdida de Peso"
    salud = "Salud y Bienestar"
    rendimiento = "Rendimiento Deportivo"

class SelloCalidadEnum(str, Enum):
    creapure = "Creapure"
    lacprodan = "Lacprodan"
    kyowa = "Kyowa"
    isolac = "Isolac"
    optipep = "Optipep"
    carnipure = "Carnipure"

class TipoProteinaEnum(str, Enum):
    whey = "Whey Concentrado"
    isolate = "Isolate (Aislado)"
    hidrolizado = "Hidrolizado"
    caseina = "Caseína"
    vegetal = "Vegetal"

class TipoCreatinaEnum(str, Enum):
    monohidrato = "Monohidrato"
    hcl = "HCL"
    kre_alkalyn = "Kre-Alkalyn"
    micronizada = "Micronizada"

class PerfilAminoacidosEnum(str, Enum):
    bcaa = "BCAA"
    eaa = "EAA"
    glutamina = "Glutamina"
    citrulina = "Citrulina"
    beta_alanina = "Beta-Alanina"

class TipoVitaminaEnum(str, Enum):
    multivitaminico = "Multivitamínico"
    vitamina_c = "Vitamina C"
    vitamina_d = "Vitamina D"
    magnesio = "Magnesio"
    omega3 = "Omega-3"

def normalizar_marca(nombre: str) -> str:
    """
    Recibe un nombre de marca caótico y lo devuelve limpio y capitalizado.
    Ejemplo: "  my PROTEIN  " -> "My Protein"
    """
    if not nombre:
        return "Desconocida"
    # Quita espacios dobles y a los lados, y capitaliza cada palabra
    return " ".join(nombre.split()).title()

# ==========================================
# --- 2. LOS ESQUEMAS DE RESPUESTA (100% INGLÉS PARA EL FRONTEND) ---
# ==========================================
class BrandResponse(BaseModel):
    id: int
    name: str = Field(validation_alias="nombre")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CategoryResponse(BaseModel):
    id: int
    name: str = Field(validation_alias="nombre")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ProductResponse(BaseModel):
    id: int
    name: str = Field(validation_alias="nombre")
    description: str = Field(validation_alias="descripcion")
    price: float = Field(validation_alias="precio")
    image_url: str = Field(validation_alias="imagen_url")
    affiliate_url: str = Field(validation_alias="afiliado_url", default="")

    slug: Optional[str] = None
    weight_grams: Optional[int] = Field(validation_alias="peso_gramos", default=None)
    price_per_kg: Optional[float] = Field(validation_alias="precio_por_kg", default=None)
    
    # --- Filtros Globales ---
    flavor: List[str] = Field(validation_alias="sabor", default_factory=list)    
    format: Optional[FormatoEnum] = Field(validation_alias="formato", default=None)
    goal: Optional[ObjetivoEnum] = Field(validation_alias="objetivo", default=None)
    is_vegan: bool = Field(validation_alias="es_vegano", default=False)
    quality_seal: Optional[SelloCalidadEnum] = Field(validation_alias="sello_calidad", default=None)
    
    # --- Sub-filtros por Categoría ---
    protein_type: Optional[TipoProteinaEnum] = Field(validation_alias="tipo_proteina", default=None)
    protein_percentage: Optional[int] = Field(validation_alias="porcentaje_proteina", default=None)
    creatine_type: Optional[TipoCreatinaEnum] = Field(validation_alias="tipo_creatina", default=None)
    amino_profile: Optional[PerfilAminoacidosEnum] = Field(validation_alias="perfil_aminoacidos", default=None)
    vitamin_type: Optional[TipoVitaminaEnum] = Field(validation_alias="tipo_vitamina", default=None)
    
    characteristics: Optional[Dict[str, Any]] = Field(validation_alias="caracteristicas", default=None)
    
    # Objetos anidados en inglés
    brand: Optional[BrandResponse] = Field(validation_alias="marca", default=None)
    category: Optional[CategoryResponse] = Field(validation_alias="categoria", default=None)
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PaginatedProducts(BaseModel):
    total_resultados: int
    productos: List[ProductResponse]

# ==========================================
# --- MOLDES PARA USUARIOS Y SEGURIDAD ---
# ==========================================
class UsuarioCreate(BaseModel):
    email: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# --- ESQUEMAS DE FAVORITOS ---
# ==========================================
class FavoritoCreate(BaseModel):
    producto_id: int

class FavoriteResponse(BaseModel):
    favorite_id: int = Field(validation_alias="id")
    product_id: int = Field(validation_alias="producto_id")
    product: ProductResponse = Field(validation_alias="producto")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)