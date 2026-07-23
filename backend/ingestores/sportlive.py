import sys
import os
# Esto le dice a Python: "Oye, busca también en la carpeta que está justo por encima de mí"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import zipfile
import io
import json
import re
import unicodedata

# Ahora ya podemos importar los archivos de la carpeta backend sin que dé error
import models
from database import SessionLocal
from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum,
    CategoriaEnum, normalizar_marca
)

# ... (El resto de tu código se queda exactamente igual) ...

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

def calcular_metricas_precio(item: dict, precio: float):
    # Ahora recibimos el diccionario completo del producto
    nombre = item.get('name', '').lower()
    peso_json = str(item.get('weight', '')).lower() # <-- Cazamos la columna oculta
    
    metricas = {
        "peso_gramos": None,
        "precio_por_kg": None,
        "unidades": None,
        "precio_por_unidad": None
    }
    
    # ---------------------------------------------------------
    # 1. BÚSQUEDA DE PESO (Sistema en Cascada)
    # ---------------------------------------------------------
    # Primero buscamos en la columna oficial del JSON. Si falla, miramos en el título.
    textos_donde_buscar = [peso_json, nombre]
    
    for texto in textos_donde_buscar:
        if not texto: 
            continue
            
        match_peso = re.search(r'(\d+(?:[.,]\d+)?)\s*(kg|kilo|kilos|g|gr|gramos|lbs|lb|libra)s?\.?\b', texto)
        if match_peso:
            cantidad_cruda = match_peso.group(1).replace(',', '.')
            try:
                cantidad = float(cantidad_cruda)
                unidad = match_peso.group(2)
                
                if unidad in ['kg', 'kilo', 'kilos']:
                    peso_kg = cantidad
                    metricas["peso_gramos"] = int(cantidad * 1000)
                elif unidad in ['lbs', 'lb', 'libra']:
                    peso_kg = cantidad * 0.453592
                    metricas["peso_gramos"] = int(peso_kg * 1000)
                else: 
                    peso_kg = cantidad / 1000
                    metricas["peso_gramos"] = int(cantidad)
                    
                if precio and precio > 0 and peso_kg > 0:
                    metricas["precio_por_kg"] = round(precio / peso_kg, 2)
                
                # Si hemos encontrado el peso, rompemos el bucle (no hace falta mirar el título)
                break 
                
            except ValueError:
                pass
            
    return metricas


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

# 2. CATEGORÍA ESTRICTA (JERARQUÍA DEL TÍTULO ABSOLUTA)
    if any(p in n for p in ["crema", "harina", "copos", "mermelada", "avena", "eritritol", "peanut"]): 
        c["categoria"] = CategoriaEnum.alimentacion.value
    elif any(p in n for p in ["gel", "electrolitos", "hidratación", "boom", "pre-entreno", "pre entreno", "hydrop"]): 
        c["categoria"] = CategoriaEnum.pre_entrenos.value
    # Hemos quitado "gainer" e "iso" (muy genérico) de aquí:
    elif any(p in n for p in ["whey", "protein", "proteína", "proteina", "isolate", "aislado"]): 
        c["categoria"] = CategoriaEnum.proteinas.value
    elif "creatin" in n: 
        c["categoria"] = CategoriaEnum.creatinas.value
    elif any(p in n for p in ["amino", "bcaa", "glutamina", "carnitina"]): 
        c["categoria"] = CategoriaEnum.aminoacidos.value
    elif any(p in n for p in ["vitamin", "mineral", "magnesio", "calcio", "zinc", "omega", "colágeno"]): 
        c["categoria"] = CategoriaEnum.vitaminas.value
    else:
        # CERO BÚSQUEDAS EN LA DESCRIPCIÓN. 
        # Si el título no nos dice la categoría claramente, va a "Otros".
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
    
    if not sabores_encontrados:
        sabores_encontrados.append(SaborEnum.neutro.value)
    c["sabor"] = sabores_encontrados # Ahora es una lista: ["Fresa", "Vainilla"]

    c["formato"] = None
    if any(p in texto_completo for p in ["cápsula", "capsula", "comprimido", "perla"]): c["formato"] = FormatoEnum.capsulas
    elif any(p in texto_completo for p in ["vial", "gel", "líquido"]): c["formato"] = FormatoEnum.liquido
    elif any(p in texto_completo for p in ["polvo", "harina"]): c["formato"] = FormatoEnum.polvo
    elif "barrita" in texto_completo: c["formato"] = FormatoEnum.barrita
    if not c["formato"]:
        # Si es Proteína o Creatina, el estándar de la industria es que sea en Polvo
        if c["categoria"] in [CategoriaEnum.proteinas.value, CategoriaEnum.creatinas.value]:
            c["formato"] = FormatoEnum.polvo.value
            
        # Si en las instrucciones dice "cazo", "dosificador", "scoop" o "mezclar en agua", es Polvo
        elif any(p in texto_completo for p in ["cazo", "cacito", "scoop", "dosificador", "mezclar", "ml de agua"]):
            c["formato"] = FormatoEnum.polvo.value


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

        metricas = calcular_metricas_precio(item, precio)
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
            
            peso_gramos=metricas["peso_gramos"],
            precio_por_kg=metricas["precio_por_kg"],

            slug=generar_slug(nombre),
        )
        productos_nuevos.append(nuevo_producto)

    db.add_all(productos_nuevos)
    db.commit()
    print(f"\n🎉 ¡Limpieza completada! {len(productos_nuevos)} productos guardados perfectamente estructurados.")

if __name__ == "__main__":
    inyectar_en_bd()