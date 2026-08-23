import re
import html
import unicodedata
from typing import Any, Dict, Optional, List, Union

from schemas import (
    SaborEnum,
    FormatoEnum,
    ObjetivoEnum,
    SelloCalidadEnum,
    TipoProteinaEnum,
    TipoCreatinaEnum,
    PerfilAminoacidosEnum,
    TipoVitaminaEnum,
    CategoriaEnum,
)


def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto_sin_html = re.sub(r"<[^>]+>", " ", str(texto))
    return texto_sin_html.strip().lower()


def normalizar_descripcion_ui(texto: str) -> str:
    if not texto:
        return ""

    # 1. Eliminar HTML y decodificar entidades raras (ej: &#8211; se vuelve un guion)
    t = re.sub(r"<[^>]+>", " ", str(texto))
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()

    # 2. Aniquilar preguntas iniciales.
    # Bucle por si hay varias seguidas ("¿Qué es X? ¿Para qué sirve?")
    while re.match(r"^¿[^?]+\?\s*", t):
        t = re.sub(r"^¿[^?]+\?\s*", "", t).strip()

    if not t:
        return ""

    # 3. Tijera inteligente (solo si el rollo comercial está en medio o al final)
    corte_tags = [
        "¿para qué sirve",
        "¿a quién va dirigido",
        "¿qué beneficios",
        "beneficios de",
        "funciones del",
        "ingredientes:",
        "una combinación ganadora",
    ]
    t_lower = t.lower()
    idx_corte = len(t)

    for tag in corte_tags:
        idx = t_lower.find(tag)
        # Solo cortamos si encontramos el tag más adelante en el texto, no en la posición 0
        if idx > 0 and idx < idx_corte:
            idx_corte = idx

    t = t[:idx_corte].strip()

    if not t:
        return ""

    # 4. Capitalizar primera letra y asegurar punto final
    # NO CORTAMOS a 200 caracteres para permitir que el Frontend gestione el "Leer más"
    t = t[0].upper() + t[1:]
    if not t.endswith((".", "!", "?")):
        t += "."

    return t


def generar_slug(nombre: str) -> str:
    if not nombre:
        return ""
    texto = (
        unicodedata.normalize("NFKD", str(nombre))
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def extraer_porcentaje_proteina(texto: str) -> Optional[int]:
    if not texto:
        return None
    texto_lower = str(texto).lower()

    m1 = re.search(
        r"(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,20}100\s*g",
        texto_lower,
    )
    if m1:
        return round(float(m1.group(1).replace(",", ".")))

    m2 = re.search(
        r"(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,30}(\d{2,3}(?:[.,]\d+)?)\s*g",
        texto_lower,
    )
    if m2:
        prot = float(m2.group(1).replace(",", "."))
        porcion = float(m2.group(2).replace(",", "."))
        if porcion > 0 and prot <= porcion:
            return round((prot / porcion) * 100)

    m3 = re.search(
        r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:prote[íi]na|pureza|wpc|wpi|cfm|whey|aislado)",
        texto_lower,
    )
    if m3:
        return round(float(m3.group(1).replace(",", ".")))

    return None


