import sys
import os
import time
import random
import requests
from bs4 import BeautifulSoup
import json
import base64
import re
import unicodedata

# Rutas para que reconozca la carpeta backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import SessionLocal
from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum, CategoriaEnum, normalizar_marca
)

db = SessionLocal()

# ==========================================
# 1. EL MAPA DE CATEGORÍAS (URLs Limpias)
# ==========================================
URLS_OBJETIVO = [
    "https://www.hsnstore.com/nutricion-deportiva",
    "https://www.hsnstore.com/salud-bienestar/acidos-grasos-esenciales",
    "https://www.hsnstore.com/salud-bienestar/perder-peso",
    "https://www.hsnstore.com/salud-bienestar/antioxidantes",
    "https://www.hsnstore.com/salud-bienestar/digestion",
    "https://www.hsnstore.com/salud-bienestar/estres-ansiedad",
    "https://www.hsnstore.com/salud-bienestar/sueno-descanso",
    "https://www.hsnstore.com/salud-bienestar/huesos-y-articulaciones",
    "https://www.hsnstore.com/alimentacion-saludable/mantequillas-y-cremas",
    "https://www.hsnstore.com/alimentacion-saludable/snacks-y-tentempies"
]

# ==========================================
# 2. HERRAMIENTAS Y MATEMÁTICAS
# ==========================================
def limpiar_texto(texto: str) -> str:
    if not texto: return ""
    return re.sub(r'<[^>]+>', ' ', texto).lower()

def generar_slug(nombre: str) -> str:
    texto = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

def generar_enlace_afiliado(url_producto: str) -> str:
    cadena = f"product||0||SUPARATOR||{url_producto}"
    link_id = base64.b64encode(cadena.encode('utf-8')).decode('utf-8')
    return f"https://www.hsnstore.com/affiliate/click/index?linkid={link_id}"

def extraer_porcentaje_proteina(texto: str):
    if not texto: return None
    texto = texto.lower()
    
    # 1. Caza formato explícito "77,3 g de proteína por 100 g"
    m1 = re.search(r'(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,20}100\s*g', texto)
    if m1: return round(float(m1.group(1).replace(',', '.')))

    # 2. Caza formato matemático "23 g de proteína por porción de 30 g" -> Hace (23/30)*100
    m2 = re.search(r'(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,30}(\d{2,3}(?:[.,]\d+)?)\s*g', texto)
    if m2:
        prot = float(m2.group(1).replace(',', '.'))
        porcion = float(m2.group(2).replace(',', '.'))
        if porcion > 0 and prot <= porcion:
            return round((prot / porcion) * 100)

    # 3. Caza porcentajes atados directamente a la palabra "80% de proteína" o "WPC 80%"
    m3 = re.search(r'(\d{2}(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:prote[íi]na|pureza|wpc|wpi|cfm|whey|aislado)', texto)
    if m3: return round(float(m3.group(1).replace(',', '.')))

    m4 = re.search(r'(?:wpc|wpi|cfm|whey|prote[íi]na|pureza|concentración|proteico)[^\d]{0,20}(\d{2}(?:[.,]\d+)?)\s*%', texto)
    if m4: return round(float(m4.group(1).replace(',', '.')))

    # 4. Búsqueda Desesperada (Cazador Contextual)
    porcentajes = re.finditer(r'(\d{2}(?:[.,]\d+)?)\s*%', texto)
    for p in porcentajes:
        valor = round(float(p.group(1).replace(',', '.')))
        if 50 <= valor <= 98: 
            inicio = max(0, p.start() - 60)
            fin = min(len(texto), p.end() + 60)
            entorno = texto[inicio:fin]
            if any(palabra in entorno for palabra in ["prote", "pureza", "aislado", "concentrado", "contenido"]):
                return valor

    return None

