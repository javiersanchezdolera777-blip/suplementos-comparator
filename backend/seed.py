import models
from database import SessionLocal

db = SessionLocal()

print("🌱 Iniciando la siembra de productos enriquecidos...")

# 1. Función auxiliar para crear marcas y categorías si no existen
def get_or_create_marca(nombre):
    marca = db.query(models.Marca).filter_by(nombre=nombre).first()
    if not marca:
        marca = models.Marca(nombre=nombre)
        db.add(marca)
        db.commit()
        db.refresh(marca)
    return marca

def get_or_create_categoria(nombre):
    cat = db.query(models.Categoria).filter_by(nombre=nombre).first()
    if not cat:
        cat = models.Categoria(nombre=nombre)
        db.add(cat)
        db.commit()
        db.refresh(cat)
    return cat

# 2. Preparamos las Marcas y Categorías
cat_prot = get_or_create_categoria("Proteínas")
cat_crea = get_or_create_categoria("Creatinas")
cat_amino = get_or_create_categoria("Aminoácidos")
cat_vit = get_or_create_categoria("Vitaminas")

marca_hsn = get_or_create_marca("HSN")
marca_bulk = get_or_create_marca("Bulk")
marca_mypro = get_or_create_marca("MyProtein")
marca_optimum = get_or_create_marca("Optimum Nutrition")

# 3. Limpiamos SOLO los productos antiguos para no tener duplicados
db.query(models.Producto).delete()
db.commit()

# 4. Creamos los productos "Vitamínados" con los nuevos sub-filtros
productos = [
    models.Producto(
        nombre="100% Whey Gold Standard",
        descripcion="Proteína aislada de suero de leche de alta calidad, referencia mundial.",
        precio=59.99,
        imagen_url="https://ejemplo.com/gold_standard.jpg",
        categoria_id=cat_prot.id,
        marca_id=marca_optimum.id,
        objetivo="Volumen Muscular",
        sabor="Chocolate",
        formato="Polvo",
        es_vegano=False,
        sello_calidad="Optipep",
        tipo_proteina="Isolate (Aislado)",
        porcentaje_proteina=90
    ),
    models.Producto(
        nombre="Vegan Protein Blend",
        descripcion="Mezcla de proteínas de guisante y arroz integral.",
        precio=34.50,
        imagen_url="https://ejemplo.com/vegan_mypro.jpg",
        categoria_id=cat_prot.id,
        marca_id=marca_mypro.id,
        objetivo="Pérdida de Peso",
        sabor="Vainilla",
        formato="Polvo",
        es_vegano=True,
        tipo_proteina="Vegetal",
        porcentaje_proteina=78
    ),
    models.Producto(
        nombre="Creatina Monohidrato Excel",
        descripcion="Creatina ultra pura con sello oficial.",
        precio=24.90,
        imagen_url="https://ejemplo.com/creatina_hsn.jpg",
        categoria_id=cat_crea.id,
        marca_id=marca_hsn.id,
        objetivo="Rendimiento Deportivo",
        sabor="Sin sabor",
        formato="Polvo",
        es_vegano=True,
        sello_calidad="Creapure",
        tipo_creatina="Monohidrato"
    ),
    models.Producto(
        nombre="BCAA 2:1:1 Elite Quality",
        descripcion="Aminoácidos ramificados para recuperación muscular.",
        precio=19.99,
        imagen_url="https://ejemplo.com/bcaa.jpg",
        categoria_id=cat_amino.id,
        marca_id=marca_bulk.id,
        objetivo="Rendimiento Deportivo",
        sabor="Limón",
        formato="Polvo",
        es_vegano=True,
        sello_calidad="Kyowa",
        perfil_aminoacidos="BCAA"
    ),
    models.Producto(
        nombre="Daily Multivitamin",
        descripcion="Complejo vitamínico con minerales esenciales.",
        precio=12.50,
        imagen_url="https://ejemplo.com/vit.jpg",
        categoria_id=cat_vit.id,
        marca_id=marca_hsn.id,
        objetivo="Salud y Bienestar",
        sabor="Sin sabor",
        formato="Cápsulas",
        es_vegano=False,
        tipo_vitamina="Multivitamínico"
    )
]

db.add_all(productos)
db.commit()

print("✅ ¡Éxito! 5 productos con súper-filtros inyectados en la base de datos.")