def calcular_metricas_precio(
    item_or_nombre: Union[dict, str],
    precio: Optional[float] = None,
    descripcion: str = "",
) -> Dict[str, Any]:
    nombre = ""
    peso_explicit = None
    peso_json = ""

    if isinstance(item_or_nombre, dict):
        item = item_or_nombre
        nombre = str(item.get("name") or item.get("nombre") or "").lower()
        if precio is None:
            raw_precio = (
                item.get("precio") or item.get("price") or item.get("precio_actual")
            )
            try:
                precio = float(raw_precio) if raw_precio is not None else 0.0
            except (ValueError, TypeError):
                precio = 0.0
        descripcion = str(item.get("description") or item.get("descripcion") or "")
        peso_json = str(item.get("weight") or "").lower()
        if item.get("peso_gramos") is not None:
            try:
                peso_explicit = int(item["peso_gramos"])
            except (ValueError, TypeError):
                pass
    else:
        nombre = str(item_or_nombre or "").lower()
        if precio is None:
            precio = 0.0

    metricas = {
        "peso_gramos": None,
        "precio_por_kg": None,
        "unidades": None,
        "precio_por_unidad": None,
    }

    if peso_explicit is not None and peso_explicit > 0:
        metricas["peso_gramos"] = peso_explicit
        peso_kg = peso_explicit / 1000.0
        if precio and precio > 0 and peso_kg > 0:
            metricas["precio_por_kg"] = round(precio / peso_kg, 2)

    match_unidades = re.search(
        r"(\d+)\s*(cap|caps|cápsulas|capsulas|comprimidos|pastillas|perlas|viales|uds|unidades|tablets|tabletas)\b",
        nombre,
    )
    es_pastilla = False

    if match_unidades:
        try:
            unidades = int(match_unidades.group(1))
            metricas["unidades"] = unidades
            es_pastilla = True
            if precio and precio > 0 and unidades > 0:
                metricas["precio_por_unidad"] = round(precio / unidades, 3)
        except ValueError:
            pass

    if metricas["peso_gramos"] is None and not es_pastilla:
        textos_donde_buscar = [t for t in [peso_json, nombre, descripcion] if t]
        for texto in textos_donde_buscar:
            patron = r"(\d+(?:[.,]\d+)?)\s*(kg|kilo|kilos|g|gr|gramos|lbs|lb|libra|ml|l|litros)\b"
            coincidencias = list(re.finditer(patron, texto))
            peso_encontrado = False
            for match in reversed(coincidencias):
                cantidad_cruda = match.group(1).replace(",", ".")
                try:
                    cantidad = float(cantidad_cruda)
                    unidad = match.group(2)
                    peso_kg = 0.0
                    if unidad in ["kg", "kilo", "kilos", "l", "litros"]:
                        peso_kg = cantidad
                    elif unidad in ["lbs", "lb", "libra"]:
                        peso_kg = cantidad * 0.453592
                    else:
                        if cantidad < 20 and texto == nombre:
                            continue
                        peso_kg = cantidad / 1000
                    metricas["peso_gramos"] = int(peso_kg * 1000)
                    if precio and precio > 0 and peso_kg > 0:
                        metricas["precio_por_kg"] = round(precio / peso_kg, 2)
                    peso_encontrado = True
                    break
                except ValueError:
                    continue
            if peso_encontrado:
                break

    return metricas


