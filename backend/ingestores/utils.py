import re
import unicodedata
from typing import Any, Dict, Optional, List, Union

from schemas import (
    SaborEnum, FormatoEnum, ObjetivoEnum, SelloCalidadEnum, 
    TipoProteinaEnum, TipoCreatinaEnum, PerfilAminoacidosEnum, TipoVitaminaEnum,
    CategoriaEnum
)

def limpiar_texto(texto: str) -> str:
    if not texto: return ""
    texto_sin_html = re.sub(r'<[^>]+>', ' ', str(texto))
    if "una combinación ganadora" in texto_sin_html.lower():
        texto_sin_html = texto_sin_html[:texto_sin_html.lower().find("una combinación ganadora")]
    return texto_sin_html.strip().lower()

def generar_slug(nombre: str) -> str:
    if not nombre: return ""
    texto = unicodedata.normalize('NFKD', str(nombre)).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]+', '-', texto.lower()).strip('-')

def extraer_porcentaje_proteina(texto: str) -> Optional[int]:
    if not texto: return None
    texto_lower = str(texto).lower()

    m1 = re.search(r'(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,20}100\s*g', texto_lower)
    if m1: return round(float(m1.group(1).replace(',', '.')))

    m2 = re.search(r'(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,30}(\d{2,3}(?:[.,]\d+)?)\s*g', texto_lower)
    if m2:
        prot = float(m2.group(1).replace(',', '.'))
        porcion = float(m2.group(2).replace(',', '.'))
        if porcion > 0 and prot <= porcion:
            return round((prot / porcion) * 100)

    m3 = re.search(r'(\d{2}(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:prote[íi]na|pureza|wpc|wpi|cfm|whey|aislado)', texto_lower)
    if m3: return round(float(m3.group(1).replace(',', '.')))

    return None

def calcular_metricas_precio(
    item_or_nombre: Union[dict, str],
    precio: Optional[float] = None,
    descripcion: str = ""
) -> Dict[str, Any]:
    nombre = ""
    peso_explicit = None
    peso_json = ""

    if isinstance(item_or_nombre, dict):
        item = item_or_nombre
        nombre = str(item.get("name") or item.get("nombre") or "").lower()
        if precio is None:
            raw_precio = item.get("precio") or item.get("price") or item.get("precio_actual")
            try: precio = float(raw_precio) if raw_precio is not None else 0.0
            except (ValueError, TypeError): precio = 0.0
        descripcion = str(item.get("description") or item.get("descripcion") or "")
        peso_json = str(item.get("weight") or "").lower()
        if item.get("peso_gramos") is not None:
            try: peso_explicit = int(item["peso_gramos"])
            except (ValueError, TypeError): pass
    else:
        nombre = str(item_or_nombre or "").lower()
        if precio is None: precio = 0.0

    metricas = {"peso_gramos": None, "precio_por_kg": None, "unidades": None, "precio_por_unidad": None}

    if peso_explicit is not None and peso_explicit > 0:
        metricas["peso_gramos"] = peso_explicit
        peso_kg = peso_explicit / 1000.0
        if precio and precio > 0 and peso_kg > 0:
            metricas["precio_por_kg"] = round(precio / peso_kg, 2)

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

    if metricas["peso_gramos"] is None and not es_pastilla:
        textos_donde_buscar = [t for t in [peso_json, nombre, descripcion] if t]
        for texto in textos_donde_buscar:
            patron = r'(\d+(?:[.,]\d+)?)\s*(kg|kilo|kilos|g|gr|gramos|lbs|lb|libra|ml|l|litros)\b'
            coincidencias = list(re.finditer(patron, texto))
            peso_encontrado = False
            for match in reversed(coincidencias):
                cantidad_cruda = match.group(1).replace(',', '.')
                try:
                    cantidad = float(cantidad_cruda)
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
                    peso_encontrado = True
                    break
                except ValueError: continue
            if peso_encontrado: break

    return metricas

