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
from ingestores.utils import normalizar_descripcion_ui

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

URL_FEED = "https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=256625?token=D496D89D3425492898437BED5EE5EEB677232059"
ARCHIVO_CACHE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cache_ingestores",
    "farma2go_temporal.json",
)

db = SessionLocal()


def descargar_datos():
    return download_json_with_cache(
        url=URL_FEED,
        cache_path=ARCHIVO_CACHE,
        ttl_hours=12,
        timeout=45,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, application/gzip",
        },
    )


def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""
    return texto.lower()


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

    # ---------------------------------------------------------
    # 1. BÚSQUEDA DE UNIDADES (Pastillas, cápsulas, etc.) - ¡AHORA VA PRIMERO!
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. BÚSQUEDA DE PESO (Solo si NO es una pastilla)
    # ---------------------------------------------------------
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
    if not texto:
        return None
    texto = texto.lower()

    # 1. Caza formato explícito "77,3 g de proteína por 100 g"
    m1 = re.search(
        r"(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,20}100\s*g", texto
    )
    if m1:
        return round(float(m1.group(1).replace(",", ".")))

    # 2. Caza formato matemático "23 g de proteína por porción de 30 g" -> Hace (23/30)*100
    m2 = re.search(
        r"(\d{2}(?:[.,]\d+)?)\s*g\s*(?:de\s*)?prote[íi]na[^\d]{1,30}(\d{2,3}(?:[.,]\d+)?)\s*g",
        texto,
    )
    if m2:
        prot = float(m2.group(1).replace(",", "."))
        porcion = float(m2.group(2).replace(",", "."))
        if porcion > 0 and prot <= porcion:
            return round((prot / porcion) * 100)

    # 3. Caza porcentajes atados directamente a la palabra "80% de proteína" o "WPC 80%"
    m3 = re.search(
        r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:prote[íi]na|pureza|wpc|wpi|cfm|whey|aislado)",
        texto,
    )
    if m3:
        return round(float(m3.group(1).replace(",", ".")))

    m4 = re.search(
        r"(?:wpc|wpi|cfm|whey|prote[íi]na|pureza|concentración|proteico)[^\d]{0,20}(\d{2}(?:[.,]\d+)?)\s*%",
        texto,
    )
    if m4:
        return round(float(m4.group(1).replace(",", ".")))

    # 4. Búsqueda Desesperada (Cazador Contextual)
    porcentajes = re.finditer(r"(\d{2}(?:[.,]\d+)?)\s*%", texto)
    for p in porcentajes:
        valor = round(float(p.group(1).replace(",", ".")))
        if 50 <= valor <= 98:
            inicio = max(0, p.start() - 60)
            fin = min(len(texto), p.end() + 60)
            entorno = texto[inicio:fin]
            if any(
                palabra in entorno
                for palabra in [
                    "prote",
                    "pureza",
                    "aislado",
                    "concentrado",
                    "contenido",
                ]
            ):
                return valor

    return None