def calcular_metricas_precio(nombre: str, descripcion: str, precio: float):
    metricas = {"peso_gramos": None, "precio_por_kg": None, "unidades": None, "precio_por_unidad": None}
    match_unidades = re.search(r'(\d+)\s*(cap|caps|cápsulas|capsulas|comprimidos|pastillas|perlas|viales|uds|unidades|tablets|tabletas)\b', nombre)
    es_pastilla = False
    
    if match_unidades:
        try:
            unidades = int(match_unidades.group(1))
            metricas["unidades"] = unidades
            es_pastilla = True
            if precio and precio > 0 and unidades > 0:
                metricas["precio_por_unidad"] = round(precio / unidades, 3)
        except ValueError: pass

    if not es_pastilla:
        for texto in [nombre, descripcion]:
            if not texto: continue
            patron = r'(\d+(?:[.,]\d+)?)\s*(kg|kilo|kilos|g|gr|gramos|lbs|lb|libra|ml|l|litros)\b'
            coincidencias = list(re.finditer(patron, texto))
            peso_encontrado = False
            
            for match in reversed(coincidencias):
                cantidad = float(match.group(1).replace(',', '.'))
                unidad = match.group(2)
                peso_kg = 0.0
                
                if unidad in ['kg', 'kilo', 'kilos', 'l', 'litros']: peso_kg = cantidad
                elif unidad in ['lbs', 'lb', 'libra']: peso_kg = cantidad * 0.453592
                else: 
                    if cantidad < 20 and texto == nombre: continue 
                    peso_kg = cantidad / 1000
                    
                metricas["peso_gramos"] = int(peso_kg * 1000)
                if precio and precio > 0 and peso_kg > 0:
                    metricas["precio_por_kg"] = round(precio / peso_kg, 2)
                    
                peso_encontrado = True; break
            if peso_encontrado: break
            
    return metricas