def clasificar_producto(
    nombre: str, desc_limpia: str, categorias_raw: Optional[Union[List, str]] = None
) -> Optional[Dict[str, Any]]:
    """Clasificador central quirúrgico con resolución de colisiones y vocabulario hiper-enriquecido."""
    n = str(nombre or "").lower()

    texto_completo = n + " " + str(desc_limpia or "").lower()

    # 1. FILTRO DE BASURA (Solo en título para evitar falsos positivos)
    basura_titulo = [
        "shaker",
        "mezclador",
        "toalla",
        "facial",
        "corporal",
        "champú",
        "champu",
        "dientes",
        "dental",
        "serum",
        "cosmética",
        "cosmetica",
        "higiene",
        "pañal",
        "solar",
        "maquillaje",
        "mascarilla",
        "pelo",
        "cabello",
        "limpiador",
        "kit",
        "gel de ducha",
        "crema reductora",
        "crema hidratante",
        "loción",
        "locion",
        "bálsamo",
        "balsamo",
        "ducha",
        "baño",
        "antiarrugas",
        "antiedad",
        "colutorio",
        "spray nasal",
        "spray ocular",
        "gotas oculares",
        "colirio",
        "pomada",
        "íntimo",
        "bebé",
        "infantil",
        "chupete",
        "biberón",
        "ortopedia",
        "muñequera",
        "rodillera",
        "termómetro",
        "tiritas",
        "apósito",
        "venda",
        "alcohol",
        "agua micelar",
        "desmaquillante",
        "neceser",
        "regalo",
        "botiquín",
        "óptica",
        "sexual",
        "perfumería",
        "camiseta",
        "mochila",
        "pastillero",
    ]
    if any(re.search(r"\b" + p + r"\b", n) for p in basura_titulo):
        return None

    # 1.2 FILTRO VETERINARIO (Búsqueda estricta en Título + Descripción)
    basura_veterinaria = [
        "mascota",
        "veterinaria",
        "perro",
        "gato",
        "ave",
        "pájaro",
        "canario",
        "roedor",
        "peces",
        "cachorro",
        "felino",
        "canino",
    ]
    if any(re.search(r"\b" + p + r"\b", texto_completo) for p in basura_veterinaria):
        return None

    if categorias_raw:
        cat_list = [
            str(c).lower()
            for c in (
                categorias_raw if isinstance(categorias_raw, list) else [categorias_raw]
            )
        ]
        prohibidas = [
            "cosmética",
            "higiene",
            "bebé",
            "ortopedia",
            "facial",
            "corporal",
            "capilar",
            "solar",
            "maternidad",
            "infantil",
            "bucal",
            "dental",
            "botiquín",
            "óptica",
            "sexual",
            "perfumería",
        ]
        if any(p in c for c in cat_list for p in prohibidas):
            return None

    c = {}

    # Detección de entidades base
    es_colageno = any(p in n for p in ["colágeno", "colageno", "collagen"])
    es_espinaca = "espinaca" in n

    # Términos explícitos de proteína (incluye adjetivos 'proteico/proteica')
    tiene_termino_proteina = any(
        p in n
        for p in [
            "whey",
            "protein",
            "proteína",
            "proteina",
            "proteico",
            "proteica",
            "isolate",
            "aislado",
            "evowhey",
            "evoisolate",
            "casein",
            "caseína",
            "caseina",
            "evocasein",
            "albúmina",
            "albumina",
            "evoegg",
            "gainer",
            "evomass",
            "mass gainer",
            "hydro",
            "hidrolizad",
            "hidrolizado",
            "evohydro",
            "peptopro",
        ]
    )

    # Términos específicos de alimentación preparada/postres proteicos
    es_alimentacion_preparada = any(
        p in n
        for p in [
            "pudding",
            "mousse",
            "flan",
            "natilla",
            "café proteico",
            "cafe proteico",
            "protein coffee",
            "tortita",
            "pancake",
            "cookie",
            "galleta",
            "barrita",
            "bar",
            "flapjack",
            "snack",
            "crema de",
            "peanut butter",
            "sirope",
            "salsa",
            "harina",
            "copos",
            "avena",
            "chía",
            "chia",
            "lino",
            "semilla",
            "pipas",
            "mermelada",
            "eritritol",
            "chocolate",
        ]
    )

    # 1. SALUD Y BIENESTAR: Colágeno tiene prioridad absoluta
    if es_colageno:
        c["categoria"] = CategoriaEnum.salud.value

    # 2. ALIMENTACIÓN SALUDABLE (Postres, cafés proteicos, cremas, harinas)
    elif es_espinaca or es_alimentacion_preparada:
        c["categoria"] = CategoriaEnum.alimentacion.value

    # 3. PROTEÍNAS (Si contiene términos de proteína, NO debe ser secuestrado por 'digezyme' ni 'keto')
    elif tiene_termino_proteina:
        c["categoria"] = CategoriaEnum.proteinas.value

    # 4. CREATINAS
    elif "creatin" in n or "kre-alkalyn" in n:
        c["categoria"] = CategoriaEnum.creatinas.value

    # 5. AMINOÁCIDOS (Aminograma completo: L-Histidina, Metionina, Treonina, etc.)
    elif bool(re.search(r"\bnac\b", n)) or any(
        p in n
        for p in [
            "amino",
            "bcaa",
            "glutamina",
            "carnitina",
            "citrulina",
            "eaa",
            "leucina",
            "arginina",
            "arginine",
            "ornitina",
            "aspártico",
            "aspartico",
            "d-aa",
            "lisina",
            "lysine",
            "taurina",
            "tirosina",
            "tyrosine",
            "triptófano",
            "triptofano",
            "tryptophan",
            "beta-alanina",
            "alanina",
            "hmb",
            "gaba",
            "glutat",
            "histidina",
            "histidine",
            "metionina",
            "methionine",
            "treonina",
            "threonine",
            "fenilalanina",
            "phenylalanine",
            "valina",
            "valine",
            "isoleucina",
            "isoleucine",
            "glicina",
            "glycine",
            "prolina",
            "serina",
            "cisteína",
            "cisteina",
        ]
    ):
        c["categoria"] = CategoriaEnum.aminoacidos.value

    # 6. PRE-ENTRENOS, INTRA Y RENDIMIENTO
    elif any(
        p in n
        for p in [
            "pre-entreno",
            "pre entreno",
            "gel energético",
            "gel energ",
            "evoenergy",
            "electrolito",
            "electrolitos",
            "evolytes",
            "isotónico",
            "isotonico",
            "evotonic",
            "evorecovery",
            "recovery",
            "recuperador",
            "evocarbs",
            "evodextrin",
            "dextrina",
            "ciclodextrina",
            "amilopectina",
            "vitargo",
            "hidratación",
            "hidratacion",
            "evordx",
            "hydrop",
            "pump",
            "nitrico",
            "evobolic",
            "anabolic",
            "cafeína",
            "cafeina",
            "caffeine",
            "teanina",
            "theanine",
        ]
    ):
        c["categoria"] = CategoriaEnum.pre_entrenos.value

    # 7. VITAMINAS Y MINERALES
    elif any(
        p in n
        for p in [
            "vitamin",
            "mineral",
            "magnesio",
            "calcio",
            "zinc",
            "manganeso",
            "cromo",
            "picolinato",
            "potasio",
            "sodio",
            "hierro",
            "yodo",
            "cobre",
            "selenio",
            "evovits",
            "evozma",
            "zma",
            "multivitam",
            "coenzima",
            "b-complex",
            "complejo-b",
        ]
    ):
        c["categoria"] = CategoriaEnum.vitaminas.value

    # 8. SALUD Y BIENESTAR GENERAL (Catch-All de Salud)
    elif any(
        p in n
        for p in [
            "omega",
            "articulacio",
            "digestiv",
            "probiótico",
            "probiotico",
            "extracto",
            "cúrcuma",
            "curcuma",
            "ashwagandha",
            "espirulina",
            "spirulina",
            "ginseng",
            "ginkgo",
            "valeriana",
            "sueño",
            "ansiedad",
            "termogen",
            "evoburn",
            "evodren",
            "detox",
            "d-tox",
            "condroitina",
            "glucosamina",
            "evoptogen",
            "evoblocker",
            "estroblock",
            "glucomanano",
            "evosterone",
            "cla",
            "té verde",
            "resveratrol",
            "maca",
            "saw palmetto",
            "silicio",
            "psyllium",
            "inulina",
            "própolis",
            "hialurónico",
            "mct",
            "aceite de coco",
            "keto",
            "sauce",
            "pack",
            "giftbox",
            "melatonina",
            "aceite",
            "krill",
            "onagra",
            "bacalao",
            "care",
            "digezyme",
            "enzim",
            "enzima",
            "lactasa",
            "pepsina",
            "papaina",
            "msm",
            "uc-ii",
            "uc2",
            "5-htp",
            "5htp",
            "inositol",
            "same",
            "ala",
            "lipoico",
            "astaxantina",
            "coq10",
            "q10",
            "ubiquinol",
            "rutina",
            "antiox",
            "fórmula",
            "formula",
        ]
    ):
        c["categoria"] = CategoriaEnum.salud.value

    else:
        c["categoria"] = CategoriaEnum.salud.value

    # Subfiltros y Sabores
    texto_completo = n + " " + str(desc_limpia or "").lower()
    c["es_vegano"] = (
        True
        if any(
            p in texto_completo
            for p in [
                "apto para veganos",
                "proteína vegana",
                "vegan protein",
                "vegana",
                "vegetal",
                "100% vegano",
            ]
        )
        else False
    )
    c["sin_gluten"] = any(
        p in texto_completo
        for p in [
            "sin gluten",
            "gluten free",
            "gluten-free",
            "libre de gluten",
            "no gluten",
            "0% gluten",
            "apto para celíacos",
            "apto para celiacos",
            "sin trigo",
        ]
    )
    c["sin_lactosa"] = any(
        p in texto_completo
        for p in [
            "sin lactosa",
            "lactose free",
            "lactose-free",
            "libre de lactosa",
            "no lactosa",
            "0% lactosa",
            "zero lactose",
            "lactasa",
            "digezyme",
            "tolarase",
        ]
    )

    # ==========================================
    # 1. FORMATO (Diccionario Súper-Ampliado)
    # ==========================================
    c["formato"] = None
    if any(
        p in n
        for p in [
            "cápsula",
            "capsula",
            "caps",
            "cápsulas",
            "capsulas",
            "comprimido",
            "comprimidos",
            "perla",
            "perlas",
            "tableta",
            "tabletas",
            "tablets",
            "tabs",
            "veg caps",
            "vcap",
            "vcaps",
            "softgel",
            "pastilla",
            "pastillas",
        ]
    ):
        c["formato"] = FormatoEnum.capsulas.value
    elif any(
        p in texto_completo
        for p in [
            "polvo",
            "harina",
            "cacito",
            "scoop",
            "cucharada",
            "cucharadita",
            "cucharaditas",
            "dosificador",
            "batido",
            "soluble",
            "disolución",
            "copos",
            "granulado",
        ]
    ):
        c["formato"] = FormatoEnum.polvo.value
    elif any(
        p in texto_completo
        for p in [
            "vial",
            "viales",
            "gel",
            "geles",
            "líquido",
            "liquido",
            "gotas",
            "liquid",
            "ampolla",
            "ampollas",
            "bebida",
            "ml",
            "jarabe",
            "spray",
            "sirope",
        ]
    ):
        c["formato"] = FormatoEnum.liquido_gel.value
    elif any(
        p in texto_completo
        for p in [
            "barrita",
            "barritas",
            "barra",
            "snack",
            "flapjack",
            "galleta",
            "galletas",
            "cookie",
            "cookies",
            "brownie",
            "bizcocho",
        ]
    ):
        c["formato"] = FormatoEnum.barrita.value
    elif any(
        p in texto_completo
        for p in ["gominola", "gominolas", "gummy", "gummies", "caramelo", "caramelos"]
    ):
        c["formato"] = FormatoEnum.gominolas.value

    if not c["formato"]:
        if c.get("categoria") in [
            CategoriaEnum.proteinas.value,
            CategoriaEnum.creatinas.value,
        ]:
            c["formato"] = FormatoEnum.polvo.value
        elif any(
            p in texto_completo
            for p in ["cazo", "cacito", "scoop", "dosificador", "mezclar", "ml de agua"]
        ):
            c["formato"] = FormatoEnum.polvo.value

    # ==========================================
    # 2. SABORES (Léxico simple + Gourmet)
    # ==========================================
    sabores = []

    if "vainilla" in texto_completo:
        sabores.append(SaborEnum.vainilla.value)
    if any(p in texto_completo for p in ["chocolate", "cacao", "brownie"]):
        sabores.append(SaborEnum.chocolate.value)
    if "fresa" in texto_completo:
        sabores.append(SaborEnum.fresa.value)
    if any(p in texto_completo for p in ["limon", "limón", "citric"]):
        sabores.append(SaborEnum.limon.value)
    if "cookies" in texto_completo or "cream" in texto_completo:
        sabores.append(SaborEnum.cookies.value)
    if "plátano" in texto_completo or "banana" in texto_completo:
        sabores.append(SaborEnum.platano.value)
    if "café" in texto_completo or "capuchino" in texto_completo:
        sabores.append(SaborEnum.cafe.value)
    if "frutas del bosque" in texto_completo or "berry" in texto_completo:
        sabores.append(SaborEnum.frutas.value)
    if "coco" in texto_completo:
        sabores.append(SaborEnum.coco.value)
    if "caramelo" in texto_completo:
        sabores.append(SaborEnum.caramelo.value)
    if "avellana" in texto_completo:
        sabores.append(SaborEnum.avellana.value)
    if "cacahuete" in texto_completo or "peanut" in texto_completo:
        sabores.append(SaborEnum.cacahuete.value)
    if "almendra" in texto_completo:
        sabores.append(SaborEnum.almendra.value)
    if re.search(r"\bmenta\b", texto_completo):
        sabores.append(SaborEnum.menta.value)

    # Solo añadimos "Neutro" si no hemos encontrado sabor Y no es una cápsula
    if not sabores:
        if c.get("formato") != FormatoEnum.capsulas.value:
            sabores.append(SaborEnum.neutro.value)

    c["sabor"] = sabores

    c["tipo_proteina"] = c["porcentaje_proteina"] = c["tipo_creatina"] = c[
        "perfil_aminoacidos"
    ] = c["tipo_vitamina"] = None
    if c["categoria"] == CategoriaEnum.proteinas.value:
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto_completo)
        if any(
            v in texto_completo
            for v in [
                "proteína vegetal",
                "proteina vegetal",
                "vegan protein",
                "proteína de soja",
            ]
        ):
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
        if "micronizada" in texto_completo or "mesh" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.micronizada.value
        elif "kre-alkalyn" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.kre_alkalyn.value
        else:
            c["tipo_creatina"] = TipoCreatinaEnum.monohidrato.value

    elif c["categoria"] == CategoriaEnum.aminoacidos.value:
        if "bcaa" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa.value
        elif "glutamina" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina.value
        elif "eaa" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.eaa.value
        elif "citrulina" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.citrulina.value

    return c
