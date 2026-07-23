import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import zipfile
import gzip
import io
import json
import re
import unicodedata
import models
from database import SessionLocal

from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum,
    CategoriaEnum, normalizar_marca
)

URL_FEED = "https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=256625?token=D496D89D3425492898437BED5EE5EEB677232059"
ARCHIVO_CACHE = "farma2go_temporal.json"

db = SessionLocal()

def descargar_datos():
    if os.path.exists(ARCHIVO_CACHE):
        print("📦 Leyendo datos desde la caché local...")
        with open(ARCHIVO_CACHE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    print("🌐 Descargando catálogo desde Tradedoubler...")
    response = requests.get(URL_FEED, headers={'User-Agent': 'Mozilla/5.0'})
    
    if response.status_code != 200:
        print(f"🛑 Error HTTP: {response.status_code}")
        sys.exit(1)

    try:
        datos_descomprimidos = gzip.decompress(response.content)
        datos_json = json.loads(datos_descomprimidos)
    except OSError:
        try:
            datos_json = response.json()
        except Exception:
            print("🛑 Error: El archivo no es GZIP ni JSON válido.")
            sys.exit(1)
            
    with open(ARCHIVO_CACHE, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=4)
        
    return datos_json

def limpiar_texto(texto: str) -> str:
    if not texto: return ""
    return texto.lower()

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

def clasificar_producto(nombre: str, desc_limpia: str):
    n = nombre.lower()
    texto_completo = n + " " + desc_limpia.lower()
    c = {}
    
    # 1. FILTRO DE BASURA EXTREMO (A prueba de Farmacias)
    basura = [
        "shaker", "mezclador", "toalla", "facial", "corporal", "champú", "champu",
        "dientes", "dental", "serum", "cosmética", "cosmetica", "higiene", "pañal", 
        "solar", "maquillaje", "mascarilla", "pelo", "cabello", "limpiador", "kit", "gel de", "gel", "crema de", "crema", "loción", "locion", "bálsamo", "balsamo",
        "ducha", "baño", "hidratante", "antiarrugas", "antiedad", "colutorio", "vial","viales", "ampolla", "ampollas", "spray", "nasal", "ocular", "gotas", "colirio", "crema hidratante",
        "spray", "nasal", "ocular", "gotas", "colirio", "crema hidratante",
        "loción", "pomada", "bálsamo", "gel de", "íntimo", "bebé", "infantil",
        "chupete", "biberón", "ortopedia", "muñequera", "rodillera", "termómetro",
        "tiritas", "apósito", "venda", "alcohol", "agua micelar", "desmaquillante"
    ]
    if any(p in n for p in basura):
        return None

    # 2. CATEGORÍA ESTRICTA
    if any(p in n for p in ["harina", "copos", "mermelada", "avena", "eritritol", "peanut", "crema de cacahuete", "crema de arroz"]): 
        c["categoria"] = CategoriaEnum.alimentacion.value
    elif any(p in n for p in ["gel energético", "electrolitos", "hidratación", "pre-entreno", "pre entreno", "isotónico"]): 
        c["categoria"] = CategoriaEnum.pre_entrenos.value
    elif any(p in n for p in ["whey", "protein", "proteína", "proteina", "isolate", "aislado"]): 
        c["categoria"] = CategoriaEnum.proteinas.value
    elif "creatin" in n: 
        c["categoria"] = CategoriaEnum.creatinas.value
    elif any(p in n for p in ["amino", "bcaa", "glutamina", "carnitina"]): 
        c["categoria"] = CategoriaEnum.aminoacidos.value
    elif any(p in n for p in ["vitamin", "mineral", "magnesio", "calcio", "zinc", "omega", "colágeno"]): 
        c["categoria"] = CategoriaEnum.vitaminas.value
    else:
        return None 

    # 3. FILTROS GLOBALES
    c["es_vegano"] = True if any(p in texto_completo for p in ["apto para veganos", "proteína vegana", "vegan protein"]) else False

    # FORMATO PRIMERO (Lo necesitamos para saber qué hacer con los sabores)
    c["formato"] = None
    if any(p in texto_completo for p in ["cápsula", "capsula", "comprimido", "perla", "pastilla", "tableta"]): 
        c["formato"] = FormatoEnum.capsulas.value
    elif any(p in texto_completo for p in ["polvo", "harina", "copos", "soluble", "disolución", "batido"]): 
        c["formato"] = FormatoEnum.polvo.value
    elif any(p in texto_completo for p in ["vial", "líquido", "liquid", "bebida", "ampolla"]): 
        c["formato"] = FormatoEnum.liquido.value
    elif any(p in texto_completo for p in ["barrita", "barra", "snack"]): 
        c["formato"] = FormatoEnum.barrita.value
    elif any(p in texto_completo for p in ["gominola", "gummy"]): 
        c["formato"] = FormatoEnum.gominolas.value

    if not c["formato"]:
        if c["categoria"] in [CategoriaEnum.proteinas.value, CategoriaEnum.creatinas.value]:
            c["formato"] = FormatoEnum.polvo.value
        elif any(p in texto_completo for p in ["cazo", "cacito", "scoop", "dosificador", "mezclar", "ml de agua"]):
            c["formato"] = FormatoEnum.polvo.value

    # SABORES (Ahora dependientes del formato)
    sabores_encontrados = []
    if "vainilla" in texto_completo: sabores_encontrados.append(SaborEnum.vainilla.value)
    if any(p in texto_completo for p in ["chocolate", "cacao", "brownie"]): sabores_encontrados.append(SaborEnum.chocolate.value)
    if "fresa" in texto_completo: sabores_encontrados.append(SaborEnum.fresa.value)
    if any(p in texto_completo for p in ["limon", "limón", "citric"]): sabores_encontrados.append(SaborEnum.limon.value)
    if "cookies" in texto_completo or "cream" in texto_completo: sabores_encontrados.append(SaborEnum.cookies.value)
    if "plátano" in texto_completo or "banana" in texto_completo: sabores_encontrados.append(SaborEnum.platano.value)
    if "café" in texto_completo or "capuchino" in texto_completo: sabores_encontrados.append(SaborEnum.cafe.value)
    if "frutas del bosque" in texto_completo or "berry" in texto_completo: sabores_encontrados.append(SaborEnum.frutas.value)
    
    # Solo añadimos "Neutro" (Sin sabor) si no es una pastilla/cápsula y no hemos encontrado otro sabor
    if not sabores_encontrados:
        if c["formato"] not in [FormatoEnum.capsulas.value]:
            sabores_encontrados.append(SaborEnum.neutro.value)
        
    c["sabor"] = sabores_encontrados 

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

def inyectar_en_bd():
    print("🔄 Descargando y procesando datos de Farma2Go...")
    
    mapa_categorias = {}
    for cat in CategoriaEnum:
        cat_db = db.query(models.Categoria).filter_by(nombre=cat.value).first()
        if not cat_db:
            cat_db = models.Categoria(nombre=cat.value)
            db.add(cat_db)
            db.commit()
            db.refresh(cat_db)
        mapa_categorias[cat.value] = cat_db.id

    datos = descargar_datos()
    productos_nuevos = []
    cache_marcas = {}
    
    for item in datos.get('products', []):
        nombre = item.get('name', 'Sin nombre')
        desc_limpia = limpiar_texto(item.get('description', ''))
        
        # FILTRO EXTREMO DE CATEGORÍAS JSON
        categorias_json = [c.get("name", "").lower() for c in item.get("categories", [])]
        categorias_prohibidas = [
            "cosmética", "higiene", "bebé", "ortopedia", "facial", "corporal",
            "capilar", "solar", "maternidad", "infantil", "bucal", "dental",
            "botiquín", "óptica", "sexual", "perfumería"
        ]
        if any(prohibida in cat for cat in categorias_json for prohibida in categorias_prohibidas):
            continue

        etiquetas = clasificar_producto(nombre, desc_limpia)
        if not etiquetas:
            continue

        # LIMPIEZA DE MARCA
        marca_cruda = item.get("brand", "Desconocida")
        # Si la marca es muy larga o tiene caracteres raros, la descartamos
        if len(marca_cruda) > 30 or any(char in marca_cruda for char in ["/", "\\", ":", ";"]):
            marca_cruda = "Desconocida"
            
        nombre_marca = normalizar_marca(marca_cruda)
        
        if nombre_marca not in cache_marcas:
            marca_db = db.query(models.Marca).filter_by(nombre=nombre_marca).first()
            if not marca_db:
                marca_db = models.Marca(nombre=nombre_marca)
                db.add(marca_db)
                db.commit()
                db.refresh(marca_db)
            cache_marcas[nombre_marca] = marca_db.id

        precio = 0.0
        afiliado_url = ""
        ofertas = item.get("offers", [])
        if ofertas:
            afiliado_url = ofertas[0].get("productUrl", "")
            historial = ofertas[0].get("priceHistory", [])
            if historial and "price" in historial[0]:
                precio = float(historial[0]["price"].get("value", 0))

        imagen_url = item.get("productImage", {}).get("url", "")

        metricas = calcular_metricas_precio(item, precio)
        
        nuevo_producto = models.Producto(
            nombre=nombre,
            descripcion=desc_limpia[:900], 
            precio=precio,
            imagen_url=imagen_url,
            afiliado_url=afiliado_url,
            marca_id=cache_marcas[nombre_marca],
            categoria_id=mapa_categorias[etiquetas["categoria"]],
            
            sabor=etiquetas["sabor"],
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
            slug=generar_slug(nombre)
        )
        productos_nuevos.append(nuevo_producto)

    db.add_all(productos_nuevos)
    db.commit()
    print(f"\n🎉 ¡Inyección de Farma2Go completada! {len(productos_nuevos)} suplementos reales guardados.")

if __name__ == "__main__":
    inyectar_en_bd()