def clasificar_producto(
    nombre: str,
    desc_limpia: str,
    categorias_raw: Optional[Union[List, str]] = None
) -> Optional[Dict[str, Any]]:
    """Clasificador central quirúrgico con resolución de colisiones y vocabulario hiper-enriquecido."""
    n = str(nombre or "").lower()

    # 1. FILTRO DE BASURA EXTREMO (Solo merchandising, ropa, accesorios y cosmética/tópicos)
    basura = [
        "shaker", "mezclador", "toalla", "facial", "corporal", "champú", "champu",
        "dientes", "dental", "serum", "cosmética", "cosmetica", "higiene", "pañal", 
        "solar", "maquillaje", "mascarilla", "pelo", "cabello", "limpiador", "kit", 
        "gel de ducha", "gel reductor", "crema reductora", "crema hidratante", "loción", "locion", 
        "bálsamo", "balsamo", "ducha", "baño", "antiarrugas", "antiedad", "colutorio", 
        "spray nasal", "spray ocular", "gotas oculares", "colirio", "pomada", "íntimo", 
        "bebé", "infantil", "chupete", "biberón", "ortopedia", "muñequera", "rodillera", 
        "termómetro", "tiritas", "apósito", "venda", "alcohol", "agua micelar", 
        "desmaquillante", "balón", "balon", "neceser", "regalo", "botiquín", "óptica", 
        "sexual", "perfumería", "camiseta", "mochila", "pastillero"
    ]

    if any(p in n for p in basura):
        return None

    if categorias_raw:
        cat_list = [str(c).lower() for c in (categorias_raw if isinstance(categorias_raw, list) else [categorias_raw])]
        prohibidas = ["cosmética", "higiene", "bebé", "ortopedia", "facial", "corporal", "capilar", "solar", "maternidad", "infantil", "bucal", "dental", "botiquín", "óptica", "sexual", "perfumería"]
        if any(p in c for c in cat_list for p in prohibidas):
            return None

    c = {}

    # Detección de Colágeno y Espinacas para resolver colisiones
    es_colageno = any(p in n for p in ["colágeno", "colageno", "collagen"])
    es_espinaca = "espinaca" in n

    # 2. EVALUACIÓN DE LAS 8 CATEGORÍAS (CON PRIORIDAD CORREGIDA)

    # A) SALUD Y BIENESTAR (Máxima prioridad para Colágeno y Digestivos)
    if es_colageno or any(p in n for p in [
        "omega", "articulacio", "digestiv", "probiótico", "probiotico", 
        "extracto", "cúrcuma", "curcuma", "ashwagandha", "espirulina", "spirulina", "ginseng", 
        "ginkgo", "valeriana", "sueño", "ansiedad", "termogen", "evoburn", "evodren", "detox", 
        "condroitina", "glucosamina", "evoptogen", "evoblocker", "estroblock", "glucomanano", 
        "evosterone", "cla", "té verde", "resveratrol", "maca", "saw palmetto", "silicio", 
        "psyllium", "inulina", "própolis", "hialurónico", "mct", "aceite de coco", "keto", 
        "sauce", "pack", "giftbox", "melatonina", "aceite", "krill", "onagra", "bacalao", "care", 
        "digezyme", "enzim", "enzima", "lactasa", "pepsina", "papaina", "msm", "uc-ii", "uc2", 
        "5-htp", "5htp", "inositol", "same", "ala", "lipoico", "astaxantina", "coq10", "q10", 
        "ubiquinol", "rutina", "antiox", "fórmula", "formula"
    ]):
        c["categoria"] = CategoriaEnum.salud.value

    # B) PROTEÍNAS (Excluye colágeno explícitamente)
    elif not es_colageno and any(p in n for p in [
        "whey", "protein", "proteína", "proteina", "isolate", "aislado", "evowhey", "evoisolate", 
        "casein", "caseína", "caseina", "evocasein", "albúmina", "albumina", "evoegg", "huevo", 
        "gainer", "evomass", "mass gainer", "hydro", "hidrolizad", "hidrolizado", "evohydro", "peptopro"
    ]): 
        c["categoria"] = CategoriaEnum.proteinas.value

    # C) CREATINAS
    elif "creatin" in n or "kre-alkalyn" in n: 
        c["categoria"] = CategoriaEnum.creatinas.value

    # D) AMINOÁCIDOS (Resuelto el bug de espiNACa usando regex para \bnac\b)
    elif not es_espinaca and (bool(re.search(r'\bnac\b', n)) or any(p in n for p in [
        "amino", "bcaa", "glutamina", "carnitina", "citrulina", "eaa", "leucina", "arginina", 
        "ornitina", "aspártico", "aspartico", "d-aa", "lisina", "taurina", "tirosina", 
        "tyrosine", "triptófano", "triptofano", "tryptophan", "beta-alanina", "alanina", 
        "hmb", "gaba", "glutat"
    ])): 
        c["categoria"] = CategoriaEnum.aminoacidos.value

    # E) PRE-ENTRENOS, INTRA Y RENDIMIENTO
    elif any(p in n for p in [
        "pre-entreno", "pre entreno", "gel energético", "gel energ", "evoenergy", "electrolito", 
        "electrolitos", "evolytes", "isotónico", "isotonico", "evotonic", "evorecovery", 
        "evocarbs", "evodextrin", "dextrina", "ciclodextrina", "amilopectina", "vitargo", 
        "hidratación", "hidratacion", "evordx", "hydrop", "pump", "nitrico", "evobolic", "anabolic", 
        "cafeína", "cafeina", "caffeine", "teanina", "theanine"
    ]): 
        c["categoria"] = CategoriaEnum.pre_entrenos.value

    # F) VITAMINAS Y MINERALES
    elif any(p in n for p in [
        "vitamin", "mineral", "magnesio", "calcio", "zinc", "manganeso", "cromo", "picolinato", 
        "potasio", "sodio", "hierro", "yodo", "cobre", "selenio", "evovits", "evozma", "zma", 
        "multivitam"
    ]): 
        c["categoria"] = CategoriaEnum.vitaminas.value

    # G) ALIMENTACIÓN SALUDABLE (Incluye Espinaca y Cremas)
    elif es_espinaca or any(p in n for p in [
        "harina", "copos", "mermelada", "avena", "eritritol", "peanut", "crema de cacahuete", 
        "crema de arroz", "salsa 0", "sirope 0", "snack", "gummy", "evogummy", "barrita", 
        "flapjack", "energy bar", "bar", "galleta", "cookie", "pancake", "almendra", "pistacho", 
        "semilla", "chía", "chia", "lino", "pipas", "calabaza", "chocolate", "tableta"
    ]): 
        c["categoria"] = CategoriaEnum.alimentacion.value

    else:
        c["categoria"] = CategoriaEnum.salud.value

    # Subfiltros y Sabores
    texto_completo = n + " " + str(desc_limpia or "").lower()
    c["es_vegano"] = True if any(p in texto_completo for p in ["apto para veganos", "proteína vegana", "vegan protein", "vegana", "vegetal", "100% vegano"]) else False

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

    # FORMATO: Priorizar título para cápsulas/perlas antes de buscar polvo
    c["formato"] = None
    if any(p in n for p in ["cápsula", "capsula", "caps", "comprimido", "perla", "tableta", "tablets", "veg caps"]): 
        c["formato"] = FormatoEnum.capsulas.value
    elif any(p in texto_completo for p in ["vial", "gel", "líquido", "gotas"]): 
        c["formato"] = FormatoEnum.liquido.value
    elif any(p in texto_completo for p in ["polvo", "harina"]): 
        c["formato"] = FormatoEnum.polvo.value
    elif "barrita" in texto_completo or "flapjack" in texto_completo: 
        c["formato"] = FormatoEnum.barrita.value

    c["tipo_proteina"] = c["porcentaje_proteina"] = c["tipo_creatina"] = c["perfil_aminoacidos"] = c["tipo_vitamina"] = None
    if c["categoria"] == CategoriaEnum.proteinas.value:
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto_completo)
        if any(v in texto_completo for v in ["proteína vegetal", "proteina vegetal", "vegan protein", "proteína de soja"]):
            c["tipo_proteina"] = TipoProteinaEnum.vegetal.value
        elif "isolate" in texto_completo or "aislado" in texto_completo: 
            c["tipo_proteina"] = TipoProteinaEnum.isolate.value
        elif "caseina" in texto_completo or "casein" in texto_completo: 
            c["tipo_proteina"] = TipoProteinaEnum.caseina.value
        elif "hidrolizado" in texto_completo or "hydro" in texto_completo: 
            c["tipo_proteina"] = TipoProteinaEnum.hidrolizado.value
        else: 
            c["tipo_proteina"] = TipoProteinaEnum.whey.value

    elif c["categoria"] == CategoriaEnum.creatinas.value:
        if "micronizada" in texto_completo or "mesh" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.micronizada.value
        elif "kre-alkalyn" in texto_completo: c["tipo_creatina"] = TipoCreatinaEnum.kre_alkalyn.value
        else: c["tipo_creatina"] = TipoCreatinaEnum.monohidrato.value

    elif c["categoria"] == CategoriaEnum.aminoacidos.value:
        if "bcaa" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa.value
        elif "glutamina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina.value
        elif "eaa" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.eaa.value
        elif "citrulina" in texto_completo: c["perfil_aminoacidos"] = PerfilAminoacidosEnum.citrulina.value

    return c
