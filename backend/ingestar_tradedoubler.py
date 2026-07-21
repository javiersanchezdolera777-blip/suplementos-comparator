import requests
import zipfile
import gzip
import io
import json
import os
import models
from database import SessionLocal
from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum
)

URL_FEED = "PON_AQUI_TU_URL_DE_TRADEDOUBLER"
ARCHIVO_CACHE = "feed_temporal.json"
DOMINIO_TIENDA = "https://sportlivenutrition.com"

db = SessionLocal()

def obtener_datos_feed(feed_url: str):
    if os.path.exists(ARCHIVO_CACHE):
        print(f"📦 Leyendo datos desde el caché local...")
        with open(ARCHIVO_CACHE, 'r', encoding='utf-8') as f:
            return json.load(f)

    print("🌐 Descargando datos desde Tradedoubler...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(feed_url, headers=headers)
    response.raise_for_status()

    datos_json = None
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            datos_json = json.load(z.open(z.namelist()[0]))
    except:
        try:
            datos_json = json.loads(gzip.decompress(response.content).decode('utf-8'))
        except:
            datos_json = response.json()

    with open(ARCHIVO_CACHE, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=4)
    return datos_json

# ==========================================
# 🧠 EL SÚPER-CEREBRO CLASIFICADOR
# ==========================================
def clasificar_producto(nombre: str, descripcion: str, categoria_original: str, db: SessionLocal):
    texto = (nombre + " " + descripcion + " " + categoria_original).lower()
    
    c = {
        "es_vegano": False, "sabor": None, "formato": None, "objetivo": None,
        "sello_calidad": None, "tipo_proteina": None, "tipo_creatina": None,
        "perfil_aminoacidos": None, "tipo_vitamina": None, "categoria_id": None
    }
    
    # --- 1. VEGANO ---
    if any(p in texto for p in ["vegan", "vegetal", "guisante"]):
        c["es_vegano"] = True
        
    # --- 2. SABOR ---
    if "vainilla" in texto or "vanilla" in texto: c["sabor"] = SaborEnum.vainilla
    elif "chocolate" in texto or "cacao" in texto or "brownie" in texto: c["sabor"] = SaborEnum.chocolate
    elif "fresa" in texto or "strawberry" in texto: c["sabor"] = SaborEnum.fresa
    elif "limon" in texto or "limón" in texto: c["sabor"] = SaborEnum.limon
    elif "frutas" in texto or "bosque" in texto: c["sabor"] = SaborEnum.frutas
    elif "neutro" in texto: c["sabor"] = SaborEnum.neutro

    # --- 3. FORMATO ---
    if "cápsula" in texto or "capsula" in texto or "comprimido" in texto: c["formato"] = FormatoEnum.capsulas
    elif "vial" in texto or "gel" in texto or "líquido" in texto: c["formato"] = FormatoEnum.liquido
    elif "barrita" in texto: c["formato"] = FormatoEnum.barrita
    elif "polvo" in texto or "harina" in texto: c["formato"] = FormatoEnum.polvo

    # --- 4. OBJETIVO ---
    if "gainer" in texto or "volumen" in texto: c["objetivo"] = ObjetivoEnum.volumen
    elif "peso" in texto or "termogen" in texto or "quema" in texto or "cla" in texto: c["objetivo"] = ObjetivoEnum.definicion
    elif "salud" in texto or "articular" in texto or "omega" in texto or "colágeno" in texto: c["objetivo"] = ObjetivoEnum.salud
    elif "rendimiento" in texto or "pre-entreno" in texto or "energ" in texto: c["objetivo"] = ObjetivoEnum.rendimiento

    # --- 5. SELLO CALIDAD ---
    if "creapure" in texto: c["sello_calidad"] = SelloCalidadEnum.creapure
    elif "kyowa" in texto: c["sello_calidad"] = SelloCalidadEnum.kyowa

    # --- 6. SUB-FILTROS ---
    if "isolate" in texto or "aislado" in texto: c["tipo_proteina"] = TipoProteinaEnum.isolate
    elif "whey" in texto or "concentrad" in texto: c["tipo_proteina"] = TipoProteinaEnum.whey
    
    if "mesh" in texto or "micronizada" in texto: c["tipo_creatina"] = TipoCreatinaEnum.micronizada
    elif "creatina" in texto: c["tipo_creatina"] = TipoCreatinaEnum.monohidrato
    
    if "bcaa" in texto: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa
    elif "glutamina" in texto: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina
    
    if "multivitam" in texto or "complex" in texto: c["tipo_vitamina"] = TipoVitaminaEnum.multivitaminico
    elif "vitamina c" in texto: c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_c
    elif "vitamina d" in texto: c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_d
    elif "magnesio" in texto: c["tipo_vitamina"] = TipoVitaminaEnum.magnesio
    elif "omega" in texto: c["tipo_vitamina"] = TipoVitaminaEnum.omega3

    # --- 7. CATEGORÍA PRINCIPAL EN BASE DE DATOS ---
    if "protein" in texto or "whey" in texto: nombre_cat = "Proteínas"
    elif "creatin" in texto: nombre_cat = "Creatinas"
    elif "amino" in texto or "bcaa" in texto or "glutamina" in texto: nombre_cat = "Aminoácidos"
    elif "vitamin" in texto or "mineral" in texto or "magnesio" in texto: nombre_cat = "Vitaminas"
    elif "pre-entreno" in texto or "gel" in texto: nombre_cat = "Pre-Entrenos"
    else: nombre_cat = "Salud y Bienestar"

    cat_db = db.query(models.Categoria).filter_by(nombre=nombre_cat).first()
    if cat_db: c["categoria_id"] = cat_db.id

    return c

# ==========================================
# 3. LÓGICA DE INGESTA
# ==========================================
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
        descripcion = item.get('description', '')
        
        # 1. Extracción con Ingeniería Inversa
        precio = 0.0
        afiliado_url = ""
        ofertas = item.get("offers", [])
        if ofertas:
            afiliado_url = ofertas[0].get("productUrl", "")
            historial = ofertas[0].get("priceHistory", [])
            if historial and "price" in historial[0]:
                precio = float(historial[0]["price"].get("value", 0))

        # 2. Arreglar la URL de la imagen
        imagen_relativa = item.get("productImage", {}).get("url", "")
        imagen_url = f"{DOMINIO_TIENDA}{imagen_relativa}" if imagen_relativa else ""
        
        categoria_original = item.get("categories", [{}])[0].get("tdCategoryName", "")

        # 3. Llamar al cerebro
        etiquetas = clasificar_producto(nombre, descripcion, categoria_original, db)

        nuevo_producto = models.Producto(
            nombre=nombre,
            descripcion=descripcion[:900], 
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
            tipo_vitamina=etiquetas["tipo_vitamina"]
        )
        productos_nuevos.append(nuevo_producto)

    db.add_all(productos_nuevos)
    db.commit()
    print(f"🎉 ¡Éxito! {len(productos_nuevos)} productos inyectados con precios, imágenes y mega-filtros.")

if __name__ == "__main__":
    inyectar_en_bd()