import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
import html
import unicodedata

import models
from database import SessionLocal
from ingestores.http_client import download_json_with_cache
from ingestores.utils import normalizar_descripcion_ui, extraer_presentacion
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
    normalizar_marca,
)

URL_FEED = "https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=108208?token=D496D89D3425492898437BED5EE5EEB677232059"
ARCHIVO_CACHE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cache_ingestores",
    "sportlive_temporal.json",
)
DOMINIO_TIENDA = "https://sportlivenutrition.com"


def descargar_datos():
    return download_json_with_cache(
        url=URL_FEED,
        cache_path=ARCHIVO_CACHE,
        ttl_hours=12,
        timeout=45,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SuplementosComparatorBot/1.0",
            "Accept": "application/json, application/gzip",
        },
    )


# --- MATEMÁTICAS Y LIMPIEZA ---
def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    if "una combinación ganadora" in texto:
        return texto[: texto.find("una combinación ganadora")]
    return texto


def generar_slug(nombre: str) -> str:
    texto = (
        unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("utf-8")
    )
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def calcular_metricas_precio(item: dict, precio: float):
    nombre = item.get("name", "").lower()
    peso_json = str(item.get("weight", "")).lower()

    metricas = {
        "peso_gramos": None,
        "precio_por_kg": None,
        "unidades": None,
        "precio_por_unidad": None,
    }

    # 1. BÚSQUEDA DE UNIDADES
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

    # 2. BÚSQUEDA DE PESO
    if not es_pastilla:
        textos_donde_buscar = [peso_json, nombre]
        for texto in textos_donde_buscar:
            if not texto:
                continue
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


def extraer_porcentaje_proteina(texto: str):
    m = re.search(r"(\d{2,3})\s*%\s*(?:de\s*)?(?:prote[íi]na|pureza)", texto)
    if m:
        return int(m.group(1))
    m2 = re.search(r"prote[íi]na[^\d]{0,20}(\d{2,3})\s*%", texto)
    if m2:
        return int(m2.group(1))
    return None


