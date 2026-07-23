import requests
import zipfile
import io
import json
import os
import re
import unicodedata
import models
from database import SessionLocal

# Importamos nuestras reglas maestras desde schemas.py
from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum,
    CategoriaEnum, normalizar_marca
)

URL_FEED = "https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=108208?token=D496D89D3425492898437BED5EE5EEB677232059"
ARCHIVO_CACHE = "feed_temporal.json"
DOMINIO_TIENDA = "https://sportlivenutrition.com"

db = SessionLocal()

def descargar_datos():
    if os.path.exists(ARCHIVO_CACHE):
        with open(ARCHIVO_CACHE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    response = requests.get(URL_FEED, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            datos_json = json.load(z.open(z.namelist()[0]))
    except:
        datos_json = response.json()
        
    with open(ARCHIVO_CACHE, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=4)
    return datos_json

# --- MATEMÁTICAS Y LIMPIEZA ---
def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    if "una combinación ganadora" in texto:
        return texto[:texto.find("una combinación ganadora")]
    return texto

def generar_slug(nombre: str) -> str:
    texto = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

def extraer_peso_gramos(nombre: str, desc: str):
    m_g = re.search(r'(\d+(?:[.,]\d+)?)\s*g\b', nombre.lower())
    if m_g: return int(float(m_g.group(1).replace(',', '.')))
    m_kg = re.search(r'(\d+(?:[.,]\d+)?)\s*kg\b', nombre.lower())
    if m_kg: return int(float(m_kg.group(1).replace(',', '.')) * 1000)
    
    m_kg_desc = re.search(r'(\d+(?:[.,]\d+)?)\s*kg\b', desc)
    if m_kg_desc: return int(float(m_kg_desc.group(1).replace(',', '.')) * 1000)
    m_g_desc = re.search(r'\b(\d{3,4})\s*g\b', desc) 
    if m_g_desc: return int(m_g_desc.group(1))
    return None

def extraer_porcentaje_proteina(texto: str):
    m = re.search(r'(\d{2,3})\s*%\s*(?:de\s*)?(?:prote[íi]na|pureza)', texto)
    if m: return int(m.group(1))
    m2 = re.search(r'prote[íi]na[^\d]{0,20}(\d{2,3})\s*%', texto)
    if m2: return int(m2.group(1))
    return None

# --- EL CEREBRO DE CLASIFICACIÓN (JERÁRQUICO Y MULTISABOR) ---
def clasificar_producto(nombre: str, desc_limpia: str):
    n = nombre.lower()
    texto_completo = n + " " + desc_limpia.lower()
    c = {}
    
    # 1. FILTRO DE BASURA (Solo mira el nombre)
    if any(p in n for p in ["shaker", "mezclador", "botella", "toalla", "camiseta"]):
        return None

    # 2. CATEGORÍA ESTRICTA (JERARQUÍA DEL TÍTULO)
    if any(p in n for p in ["crema", "harina", "copos", "mermelada", "avena", "eritritol", "peanut"]): 
        c["categoria"] = CategoriaEnum.alimentacion.value
    elif any(p in n for p in ["gel", "electrolitos", "hidratación", "boom", "pre-entreno", "pre entreno", "hydrop"]): 
        c["categoria"] = CategoriaEnum.pre_entrenos.value
    elif any(p in n for p in ["whey", "protein", "gainer", "proteína", "proteina", "iso"]): 
        c["categoria"] = CategoriaEnum.proteinas.value
    elif "creatin" in n: 
        c["categoria"] = CategoriaEnum.creatinas.value
    elif any(p in n for p in ["amino", "bcaa", "glutamina", "carnitina"]): 
        c["categoria"] = CategoriaEnum.aminoacidos.value
    elif any(p in n for p in ["vitamin", "mineral", "magnesio", "calcio", "zinc", "omega", "colágeno"]): 
        c["categoria"] = CategoriaEnum.vitaminas.value
    else:
        # Último recurso: si el título no dice nada claro, miramos la descripción
        if "proteína" in desc_limpia.lower() or "protein" in desc_limpia.lower():
            c["categoria"] = CategoriaEnum.proteinas.value
        else:
            c["categoria"] = CategoriaEnum.otros.value 

    # 3. FILTROS GLOBALES (Mirando texto completo)
    c["es_vegano"] = True if any(p in texto_completo for p in ["apto para veganos", "proteína vegana", "vegan protein"]) else False

    # --- NUEVO SISTEMA: MÚLTIPLES SABORES ---
    sabores_encontrados = []
    if "vainilla" in texto_completo: sabores_encontrados.append(SaborEnum.vainilla.value)
    if any(p in texto_completo for p in ["chocolate", "cacao", "brownie"]): sabores_encontrados.append(SaborEnum.chocolate.value)
    if "fresa" in texto_completo: sabores_encontrados.append(SaborEnum.fresa.value)
    if any(p in texto_completo for p in ["limon", "limón", "citric"]): sabores_encontrados.append(SaborEnum.limon.value)
    if "cookies" in texto_completo or "cream" in texto_completo: sabores_encontrados.append(SaborEnum.cookies.value)
    if "plátano" in texto_completo or "banana" in texto_completo: sabores_encontrados.append(SaborEnum.platano.value)
    if "café" in texto_completo or "capuchino" in texto_completo: sabores_encontrados.append(SaborEnum.cafe.value)
    if "frutas del bosque" in texto_completo or "berry" in texto_completo: sabores_encontrados.append(SaborEnum.frutas.value)
    
    if not sabores_encontrados and ("neutro" in texto_completo or "sin sabor" in texto_completo):
        sabores_encontrados.append(SaborEnum.neutro.value)
        
    c["sabor"] = sabores_encontrados # Ahora es una lista: ["Fresa", "Vainilla"]

    c["formato"] = None
    if any(p in texto_completo for p in ["cápsula", "capsula", "comprimido", "perla"]): c["formato"] = FormatoEnum.capsulas
    elif any(p in texto_completo for p in ["vial", "gel", "líquido"]): c["formato"] = FormatoEnum.liquido
    elif any(p in texto_completo for p in ["polvo", "harina"]): c["formato"] = FormatoEnum.polvo
    elif "barrita" in texto_completo: c["formato"] = FormatoEnum.barrita

    c["objetivo"] = None
    if "gainer" in texto_completo or "volumen" in texto_completo: c["objetivo"] = ObjetivoEnum.volumen
    elif "peso" in texto_completo or "termogen" in texto_completo or "quema" in texto_completo: c["objetivo"] = ObjetivoEnum.definicion
    elif "rendimiento" in texto_completo: c["objetivo"] = ObjetivoEnum.rendimiento
    elif "salud" in texto_completo or "articular" in texto_completo or "omega" in texto_completo: c["objetivo"] = ObjetivoEnum.salud

    c["sello_calidad"] = None
    if "creapure" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.creapure
    elif "kyowa" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.kyowa
    elif "lacprodan" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.lacprodan
    elif "isolac" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.isolac

    # 4. SUBFILTROS ESPECÍFICOS
    c["tipo_proteina"] = c["porcentaje_proteina"] = c["tipo_creatina"] = c["perfil_aminoacidos"] = c["tipo_vitamina"] = None
    
    if c["categoria"] == CategoriaEnum.proteinas.value:
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto_completo)
        if "isolate" in texto_completo or "aislado" in texto_completo: c["tipo_proteina"] = TipoProteinaEnum.isolate
        elif "vegetal" in texto_completo or "vegan" in texto_completo: c["tipo_proteina"] = TipoProteinaEnum.vegetal
        elif "caseina" in texto_completo or "casein" in texto_completo: c["tipo_proteina"] = TipoProteinaEnum.caseina
        elif "hidrolizado" in texto_completo: c["tipo_proteina"] = TipoProteinaEnum.hidrolizado
        else: c["tipo_proteina"] = TipoProteinaEnum.whey
        
    elif c["categoria"] == CategoriaEnum.creatinas.value:
        if "micronizada" in texto_completo or "mesh" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.micronizada
        elif "hcl" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.hcl
        elif "kre-alkalyn" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.kre_alkalyn
        else: c["tipo_creatina"] = TipoCreatinaEnum.monohidrato
        
    elif c["categoria"] == CategoriaEnum.aminoacidos.value:
        if "bcaa" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa
        elif "glutamina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina
        elif "eaa" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.eaa
        elif "citrulina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.citrulina
        elif "alanina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.beta_alanina

    elif c["categoria"] == CategoriaEnum.vitaminas.value:
        if "multivitam" in texto_completo or "complex" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.multivitaminico
        elif "vitamina c" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_c
        elif "vitamina d" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_d
        elif "magnesio" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.magnesio
        elif "omega" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.omega3

    return c

# --- RUTINA DE INYECCIÓN ---
def inyectar_en_bd():
    print("🔄 Vaciando datos antiguos (por si acaso)...")
    db.query(models.Producto).delete()
    db.query(models.Categoria).delete()
    db.commit()

    # CREAMOS LAS CATEGORÍAS DESDE EL ENUM DE SCHEMAS
    mapa_categorias = {}
    for cat in CategoriaEnum:
        nueva_cat = models.Categoria(nombre=cat.value)
        db.add(nueva_cat)
        db.commit()
        db.refresh(nueva_cat)
        mapa_categorias[cat.value] = nueva_cat.id

    # CREAMOS LA MARCA NORMALIZADA
    nombre_marca = normalizar_marca("Sport Live")
    marca_oficial = db.query(models.Marca).filter_by(nombre=nombre_marca).first()
    if not marca_oficial:
        marca_oficial = models.Marca(nombre=nombre_marca)
        db.add(marca_oficial)
        db.commit()

    # INGESTAMOS PRODUCTOS
    datos = descargar_datos()
    productos_nuevos = []
    
    for item in datos.get('products', []):
        nombre = item.get('name', 'Sin nombre')
        desc_limpia = limpiar_texto(item.get('description', ''))
        
        etiquetas = clasificar_producto(nombre, desc_limpia)
        if not etiquetas:
            print(f"⏭️  Ignorando producto no deseado: {nombre}")
            continue

        precio = 0.0
        afiliado_url = ""
        ofertas = item.get("offers", [])
        if ofertas:
            afiliado_url = ofertas[0].get("productUrl", "")
            historial = ofertas[0].get("priceHistory", [])
            if historial and "price" in historial[0]:
                precio = float(historial[0]["price"].get("value", 0))

        img = item.get("productImage", {}).get("url", "")
        imagen_url = f"{DOMINIO_TIENDA}{img}" if img else ""

        peso_gramos = extraer_peso_gramos(nombre, desc_limpia)
        precio_por_kg = round((precio / peso_gramos) * 1000, 2) if (precio and peso_gramos and peso_gramos > 0) else None

        nuevo_producto = models.Producto(
            nombre=nombre,
            descripcion=desc_limpia[:900], 
            precio=precio,
            imagen_url=imagen_url,
            afiliado_url=afiliado_url,
            marca_id=marca_oficial.id,
            categoria_id=mapa_categorias[etiquetas["categoria"]],
            
            sabor=etiquetas["sabor"], # <-- Ahora guarda una lista
            formato=etiquetas["formato"],
            objetivo=etiquetas["objetivo"],
            es_vegano=etiquetas["es_vegano"],
            sello_calidad=etiquetas["sello_calidad"],
            
            tipo_proteina=etiquetas["tipo_proteina"],
            porcentaje_proteina=etiquetas["porcentaje_proteina"],
            tipo_creatina=etiquetas["tipo_creatina"],
            perfil_aminoacidos=etiquetas["perfil_aminoacidos"],
            tipo_vitamina=etiquetas["tipo_vitamina"],
            
            slug=generar_slug(nombre),
            peso_gramos=peso_gramos,
            precio_por_kg=precio_por_kg
        )
        productos_nuevos.append(nuevo_producto)

    db.add_all(productos_nuevos)
    db.commit()
    print(f"\n🎉 ¡Limpieza completada! {len(productos_nuevos)} productos guardados perfectamente estructurados.")

if __name__ == "__main__":
    inyectar_en_bd()