def clasificar_producto(nombre: str, desc_limpia: str):
    n = nombre.lower()
    texto_completo = n + " " + desc_limpia.lower()
    c = {}

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
    if any(p in n for p in basura_titulo):
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
    if any(p in texto_completo for p in basura_veterinaria):
        return None

    # 2. CATEGORÍA ESTRICTA
    if any(
        p in n
        for p in [
            "harina",
            "copos",
            "mermelada",
            "avena",
            "eritritol",
            "peanut",
            "crema de cacahuete",
            "crema de arroz",
        ]
    ):
        c["categoria"] = CategoriaEnum.alimentacion.value
    elif any(
        p in n
        for p in [
            "gel energético",
            "electrolitos",
            "hidratación",
            "pre-entreno",
            "pre entreno",
            "isotónico",
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
        return None

    # 3. FILTROS GLOBALES
    c["es_vegano"] = (
        True
        if any(
            p in texto_completo
            for p in ["apto para veganos", "proteína vegana", "vegan protein"]
        )
        else False
    )

    # FORMATO PRIMERO (Lo necesitamos para saber qué hacer con los sabores)
    c["formato"] = None
    if any(
        p in texto_completo
        for p in ["cápsula", "capsula", "comprimido", "perla", "pastilla", "tableta"]
    ):
        c["formato"] = FormatoEnum.capsulas.value
    elif any(
        p in texto_completo
        for p in ["polvo", "harina", "copos", "soluble", "disolución", "batido"]
    ):
        c["formato"] = FormatoEnum.polvo.value
    elif any(
        p in texto_completo for p in ["vial", "líquido", "liquid", "bebida", "ampolla"]
    ):
        c["formato"] = FormatoEnum.liquido.value
    elif any(p in texto_completo for p in ["barrita", "barra", "snack"]):
        c["formato"] = FormatoEnum.barrita.value
    elif any(p in texto_completo for p in ["gominola", "gummy"]):
        c["formato"] = FormatoEnum.gominolas.value

    if not c["formato"]:
        if c["categoria"] in [
            CategoriaEnum.proteinas.value,
            CategoriaEnum.creatinas.value,
        ]:
            c["formato"] = FormatoEnum.polvo.value
        elif any(
            p in texto_completo
            for p in ["cazo", "cacito", "scoop", "dosificador", "mezclar", "ml de agua"]
        ):
            c["formato"] = FormatoEnum.polvo.value

    # SABORES (Ahora dependientes del formato)
    sabores_encontrados = []
    if "vainilla" in texto_completo:
        sabores_encontrados.append(SaborEnum.vainilla.value)
    if any(p in texto_completo for p in ["chocolate", "cacao", "brownie"]):
        sabores_encontrados.append(SaborEnum.chocolate.value)
    if "fresa" in texto_completo:
        sabores_encontrados.append(SaborEnum.fresa.value)
    if any(p in texto_completo for p in ["limon", "limón", "citric"]):
        sabores_encontrados.append(SaborEnum.limon.value)
    if "cookies" in texto_completo or "cream" in texto_completo:
        sabores_encontrados.append(SaborEnum.cookies.value)
    if "plátano" in texto_completo or "banana" in texto_completo:
        sabores_encontrados.append(SaborEnum.platano.value)
    if "café" in texto_completo or "capuchino" in texto_completo:
        sabores_encontrados.append(SaborEnum.cafe.value)
    if "frutas del bosque" in texto_completo or "berry" in texto_completo:
        sabores_encontrados.append(SaborEnum.frutas.value)

    # Solo añadimos "Neutro" (Sin sabor) si no es una pastilla/cápsula y no hemos encontrado otro sabor
    if not sabores_encontrados:
        if c["formato"] not in [FormatoEnum.capsulas.value]:
            sabores_encontrados.append(SaborEnum.neutro.value)

    c["sabor"] = sabores_encontrados

    # 4. Objetivos y Sellos (AHORA ES MULTISELECCIÓN Y MÁS LISTO)
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
        c["sello_calidad"] = SelloCalidadEnum.creapure
    elif "kyowa" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.kyowa
    elif "lacprodan" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.lacprodan
    elif "isolac" in texto_completo:
        c["sello_calidad"] = SelloCalidadEnum.isolac

    c["tipo_proteina"] = c["porcentaje_proteina"] = c["tipo_creatina"] = c[
        "perfil_aminoacidos"
    ] = c["tipo_vitamina"] = None

    if c["categoria"] == CategoriaEnum.proteinas.value:
        # 1. Primero determinamos el TIPO de proteína (¡ADIÓS FALSOS POSITIVOS!)
        if any(
            v in texto_completo
            for v in [
                "proteína vegetal",
                "proteina vegetal",
                "vegan protein",
                "proteína de soja",
                "proteina de soja",
                "proteína de guisante",
                "proteína de arroz",
                "proteína de garbanzo",
                "proteína de calabaza",
            ]
        ):
            c["tipo_proteina"] = TipoProteinaEnum.vegetal.value
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
        if "micronizada" in texto_completo or "mesh" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.micronizada
        elif "hcl" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.hcl
        elif "kre-alkalyn" in texto_completo:
            c["tipo_creatina"] = TipoCreatinaEnum.kre_alkalyn
        else:
            c["tipo_creatina"] = TipoCreatinaEnum.monohidrato

    elif c["categoria"] == CategoriaEnum.aminoacidos.value:
        if "bcaa" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.bcaa
        elif "glutamina" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.glutamina
        elif "eaa" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.eaa
        elif "citrulina" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.citrulina
        elif "alanina" in texto_completo:
            c["perfil_aminoacidos"] = PerfilAminoacidosEnum.beta_alanina

    elif c["categoria"] == CategoriaEnum.vitaminas.value:
        if "multivitam" in texto_completo or "complex" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.multivitaminico
        elif "vitamina c" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_c
        elif "vitamina d" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.vitamina_d
        elif "magnesio" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.magnesio
        elif "omega" in texto_completo:
            c["tipo_vitamina"] = TipoVitaminaEnum.omega3

    return c


def inyectar_en_bd():
    print("🔄 Descargando y procesando datos de Farma2Go...")
    datos = descargar_datos()
    if not datos:
        print("⚠️ No se recibieron datos del feed. Se aborta la inserción.")
        return

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
                cat_db = db.query(models.Categoria).filter_by(nombre=cat.value).first()
                if not cat_db:
                    raise
        mapa_categorias[cat.value] = cat_db.id
    productos_nuevos = []
    cache_marcas = {}
    print("🧹 Cargando catálogo antiguo de Farma2Go en memoria (Upsert)...")
    productos_bd = {
        p.slug: p for p in db.query(models.Producto).filter_by(tienda="Farma2Go").all()
    }
    print(f"✨ {len(productos_bd)} productos en memoria. Iniciando ingesta...")

    for item in datos.get("products", []):
        nombre = html.unescape(item.get("name", "Sin nombre"))
        desc_cruda = item.get("description", "")
        desc_limpia = limpiar_texto(desc_cruda)
        descripcion_ui = normalizar_descripcion_ui(desc_cruda)

        # FILTRO EXTREMO DE CATEGORÍAS JSON
        categorias_json = [
            c.get("name", "").lower() for c in item.get("categories", [])
        ]
        categorias_prohibidas = [
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
        if any(
            prohibida in cat
            for cat in categorias_json
            for prohibida in categorias_prohibidas
        ):
            continue

        etiquetas = clasificar_producto(nombre, desc_limpia)
        if not etiquetas:
            continue

        # LIMPIEZA DE MARCA
        marca_cruda = item.get("brand", "Desconocida")
        # Si la marca es muy larga o tiene caracteres raros, la descartamos
        if len(marca_cruda) > 30 or any(
            char in marca_cruda for char in ["/", "\\", ":", ";"]
        ):
            marca_cruda = "Desconocida"

        nombre_marca = normalizar_marca(marca_cruda)

        if nombre_marca not in cache_marcas:
            marca_db = db.query(models.Marca).filter_by(nombre=nombre_marca).first()
            if not marca_db:
                try:
                    marca_db = models.Marca(nombre=nombre_marca)
                    db.add(marca_db)
                    db.commit()
                    db.refresh(marca_db)
                except Exception:
                    db.rollback()
                    marca_db = (
                        db.query(models.Marca).filter_by(nombre=nombre_marca).first()
                    )
                    if not marca_db:
                        raise
            cache_marcas[nombre_marca] = marca_db.id

        precio = 0.0
        precio_anterior = None
        afiliado_url = ""
        ofertas = item.get("offers", [])
        if ofertas:
            afiliado_url = ofertas[0].get("productUrl", "")

            # 1. Intentamos sacar el precio rebajado y el original de la API
            oferta = ofertas[0]
            if "price" in oferta and isinstance(oferta["price"], dict):
                precio = float(oferta["price"].get("value", 0.0))

            if "previousPrice" in oferta and isinstance(oferta["previousPrice"], dict):
                p_previo = float(oferta["previousPrice"].get("value", 0.0))
                if p_previo > precio:
                    precio_anterior = p_previo

            # 2. Respaldo antiguo (Historial) por si falla lo de arriba
            if precio == 0.0:
                historial = oferta.get("priceHistory", [])
                if historial and "price" in historial[0]:
                    precio = float(historial[0]["price"].get("value", 0))

        imagen_url = item.get("productImage", {}).get("url", "")

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
            p_existente.marca_id = cache_marcas[nombre_marca]
            p_existente.categoria_id = categoria_id
            p_existente.sabor = etiquetas["sabor"]
            p_existente.formato = etiquetas["formato"]
            p_existente.objetivo = etiquetas["objetivo"]
            p_existente.es_vegano = etiquetas["es_vegano"]
            p_existente.sin_gluten = bool(etiquetas.get("sin_gluten"))
            p_existente.sin_lactosa = bool(etiquetas.get("sin_lactosa"))
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
        else:
            nuevo_producto = models.Producto(
                nombre=nombre,
                descripcion=descripcion_ui,
                precio=precio,
                precio_anterior=precio_anterior,
                imagen_url=imagen_url,
                afiliado_url=afiliado_url,
                tienda="Farma2Go",
                marca_id=cache_marcas[nombre_marca],
                categoria_id=categoria_id,
                sabor=etiquetas["sabor"],
                formato=etiquetas["formato"],
                objetivo=etiquetas["objetivo"],
                es_vegano=etiquetas["es_vegano"],
                sin_gluten=bool(etiquetas.get("sin_gluten")),
                sin_lactosa=bool(etiquetas.get("sin_lactosa")),
                sello_calidad=etiquetas["sello_calidad"],
                tipo_proteina=etiquetas["tipo_proteina"],
                porcentaje_proteina=etiquetas["porcentaje_proteina"],
                tipo_creatina=etiquetas["tipo_creatina"],
                perfil_aminoacidos=etiquetas["perfil_aminoacidos"],
                tipo_vitamina=etiquetas["tipo_vitamina"],
                peso_gramos=metricas["peso_gramos"],
                precio_por_kg=metricas["precio_por_kg"],
                slug=slug_norm,
            )
            productos_nuevos.append(nuevo_producto)
            productos_bd[slug_norm] = nuevo_producto

    db.add_all(productos_nuevos)
    db.commit()
    print(
        f"\n🎉 ¡Inyección de Farma2Go completada! {len(productos_nuevos)} suplementos reales guardados."
    )


if __name__ == "__main__":
    inyectar_en_bd()