def clasificar_producto(nombre: str, desc_limpia: str):
    n = nombre.lower()
    texto_completo = n + " " + desc_limpia.lower()
    c = {}

    # 1. FILTRO DE BASURA (Mejorado con límites de palabra \b)
    basura_titulo = ["shaker", "mezclador", "botella", "toalla", "camiseta"]
    if any(re.search(r"\b" + p + r"\b", n) for p in basura_titulo):
        return None

    # 1.2 FILTRO VETERINARIO (Mejorado)
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

    if any(
        p in n
        for p in [
            "crema",
            "harina",
            "copos",
            "mermelada",
            "avena",
            "eritritol",
            "peanut",
        ]
    ):
        c["categoria"] = CategoriaEnum.alimentacion.value
    elif any(
        p in n
        for p in [
            "gel",
            "electrolitos",
            "hidratación",
            "boom",
            "pre-entreno",
            "pre entreno",
            "hydrop",
        ]
    ):
        c["categoria"] = CategoriaEnum.pre_entrenos.value
    elif any(
        p in n
        for p in ["whey", "protein", "proteína", "proteina", "isolate", "aislado"]
    ):
        c["categoria"] = CategoriaEnum.proteinas.value
    elif "creatin" in n:
        c["categoria"] = CategoriaEnum.creatinas.value
    elif any(p in n for p in ["amino", "bcaa", "glutamina", "carnitina"]):
        c["categoria"] = CategoriaEnum.aminoacidos.value
    elif any(
        p in n
        for p in [
            "vitamin",
            "mineral",
            "magnesio",
            "calcio",
            "zinc",
            "omega",
            "colágeno",
        ]
    ):
        c["categoria"] = CategoriaEnum.vitaminas.value
    else:
        c["categoria"] = CategoriaEnum.otros.value

    # FILTROS DIETÉTICOS MEJORADOS
    c["es_vegano"] = any(
        p in texto_completo
        for p in [
            "vegano",
            "vegana",
            "vegan ",
            " vegan",
            "veggie",
            "plant-based",
            "plant based",
            "apto para veganos",
            "origen vegetal",
            "100% vegetal",
        ]
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
            "dairy free",
            "dairy-free",
            "sin lácteos",
        ]
    )

    # SELLOS DE CALIDAD COMPLETOS
    c["sello_calidad"] = None
    if "creapure" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.creapure.value
    elif "kyowa" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.kyowa.value
    elif "lacprodan" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.lacprodan.value
    elif "isolac" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.isolac.value
    elif "optipep" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.optipep.value
    elif "carnipure" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.carnipure.value

    # ==========================================
    # 1. FORMATO (Recuperado de versión estable)
    # ==========================================
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

    objetivos = []
    if any(
        p in texto_completo
        for p in ["volumen", "gainer", "masa", "crecimiento", "aumento"]
    ):
        objetivos.append(ObjetivoEnum.volumen.value)
    if any(
        p in texto_completo
        for p in [
            "peso",
            "quema",
            "termogénico",
            "definición",
            "adelgazar",
            "grasa",
            "keto",
        ]
    ):
        objetivos.append(ObjetivoEnum.definicion.value)
    if any(
        p in texto_completo
        for p in [
            "rendimiento",
            "energía",
            "fuerza",
            "recuperación",
            "resistencia",
            "entrenamiento",
            "post-entreno",
        ]
    ):
        objetivos.append(ObjetivoEnum.rendimiento.value)
    if any(
        p in texto_completo
        for p in [
            "salud",
            "articular",
            "bienestar",
            "inmune",
            "digestión",
            "hueso",
            "articulaciones",
            "omega",
            "vitamin",
        ]
    ):
        objetivos.append(ObjetivoEnum.salud.value)
    c["objetivo"] = objetivos if objetivos else None

    c["sello_calidad"] = None
    if "creapure" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.creapure.value
    elif "kyowa" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.kyowa.value
    elif "lacprodan" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.lacprodan.value
    elif "isolac" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.isolac.value

    c["tipo_proteina"] = c["porcentaje_proteina"] = c["tipo_creatina"] = c[
        "perfil_aminoacidos"
    ] = c["tipo_vitamina"] = None
    if c["categoria"] == CategoriaEnum.proteinas.value:
        c["porcentaje_proteina"] = extraer_porcentaje_proteina(texto_completo)
        if "isolate" in texto_completo or "aislado" in texto_completo:
            c["tipo_proteina"] = TipoProteinaEnum.isolate.value
        elif "vegetal" in texto_completo or "vegan" in texto_completo:
            c["tipo_proteina"] = TipoProteinaEnum.vegetal.value
        elif "caseina" in texto_completo or "casein" in texto_completo:
            c["tipo_proteina"] = TipoProteinaEnum.caseina.value
        elif "hidrolizado" in texto_completo:
            c["tipo_proteina"] = TipoProteinaEnum.hidrolizado.value
        else:
            c["tipo_proteina"] = TipoProteinaEnum.whey.value
    elif c["categoria"] == CategoriaEnum.creatinas.value:
        if "micronizada" in texto_completo or "mesh" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.micronizada.value
        elif "hcl" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.hcl.value
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
        elif "alanina" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.beta_alanina.value
    elif c["categoria"] == CategoriaEnum.vitaminas.value:
        if "multivitam" in texto_completo or "complex" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.multivitaminico.value
        elif "vitamina c" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_c.value
        elif "vitamina d" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_d.value
        elif "magnesio" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.magnesio.value
        elif "omega" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.omega3.value

    return c


