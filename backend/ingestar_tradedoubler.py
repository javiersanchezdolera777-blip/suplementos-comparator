import requests
import zipfile
import gzip
import io
import json
import os
import re
import unicodedata
import models
from database import SessionLocal
from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum
)

URL_FEED = "https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=108208?token=D496D89D3425492898437BED5EE5EEB677232059"
ARCHIVO_CACHE = "feed_temporal.json"
DOMINIO_TIENDA = "https://sportlivenutrition.com"

db = SessionLocal()

def obtener_datos_feed(feed_url: str):
    if os.path.exists(ARCHIVO_CACHE):
        with open(ARCHIVO_CACHE, 'r', encoding='utf-8') as f:
            return json.load(f)

    response = requests.get(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            datos_json = json.load(z.open(z.namelist()[0]))
    except:
        datos_json = response.json()
    with open(ARCHIVO_CACHE, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=4)
    return datos_json

def limpiar_descripcion(desc: str) -> str:
    desc_baja = desc.lower()
    if "una combinación ganadora" in desc_baja:
        return desc[:desc_baja.find("una combinación ganadora")]
    return desc

def generar_slug(nombre: str) -> str:
    texto = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

def extraer_peso_gramos(nombre: str, descripcion: str):
    # Busca gramos/kg en el NOMBRE primero (ej: "Crema de cacahuete 350 g")
    match_g_nombre = re.search(r'(\d+(?:[.,]\d+)?)\s*g\b', nombre.lower())
    if match_g_nombre: return int(float(match_g_nombre.group(1).replace(',', '.')))
    
    match_kg_nombre = re.search(r'(\d+(?:[.,]\d+)?)\s*kg\b', nombre.lower())
    if match_kg_nombre: return int(float(match_kg_nombre.group(1).replace(',', '.')) * 1000)

    # Si no, busca en la descripción SOLO KILOS para evitar el "27g por cazo"
    match_kg_desc = re.search(r'(\d+(?:[.,]\d+)?)\s*kg\b', descripcion.lower())
    if match_kg_desc: return int(float(match_kg_desc.group(1).replace(',', '.')) * 1000)
    
    return None

def extraer_porcentaje_proteina(texto: str):
    match1 = re.search(r'(\d{2,3})\s*%\s*(?:de\s*)?prote[íi]na', texto)
    if match1: return int(match1.group(1))
    match2 = re.search(r'prote[íi]na[^\d]{0,20}(\d{2,3})\s*%', texto)
    if match2: return int(match2.group(1))
    match3 = re.search(r'(\d{2,3})\s*%\s*(?:de\s*)?pureza', texto)
    if match3: return int(match3.group(1))
    return None

# 🧠 SISTEMA DE CATEGORÍAS MEJORADO
def detectar_categoria_principal(nombre: str) -> str:
    n = nombre.lower()
    if "shaker" in n or "mezclador" in n: return "Accesorios"
    if any(p in n for p in ["crema", "harina", "copos", "mermelada", "avena", "eritritol"]): return "Alimentación Saludable"
    if "whey" in n or "protein" in n or "gainer" in n: return "Proteínas"
    if "creatina" in n or "creatine" in n: return "Creatinas"
    if any(p in n for p in ["amino", "bcaa", "glutamina", "carnitina"]): return "Aminoácidos"
    if any(p in n for p in ["vitamin", "mineral", "magnesio", "calcio", "zinc", "omega"]): return "Vitaminas"
    if "pre-entreno" in n or "boom" in n: return "Pre-Entrenos"
    if "gel " in n or "electrolitos" in n or "hidratación" in n: return "Salud y Bienestar"
    return "Otros"

def clasificar_producto(nombre: str, descripcion_limpia: str, db: SessionLocal):
    texto = (nombre + " " + descripcion_limpia).lower()
    
    c = {
        "es_vegano": False, "sabor": None, "formato": None, "objetivo": None,
        "sello_calidad": None, "tipo_proteina": None, "tipo_creatina": None,
        "perfil_aminoacidos": None, "tipo_vitamina": None, "categoria_id": None,
        "peso_gramos": extraer_peso_gramos(nombre, descripcion_limpia),
        "porcentaje_proteina": None
    }
    
    if "apto para veganos" in texto or "proteína vegana" in texto or "vegan protein" in texto: c["es_vegano"] = True
        
    # --- SABOR INTELIGENTE (Detecta raíces, abreviaturas e Inglés/Español) ---
    if any(p in texto for p in ["vainilla", "vanilla"]): 
        c["sabor"] = SaborEnum.vainilla
    elif any(p in texto for p in ["chocolate", "choco", "cacao", "brownie", "cocoa"]): 
        c["sabor"] = SaborEnum.chocolate
    elif any(p in texto for p in ["fresa", "strawberry", "yogur - fresa", "fresa - nata"]): 
        c["sabor"] = SaborEnum.fresa
    elif any(p in texto for p in ["limon", "limón", "citric", "lemon"]): 
        c["sabor"] = SaborEnum.limon
    elif any(p in texto for p in ["cookies", "cookie", "cream", "galleta"]): 
        c["sabor"] = SaborEnum.cookies
    elif any(p in texto for p in ["platano", "plátano", "banana"]): 
        c["sabor"] = SaborEnum.platano
    elif any(p in texto for p in ["cafe", "café", "capuchino", "cappuccino", "coffee"]): 
        c["sabor"] = SaborEnum.cafe
    elif any(p in texto for p in ["frutas del bosque", "bosque", "berry", "red berries"]): 
        c["sabor"] = SaborEnum.frutas
    elif any(p in texto for p in ["neutro", "sin sabor", "natural"]): 
        c["sabor"] = SaborEnum.neutro
    if "cápsula" in texto or "capsula" in texto: c["formato"] = FormatoEnum.capsulas
    elif "vial" in texto or "gel" in texto or "líquido" in texto: c["formato"] = FormatoEnum.liquido
    elif "polvo" in texto or "harina" in texto: c["formato"] = FormatoEnum.polvo

    if "gainer" in texto or "volumen" in texto: c["objetivo"] = ObjetivoEnum.volumen
    elif "peso" in texto or "termogen" in texto or "quema" in texto: c["objetivo"] = ObjetivoEnum.definicion
    elif "salud" in texto or "articular" in texto or "omega" in texto: c["objetivo"] = ObjetivoEnum.salud

    if "creapure" in texto: c["sello_calidad"] = SelloCalidadEnum.creapure
    if "kyowa" in texto: c["sello_calidad"] = SelloCalidadEnum.kyowa

    if "isolate" in texto or "aislado" in texto: c["tipo_proteina"] = TipoProteinaEnum.isolate
    elif "whey" in texto or "concentrad" in texto: c["tipo_proteina"] = TipoProteinaEnum.whey
    
    if "creatina" in texto: c["tipo_creatina"] = TipoCreatinaEnum.monohidrato
    if "bcaa" in texto: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa
    if "glutamina" in texto: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina
    if "multivitam" in texto: c["tipo_vitamina"] = TipoVitaminaEnum.multivitaminico

    # CREACIÓN AUTOMÁTICA DE CATEGORÍAS
    nombre_cat = detectar_categoria_principal(nombre)
    cat_db = db.query(models.Categoria).filter_by(nombre=nombre_cat).first()
    if not cat_db:
        cat_db = models.Categoria(nombre=nombre_cat)
        db.add(cat_db)
        db.commit()
        db.refresh(cat_db)
        
    c["categoria_id"] = cat_db.id
    
    if nombre_cat == "Proteínas":
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto)

    return c