# ==========================================
# 3. EL CEREBRO CLASIFICADOR (V2 - Mejorado)
# ==========================================
def clasificar_producto(nombre: str, desc_limpia: str):
    n = nombre.lower()
    texto_completo = n + " " + desc_limpia.lower()
    c = {}
    
    if any(p in n for p in ["shaker", "mezclador", "botella", "toalla", "camiseta", "mochila"]): return None

    # Categorías
    if any(p in n for p in ["crema", "harina", "copos", "mermelada", "avena", "eritritol", "peanut", "salsa", "sirope", "snack", "stevia", "sucralosa", "xilitol", "chocolate", "cacao", "hummus"]): 
        c["categoria"] = CategoriaEnum.alimentacion.value
    elif any(p in n for p in ["gel", "electrolitos", "hidratación", "boom", "pre-entreno", "pre entreno", "hydrop", "evordx"]): 
        c["categoria"] = CategoriaEnum.pre_entrenos.value
    elif any(p in n for p in ["whey", "protein", "proteína", "proteina", "isolate", "aislado", "evowhey", "evoisolate"]): 
        c["categoria"] = CategoriaEnum.proteinas.value
    elif "creatin" in n: 
        c["categoria"] = CategoriaEnum.creatinas.value
    elif any(p in n for p in ["amino", "bcaa", "glutamina", "carnitina", "citrulina", "eaa"]): 
        c["categoria"] = CategoriaEnum.aminoacidos.value
    elif any(p in n for p in ["vitamin", "mineral", "magnesio", "calcio", "zinc", "omega", "colágeno", "melatonina", "hierro"]): 
        c["categoria"] = CategoriaEnum.vitaminas.value
    else: 
        c["categoria"] = CategoriaEnum.otros.value

    # Filtros Globales y Sabores
    c["es_vegano"] = True if any(p in texto_completo for p in ["apto para veganos", "proteína vegana", "vegan protein", "vegana", "vegetal"]) else False

    sabores = []
    if "vainilla" in texto_completo: sabores.append(SaborEnum.vainilla.value)
    if any(p in texto_completo for p in ["chocolate", "cacao", "brownie"]): sabores.append(SaborEnum.chocolate.value)
    if "fresa" in texto_completo: sabores.append(SaborEnum.fresa.value)
    if any(p in texto_completo for p in ["limon", "limón", "citric"]): sabores.append(SaborEnum.limon.value)
    if "cookies" in texto_completo or "cream" in texto_completo: sabores.append(SaborEnum.cookies.value)
    if "plátano" in texto_completo or "banana" in texto_completo: sabores.append(SaborEnum.platano.value)
    if "café" in texto_completo or "capuchino" in texto_completo: sabores.append(SaborEnum.cafe.value)
    if "frutas del bosque" in texto_completo or "berry" in texto_completo: sabores.append(SaborEnum.frutas.value)
    if "coco" in texto_completo: sabores.append("Coco")
    if not sabores: sabores.append(SaborEnum.neutro.value)
    c["sabor"] = sabores

    # Formatos
    c["formato"] = None
    if "tableta" in n and c["categoria"] == CategoriaEnum.alimentacion.value:
        c["formato"] = FormatoEnum.barrita.value
    elif any(p in texto_completo for p in ["cápsula", "capsula", "comprimido", "perla", "tableta"]): 
        c["formato"] = FormatoEnum.capsulas.value
    elif any(p in texto_completo for p in ["vial", "gel", "líquido", "gotas"]): 
        c["formato"] = FormatoEnum.liquido.value
    elif any(p in texto_completo for p in ["polvo", "harina"]): 
        c["formato"] = FormatoEnum.polvo.value
    elif "barrita" in texto_completo: 
        c["formato"] = FormatoEnum.barrita.value
        
    if not c["formato"]:
        if c["categoria"] in [CategoriaEnum.proteinas.value, CategoriaEnum.creatinas.value]: c["formato"] = FormatoEnum.polvo.value
        elif any(p in texto_completo for p in ["cazo", "cacito", "scoop", "mezclar"]): c["formato"] = FormatoEnum.polvo.value

    # Objetivos y Sellos
    # 4. Objetivos y Sellos (AHORA ES MULTISELECCIÓN Y MÁS LISTO)
    objetivos = []
    
    if any(p in texto_completo for p in ["volumen", "gainer", "masa", "crecimiento", "aumento"]): 
        objetivos.append(ObjetivoEnum.volumen.value)
    
    if any(p in texto_completo for p in ["peso", "quema", "termogénico", "definición", "adelgazar", "grasa", "keto"]): 
        objetivos.append(ObjetivoEnum.definicion.value)
    
    if any(p in texto_completo for p in ["rendimiento", "energía", "fuerza", "recuperación", "resistencia", "entrenamiento", "post-entreno"]): 
        objetivos.append(ObjetivoEnum.rendimiento.value)
        
    if any(p in texto_completo for p in ["salud", "articular", "bienestar", "inmune", "digestión", "hueso", "articulaciones", "omega", "vitamin"]): 
        objetivos.append(ObjetivoEnum.salud.value)

    c["objetivo"] = objetivos if objetivos else None

    c["sello_calidad"] = None
    if "creapure" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.creapure.value
    elif "kyowa" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.kyowa.value
    elif "lacprodan" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.lacprodan.value
    elif "isolac" in texto_completo: c["sello_calidad"] = SelloCalidadEnum.isolac.value

    # Subfiltros
    c["tipo_proteina"] = c["porcentaje_proteina"] = c["tipo_creatina"] = c["perfil_aminoacidos"] = c["tipo_vitamina"] = None
    if c["categoria"] == CategoriaEnum.proteinas.value:
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto_completo)
        if any(v in texto_completo for v in ["proteína vegetal", "proteina vegetal", "vegan protein", "proteína de soja", "proteina de soja", "proteína de guisante", "proteína de arroz", "proteína de garbanzo", "proteína de calabaza"]):            c["tipo_proteina"] = TipoProteinaEnum.vegetal.value
        elif "isolate" in texto_completo or "aislado" in texto_completo: 
            c["tipo_proteina"] = TipoProteinaEnum.isolate.value
        elif "caseina" in texto_completo or "casein" in texto_completo: 
            c["tipo_proteina"] = TipoProteinaEnum.caseina.value
        elif "hidrolizado" in texto_completo: 
            c["tipo_proteina"] = TipoProteinaEnum.hidrolizado.value
        else: 
            c["tipo_proteina"] = TipoProteinaEnum.whey.value
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto_completo)
        
        # 3. EL PLAN B (Fallback de la industria si la función matemática devuelve None)
        if c["porcentaje_proteina"] is None:
            if c["tipo_proteina"] == TipoProteinaEnum.isolate.value:
                c["porcentaje_proteina"] = 93
            elif c["tipo_proteina"] == TipoProteinaEnum.whey.value:
                c["porcentaje_proteina"] = 75
        
    elif c["categoria"] == CategoriaEnum.creatinas.value:
        if "micronizada" in texto_completo or "mesh" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.micronizada.value
        elif "kre-alkalyn" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.kre_alkalyn.value
        else: c["tipo_creatina"] = TipoCreatinaEnum.monohidrato.value
        
    elif c["categoria"] == CategoriaEnum.aminoacidos.value:
        if "bcaa" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa.value
        elif "glutamina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina.value
        elif "eaa" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.eaa.value
        elif "citrulina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.citrulina.value
        elif "alanina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.beta_alanina.value

    elif c["categoria"] == CategoriaEnum.vitaminas.value:
        if "multivitam" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.multivitaminico.value
        elif "vitamina c" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_c.value
        elif "vitamina d" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_d.value
        elif "magnesio" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.magnesio.value
        elif "omega" in texto_completo: c["tipo_vitamina"] = TipoVitaminaEnum.omega3.value

    return c