# --- RUTINA DE INYECCIÓN ---
def inyectar_en_bd():
    db = SessionLocal()
    try:
        print("🔄 Vaciando datos antiguos de Sportlive...")
        nombre_marca = normalizar_marca("Drasanvi")
        marca_oficial = db.query(models.Marca).filter_by(nombre=nombre_marca).first()
        if not marca_oficial:
            try:
                marca_oficial = models.Marca(nombre=nombre_marca)
                db.add(marca_oficial)
                db.commit()
                db.refresh(marca_oficial)
            except Exception:
                db.rollback()
                marca_oficial = (
                    db.query(models.Marca).filter_by(nombre=nombre_marca).first()
                )
                if not marca_oficial:
                    raise
        else:
            pass

        # CATEGORÍAS
        mapa_categorias = {}
        for cat in CategoriaEnum:
            cat_db = db.query(models.Categoria).filter_by(nombre=cat.value).first()
            if not cat_db:
                try:
                    cat_db = models.Categoria(nombre=cat.value)
                    db.add(cat_db)
                    db.commit()
                    db.refresh(cat_db)
                except Exception:
                    db.rollback()
                    cat_db = (
                        db.query(models.Categoria).filter_by(nombre=cat.value).first()
                    )
                    if not cat_db:
                        raise
            mapa_categorias[cat.value] = cat_db.id

        print("🧹 Cargando catálogo antiguo de Sportlive en memoria (Upsert)...")
        productos_bd = {
            p.slug: p
            for p in db.query(models.Producto).filter_by(tienda="Sportlive").all()
        }
        print(f"✨ {len(productos_bd)} productos en memoria. Iniciando ingesta...")

        datos = descargar_datos()
        productos_nuevos = []

        for item in datos.get("products", []):
            nombre = html.unescape(item.get("name", "Sin nombre"))
            desc_cruda = item.get("description", "")
            desc_limpia = limpiar_texto(desc_cruda)
            descripcion_ui = normalizar_descripcion_ui(desc_cruda)

            etiquetas = clasificar_producto(nombre, desc_limpia)
            if not etiquetas:
                continue

            presentacion_ext = extraer_presentacion(nombre)

            precio = 0.0
            precio_anterior = None
            afiliado_url = ""
            ofertas = item.get("offers", [])

            if ofertas:
                oferta = ofertas[0]
                afiliado_url = oferta.get("productUrl", "")

                if "price" in oferta and isinstance(oferta["price"], dict):
                    precio = float(oferta["price"].get("value", 0.0))

                if "previousPrice" in oferta and isinstance(
                    oferta["previousPrice"], dict
                ):
                    p_previo = float(oferta["previousPrice"].get("value", 0.0))
                    if p_previo > precio:
                        precio_anterior = p_previo

                if precio == 0.0:
                    historial = oferta.get("priceHistory", [])
                    if historial and "price" in historial[0]:
                        precio = float(historial[0]["price"].get("value", 0))

            img = item.get("productImage", {}).get("url", "")
            imagen_url = (
                img
                if img.startswith("http")
                else f"{DOMINIO_TIENDA}{img}" if img else ""
            )

            metricas = calcular_metricas_precio(item, precio)

            categoria_id = mapa_categorias.get(etiquetas["categoria"])
            if not categoria_id:
                categoria_id = next(iter(mapa_categorias.values()))

            slug_norm = generar_slug(nombre)
            if slug_norm in productos_bd:
                p_existente = productos_bd[slug_norm]
                p_existente.nombre = nombre
                p_existente.descripcion = descripcion_ui
                p_existente.imagen_url = imagen_url
                p_existente.afiliado_url = afiliado_url
                p_existente.marca_id = marca_oficial.id
                p_existente.categoria_id = categoria_id
                p_existente.sabor = etiquetas["sabor"]
                p_existente.formato = etiquetas["formato"]
                p_existente.objetivo = etiquetas["objetivo"]
                p_existente.es_vegano = etiquetas["es_vegano"]
                p_existente.sello_calidad = etiquetas["sello_calidad"]
                p_existente.tipo_proteina = etiquetas["tipo_proteina"]
                p_existente.porcentaje_proteina = etiquetas["porcentaje_proteina"]
                p_existente.tipo_creatina = etiquetas["tipo_creatina"]
                p_existente.perfil_aminoacidos = etiquetas["perfil_aminoacidos"]
                p_existente.tipo_vitamina = etiquetas["tipo_vitamina"]
                p_existente.peso_gramos = metricas["peso_gramos"]
                p_existente.precio_por_kg = metricas["precio_por_kg"]

                if precio_anterior is not None:
                    p_existente.precio_anterior = precio_anterior
                    p_existente.precio = precio
                else:
                    if precio < p_existente.precio:
                        p_existente.precio_anterior = float(p_existente.precio)
                        p_existente.precio = precio
                    elif precio > p_existente.precio:
                        p_existente.precio_anterior = None
                        p_existente.precio = precio
                        
                # Forzar actualización explícita si hay un cambio real en la presentación
                if presentacion_ext and p_existente.presentacion != presentacion_ext:
                    p_existente.presentacion = presentacion_ext
                    db.add(p_existente)
                    db.commit()
            else:
                nuevo_producto = models.Producto(
                    nombre=nombre,
                    descripcion=descripcion_ui,
                    precio=precio,
                    precio_anterior=precio_anterior,
                    imagen_url=imagen_url,
                    afiliado_url=afiliado_url,
                    tienda="Sportlive",
                    marca_id=marca_oficial.id,
                    categoria_id=categoria_id,
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
                    presentacion=presentacion_ext,
                    slug=slug_norm,
                )
                productos_nuevos.append(nuevo_producto)
                productos_bd[slug_norm] = nuevo_producto

        db.add_all(productos_nuevos)
        db.commit()
        print(
            f"\n🎉 ¡Limpieza completada! {len(productos_nuevos)} productos de {nombre_marca} guardados perfectamente estructurados."
        )

    except Exception as e:
        print(f"❌ ERROR INESPERADO en Sportlive: {e}")
        db.rollback()
    finally:
        db.close()
        print("🚪 Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    inyectar_en_bd()