def inyectar_en_bd():
    data = obtener_datos_feed(URL_FEED)
    productos_feed = data.get('products', [])

    print("Limpiando catálogo antiguo...")
    db.query(models.Producto).delete()
    db.commit()

    marca_default = db.query(models.Marca).filter_by(nombre="Sport Live").first()
    if not marca_default:
        marca_default = models.Marca(nombre="Sport Live")
        db.add(marca_default)
        db.commit()

    productos_nuevos = []
    
    for item in productos_feed:
        nombre = item.get('name', 'Sin nombre')
        descripcion_limpia = limpiar_descripcion(item.get('description', ''))
        
        precio = 0.0
        afiliado_url = ""
        ofertas = item.get("offers", [])
        if ofertas:
            afiliado_url = ofertas[0].get("productUrl", "")
            historial = ofertas[0].get("priceHistory", [])
            if historial and "price" in historial[0]:
                precio = float(historial[0]["price"].get("value", 0))

        imagen_relativa = item.get("productImage", {}).get("url", "")
        imagen_url = f"{DOMINIO_TIENDA}{imagen_relativa}" if imagen_relativa else ""

        etiquetas = clasificar_producto(nombre, descripcion_limpia, db)
        
        # 🧮 CÁLCULO DEL PRECIO POR KILO ANTES DE GUARDAR
        peso = etiquetas["peso_gramos"]
        precio_kg = None
        if precio and peso and peso > 0:
            precio_kg = round((precio / peso) * 1000, 2)

        nuevo_producto = models.Producto(
            nombre=nombre,
            descripcion=descripcion_limpia[:900], 
            precio=precio,
            imagen_url=imagen_url,
            afiliado_url=afiliado_url,
            marca_id=marca_default.id,
            categoria_id=etiquetas["categoria_id"],
            sabor=etiquetas["sabor"],
            formato=etiquetas["formato"],
            objetivo=etiquetas["objetivo"],
            es_vegano=etiquetas["es_vegano"],
            sello_calidad=etiquetas["sello_calidad"],
            tipo_proteina=etiquetas["tipo_proteina"],
            tipo_creatina=etiquetas["tipo_creatina"],
            perfil_aminoacidos=etiquetas["perfil_aminoacidos"],
            tipo_vitamina=etiquetas["tipo_vitamina"],
            slug=generar_slug(nombre),
            peso_gramos=peso,
            porcentaje_proteina=etiquetas["porcentaje_proteina"],
            precio_por_kg=precio_kg  # <-- Dato real guardado
        )
        productos_nuevos.append(nuevo_producto)

    db.add_all(productos_nuevos)
    db.commit()
    print(f"🎉 ¡Éxito! {len(productos_nuevos)} productos inyectados.")

if __name__ == "__main__":
    inyectar_en_bd()