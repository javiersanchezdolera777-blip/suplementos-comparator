from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
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
    coco = "Coco"
    caramelo = "Caramelo"
    avellana = "Avellana"
    cacahuete = "Cacahuete"
    almendra = "Almendra"
    menta = "Menta"


class FormatoEnum(str, Enum):
    polvo = "Polvo"
    capsulas = "Cápsulas"
    liquido_gel = "Líquido / Gel"
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
    if not nombre:
        return "Desconocida"
    n_limpio = " ".join(str(nombre).split()).title()
    n_lower = n_limpio.lower()

    # 1. Gamas y submarcas propias de HSN -> Todas son marca "HSN"
    lineas_hsn = [
        "hsn",
        "hsn store",
        "hsnstore",
        "hsn-store",
        "hsn packs",
        "sport series",
        "sportseries",
        "essential series",
        "essentialseries",
        "raw series",
        "rawseries",
        "food series",
        "foodseries",
        "keto series",
        "ketoseries",
        "flavour series",
        "flavourseries",
        "myco nutrition",
        "myconutrition",
        "bio series",
        "bioseries",
    ]
    if any(linea in n_lower for linea in lineas_hsn):
        return "HSN"

    # 2. Marcas externas reales vendidas en HSN
    if "now" in n_lower:
        return "NOW Foods"
    if "swanson" in n_lower:
        return "Swanson"
    if n_lower in ["sportlive", "sport live", "pharma2go", "farma2go", "desconocida"]:
        return "Desconocida"

    return n_limpio


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
    precio_anterior: Optional[float] = None
    image_url: str = Field(validation_alias="imagen_url")
    affiliate_url: str = Field(validation_alias="afiliado_url", default="")

    slug: Optional[str] = None

    @field_validator("affiliate_url", mode="before")
    def normalize_affiliate_url(cls, v):
        return v or ""

    tienda: Optional[str] = None
    weight_grams: Optional[int] = Field(validation_alias="peso_gramos", default=None)
    price_per_kg: Optional[float] = Field(
        validation_alias="precio_por_kg", default=None
    )

    # --- Filtros Globales ---
    flavor: List[str] = Field(validation_alias="sabor", default_factory=list)
    format: Optional[FormatoEnum] = Field(validation_alias="formato", default=None)
    goals: Optional[List[str]] = Field(validation_alias="objetivos", default=None)
    is_vegan: bool = Field(validation_alias="es_vegano", default=False)
    sin_gluten: bool = False
    sin_lactosa: bool = False
    quality_seal: Optional[SelloCalidadEnum] = Field(
        validation_alias="sello_calidad", default=None
    )

    @field_validator("flavor", mode="before")
    def normalize_flavor(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(item) for item in v]
        return []

    # --- Sub-filtros por Categoría ---
    protein_type: Optional[TipoProteinaEnum] = Field(
        validation_alias="tipo_proteina", default=None
    )
    protein_percentage: Optional[int] = Field(
        validation_alias="porcentaje_proteina", default=None
    )
    creatine_type: Optional[TipoCreatinaEnum] = Field(
        validation_alias="tipo_creatina", default=None
    )
    amino_profile: Optional[PerfilAminoacidosEnum] = Field(
        validation_alias="perfil_aminoacidos", default=None
    )
    vitamin_type: Optional[TipoVitaminaEnum] = Field(
        validation_alias="tipo_vitamina", default=None
    )

    characteristics: Optional[Dict[str, Any]] = Field(
        validation_alias="caracteristicas", default=None
    )

    # Objetos anidados en inglés
    brand: Optional[BrandResponse] = Field(validation_alias="marca", default=None)
    category: Optional[CategoryResponse] = Field(
        validation_alias="categoria", default=None
    )

    @model_validator(mode="after")
    def filter_intelligent_price_per_kg(self):
        if self.price_per_kg is not None:
            # Regla 1: Categorías Core
            palabras_clave = [
                "proteina",
                "creatina",
                "carbohidrato",
                "ganador",
                "mass",
                "gainer",
            ]
            name_lower = self.name.lower() if self.name else ""
            cat_lower = (
                self.category.name.lower()
                if (self.category and self.category.name)
                else ""
            )

            es_core = any(p in name_lower for p in palabras_clave) or any(
                p in cat_lower for p in palabras_clave
            )
            if not es_core:
                self.price_per_kg = None

            # Regla 2: Filtro de Cordura (Outliers)
            if self.price_per_kg is not None:
                if self.price_per_kg > 100 or self.price_per_kg < 2:
                    self.price_per_kg = None

        return self

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


# ==========================================
# --- ESQUEMAS DE NEWSLETTER ---
# ==========================================
class NewsletterCreate(BaseModel):
    email: str = Field(
        ..., pattern=r"^\S+@\S+\.\S+$", description="Dirección de correo electrónico"
    )

# ==========================================
# --- ESQUEMAS SOCIALES Y DE COMUNIDAD ---
# ==========================================
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PerfilBase(BaseModel):
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    suplemento_favorito: Optional[str] = None
    objetivo_etapa: Optional[str] = "Mantenimiento"

class PerfilCreate(PerfilBase):
    pass

class PerfilResponse(PerfilBase):
    id: int
    puntos_totales: int
    racha_actual: int

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime

class StackBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    es_publico: Optional[bool] = True

class StackCreate(StackBase):
    pass

class StackResponse(StackBase):
    id: int
    fecha_creacion: datetime
    # Reutilizamos tu súper esquema de productos para devolver los botes dentro del Stack
    productos: List[ProductResponse] = []

    model_config = ConfigDict(from_attributes=True)