# ==========================================
# 4. INYECCIÓN PRINCIPAL BLINDADA
# ==========================================
def inyectar_en_bd():
    try:
        nombre_marca = normalizar_marca("HSN")
        marca_hsn = db.query(models.Marca).filter_by(nombre=nombre_marca).first()
        if not marca_hsn:
            marca_hsn = models.Marca(nombre=nombre_marca)
            db.add(marca_hsn)
            db.commit(); db.refresh(marca_hsn)

        print("🧹 Limpiando catálogo antiguo de HSN...")
        db.query(models.Producto).filter(models.Producto.marca_id == marca_hsn.id).delete()
        db.commit()

        mapa_categorias = {}
        for cat in CategoriaEnum:
            cat_db = db.query(models.Categoria).filter_by(nombre=cat.value).first()
            if not cat_db:
                cat_db = models.Categoria(nombre=cat.value); db.add(cat_db); db.commit(); db.refresh(cat_db)
            mapa_categorias[cat.value] = cat_db.id
    except Exception as e:
        db.rollback()
        print(f"❌ Error al inicializar BBDD: {e}")
        return

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
    })

    productos_nuevos = []
    enlaces_procesados = set()
    total_general = 0

    for url_cat in URLS_OBJETIVO:
        print(f"\n🌐 Explorando: {url_cat}")
        cat_count = 0
        pagina = 1
        max_paginas = 20
        
        while pagina <= max_paginas:
            url_pagina = f"{url_cat}?p={pagina}" if pagina > 1 else url_cat
            try:
                res_cat = session.get(url_pagina, timeout=30)
                soup_cat = BeautifulSoup(res_cat.text, 'lxml')
                enlaces_pagina = [a.get('href') for a in soup_cat.select('.product-item-link') if a.get('href')]
                
                if not enlaces_pagina: 
                    break 
                
                print(f"   📄 Procesando página {pagina} ({len(enlaces_pagina)} productos)...")
                
                for url_prod in enlaces_pagina:
                    if url_prod in enlaces_procesados: continue
                    enlaces_procesados.add(url_prod)
                    
                    try:
                        res_prod = session.get(url_prod, timeout=20)
                        soup_prod = BeautifulSoup(res_prod.text, 'lxml')
                        
                        stock = soup_prod.find('meta', {'itemprop': 'availability'})
                        if stock and 'outofstock' in stock.get('content', '').lower():
                            continue 
                        
                        bloques_json = soup_prod.find_all('script', type='application/ld+json')
                        datos_producto = None
                        
                        for bloque in bloques_json:
                            try:
                                contenido = json.loads(bloque.string.strip())
                                if isinstance(contenido, dict) and contenido.get('@type') == 'Product': datos_producto = contenido; break
                                elif isinstance(contenido, list):
                                    for item in contenido:
                                        if isinstance(item, dict) and item.get('@type') == 'Product': datos_producto = item; break
                            except: pass
                        
                        if not datos_producto: continue
                        
                        nombre = datos_producto.get('name', 'Sin nombre')
                        imagen = datos_producto.get('image', '')
                        desc_cruda = datos_producto.get('description', '')
                        
                        precio = 0.0
                        precio_anterior = None 
                        ofertas = datos_producto.get('offers', {})
                        try:
                            if isinstance(ofertas, dict): precio = float(ofertas.get('lowPrice', ofertas.get('price', 0.0)))
                            elif isinstance(ofertas, list):
                                for of in ofertas:
                                    if isinstance(of, dict) and float(of.get('price', 0.0)) > 0:
                                        precio = float(of.get('price', 0.0)); break
                        except: pass
                        
                        
                        if precio == 0.0:
                            precio_meta = soup_prod.find('meta', {'property': 'product:price:amount'})
                            if precio_meta:
                                precio = float(precio_meta.get('content', 0.0))
                            else:
                                precio_html = soup_prod.find('span', class_=re.compile(r'price'))
                                if precio_html:
                                    txt = precio_html.text.replace('€', '').replace(',', '.').replace('\xa0', '').strip()
                                    try: 
                                        match_precio = re.search(r'(\d+\.\d+)', txt)
                                        if match_precio: precio = float(match_precio.group(1))
                                    except: pass

                        if precio > 0:
                            html_precio_viejo = soup_prod.find(class_=re.compile(r'old-price'))
                            if html_precio_viejo:
                                html_span = html_precio_viejo.find('span', class_=re.compile(r'price'))
                                if html_span:
                                    txt_viejo = html_span.text.replace('€', '').replace(',', '.').replace('\xa0', '').strip()
                                    try:
                                        match_viejo = re.search(r'(\d+\.\d+)', txt_viejo)
                                        if match_viejo:
                                            p_viejo = float(match_viejo.group(1))
                                            if p_viejo > precio:
                                                precio_anterior = p_viejo
                                    except: pass

                        # --- NUEVO: CAZADOR DE PESOS OCULTOS PARA HSN ---
                        titulo_pagina = soup_prod.find('title').text if soup_prod.find('title') else ""
                        opcion_marcada = soup_prod.find(class_=re.compile(r'swatch-option.*selected'))
                        texto_talla = opcion_marcada.text if opcion_marcada else ""
                        nombre_ampliado = f"{nombre} {titulo_pagina} {texto_talla}".lower()
                        # ------------------------------------------------

                        # --- NUEVO: CAZADOR DE SABORES OCULTOS PARA HSN ---
                        opciones_sabor = soup_prod.find_all(attrs={"option-label": True})
                        textos_sabores = [op.get("option-label", "") for op in opciones_sabor]
                        
                        # Plan B por si usan clases en lugar de option-label
                        if not textos_sabores:
                            swatches = soup_prod.find_all(class_=re.compile(r'swatch-option'))
                            textos_sabores = [s.text for s in swatches]
                            
                        texto_sabores_extra = " ".join(textos_sabores).lower()
                        # ------------------------------------------------------------

                        desc_limpia = limpiar_texto(desc_cruda)
                        
                        # Fusionamos la descripción limpia con los sabores ocultos que hemos cazado
                        desc_ampliada_para_cerebro = f"{desc_limpia} {texto_sabores_extra}"
                        
                        etiquetas = clasificar_producto(nombre, desc_ampliada_para_cerebro)
                        
                        if not etiquetas: continue
                        
                        metricas = calcular_metricas_precio(nombre_ampliado, desc_limpia, precio)
                        url_afiliado = generar_enlace_afiliado(url_prod)
                        
                        nuevo_prod = models.Producto(
                            nombre=nombre, descripcion=desc_limpia[:900], precio=precio,precio_anterior=precio_anterior, imagen_url=imagen, afiliado_url=url_afiliado,
                            marca_id=marca_hsn.id, categoria_id=mapa_categorias[etiquetas["categoria"]], sabor=etiquetas["sabor"],
                            formato=etiquetas["formato"], objetivo=etiquetas["objetivo"], es_vegano=etiquetas["es_vegano"],
                            sello_calidad=etiquetas["sello_calidad"], tipo_proteina=etiquetas["tipo_proteina"],
                            porcentaje_proteina=etiquetas["porcentaje_proteina"], tipo_creatina=etiquetas["tipo_creatina"],
                            perfil_aminoacidos=etiquetas["perfil_aminoacidos"], tipo_vitamina=etiquetas["tipo_vitamina"],
                            peso_gramos=metricas["peso_gramos"], precio_por_kg=metricas["precio_por_kg"], slug=generar_slug(nombre),
                        )
                        productos_nuevos.append(nuevo_prod)
                        cat_count += 1
                        total_general += 1
                        
                        # --- ESCUDO ANTI-FALLOS DE BBDD ---
                        if len(productos_nuevos) >= 20:
                            try:
                                db.add_all(productos_nuevos)
                                db.commit()
                            except Exception as db_err:
                                db.rollback() # <- ESTO SALVA EL SCRIPT
                                print(f"      ⚠️ Advertencia BD: {db_err.__class__.__name__}. Reintentando en el próximo lote.")
                            finally:
                                productos_nuevos = [] 
                            
                        time.sleep(0.3 + random.random() * 0.5)
                        
                    except requests.exceptions.RequestException:
                        continue 
                    
            except requests.exceptions.RequestException as net_err:
                # --- ESCUDO ANTI-APAGONES DE RED ---
                print(f"   ⚠️ Corte de internet detectado en página {pagina}. Saltando...")
                time.sleep(2) # Pausa para que el router se recupere
                break 
            except Exception as e:
                print(f"   ⚠️ Fallo inesperado en página {pagina}: {e}")
                break 
            
            pagina += 1
            
        print(f"   ✅ {cat_count} productos procesados en esta categoría.")

    # Guardado Final Seguro
    if productos_nuevos:
        try:
            db.add_all(productos_nuevos)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"⚠️ Aviso: No se pudieron guardar los últimos {len(productos_nuevos)} productos.")
        
    print(f"\n🎉 ¡MISIÓN CUMPLIDA! Catálogo inyectado: {total_general} productos robustos.")
if __name__ == "__main__":
    inyectar_en_bd()