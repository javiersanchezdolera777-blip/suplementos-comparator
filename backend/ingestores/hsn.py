import sys
import os

# 1. ESTO TIENE QUE SER LO PRIMERO QUE LEA PYTHON
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. AHORA SÍ, EMPIEZAN LAS IMPORTACIONES LOCALES
from ingestores.utils import clasificar_producto
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
from ingestores.http_client import create_session, get_with_backoff
from database import SessionLocal
import models
import random
import time
import traceback
import requests
from bs4 import BeautifulSoup
import json
import base64
import re
import unicodedata

db = SessionLocal()

# ==========================================
# 1. EL MAPA DE CATEGORÍAS (URLs Limpias)
# ...

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
    "https://www.hsnstore.com/alimentacion-saludable/snacks-y-tentempies",
]

# ==========================================
# 2. HERRAMIENTAS Y MATEMÁTICAS
# ==========================================


def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""
    return re.sub(r"<[^>]+>", " ", texto).lower()


def generar_slug(nombre: str) -> str:
    texto = (
        unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("utf-8")
    )
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def generar_enlace_afiliado(url_producto: str) -> str:
    cadena = f"product||0||SUPARATOR||{url_producto}"
    link_id = base64.b64encode(cadena.encode("utf-8")).decode("utf-8")
    return f"https://www.hsnstore.com/affiliate/click/index?linkid={link_id}"


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


def calcular_metricas_precio(nombre: str, descripcion: str, precio: float):
    metricas = {
        "peso_gramos": None,
        "precio_por_kg": None,
        "unidades": None,
        "precio_por_unidad": None,
    }
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

    if not es_pastilla:
        for texto in [nombre, descripcion]:
            if not texto:
                continue
            patron = r"(\d+(?:[.,]\d+)?)\s*(kg|kilo|kilos|g|gr|gramos|lbs|lb|libra|ml|l|litros)\b"
            coincidencias = list(re.finditer(patron, texto))
            peso_encontrado = False

            for match in reversed(coincidencias):
                cantidad = float(match.group(1).replace(",", "."))
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
            if peso_encontrado:
                break

    return metricas


# ==========================================
# 3. EL CEREBRO CLASIFICADOR (V2 - Mejorado)
# ==========================================
# ==========================================
# 4. INYECCIÓN PRINCIPAL BLINDADA
# ==========================================


def inyectar_en_bd():
    db = SessionLocal()

    try:
        nombre_marca = normalizar_marca("HSN")
        marca_hsn = db.query(models.Marca).filter_by(nombre=nombre_marca).first()
        if not marca_hsn:
            try:
                marca_hsn = models.Marca(nombre=nombre_marca)
                db.add(marca_hsn)
                db.commit()
                db.refresh(marca_hsn)
            except Exception:
                db.rollback()
                marca_hsn = (
                    db.query(models.Marca).filter_by(nombre=nombre_marca).first()
                )
                if not marca_hsn:
                    raise

        print("🧹 Cargando catálogo antiguo de HSN en memoria (Upsert)...")
        productos_bd = {
            p.slug: p for p in db.query(models.Producto).filter_by(tienda="HSN").all()
        }
        print(f"✨ {len(productos_bd)} productos en memoria. Iniciando ingesta...")

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
    except Exception as e:
        db.rollback()
        print(f"❌ Error al inicializar BBDD: {e}")
        return

    session = create_session(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Referer": "https://www.hsnstore.com/",
        }
    )

    productos_nuevos = []
    enlaces_procesados = set()
    total_general = 0

    for url_cat in URLS_OBJETIVO:
        print(f"\n🌐 Explorando: {url_cat}")
        cat_count = 0
        pagina = 1
        try:
            max_paginas = int(os.getenv("HSN_MAX_PAGES", "50"))
        except Exception:
            max_paginas = 50

        while pagina <= max_paginas:
            url_pagina = f"{url_cat}?p={pagina}" if pagina > 1 else url_cat
            try:
                try:
                    res_cat = get_with_backoff(session, url_pagina, timeout=30)
                except Exception as net_err:
                    print(f"   ⚠️ No se pudo cargar la página {url_pagina}: {net_err}")
                    break

                if res_cat.status_code != 200:
                    print(
                        f"   ⚠️ Página {pagina} devolvió {res_cat.status_code}. Saltando categoría."
                    )
                    break
                try:
                    soup_cat = BeautifulSoup(res_cat.text, "lxml")
                except Exception:
                    soup_cat = BeautifulSoup(res_cat.text, "html.parser")

                enlaces_pagina = [
                    a.get("href")
                    for a in soup_cat.select(".product-item-link")
                    if a.get("href")
                ]

                if not enlaces_pagina:
                    break

                print(
                    f"   📄 Procesando página {pagina} ({len(enlaces_pagina)} productos)..."
                )

                for url_prod in enlaces_pagina:
                    if url_prod in enlaces_procesados:
                        continue
                    enlaces_procesados.add(url_prod)

                    try:
                        try:
                            res_prod = get_with_backoff(session, url_prod, timeout=20)
                        except Exception as net_err:
                            print(
                                f"      ⚠️ No se pudo cargar el producto {url_prod}: {net_err}"
                            )
                            continue

                        if res_prod.status_code != 200:
                            print(
                                f"      ⚠️ Producto {url_prod} devolvió {res_prod.status_code}. Continuando..."
                            )
                            continue
                        # Preferir extraer JSON-LD sin parsear todo el HTML (ahorra trabajo a lxml)
                        datos_producto = None
                        try:
                            # Buscar bloques <script type="application/ld+json">...</script>
                            bloques = re.findall(
                                r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                                res_prod.text,
                                flags=re.S | re.I,
                            )
                            for bloque in bloques:
                                try:
                                    contenido = json.loads(bloque.strip())
                                    if (
                                        isinstance(contenido, dict)
                                        and contenido.get("@type") == "Product"
                                    ):
                                        datos_producto = contenido
                                        break
                                    if isinstance(contenido, list):
                                        for item in contenido:
                                            if (
                                                isinstance(item, dict)
                                                and item.get("@type") == "Product"
                                            ):
                                                datos_producto = item
                                                break
                                        if datos_producto:
                                            break
                                except Exception:
                                    continue
                        except Exception:
                            datos_producto = None

                        # Siempre crear BeautifulSoup para los fallbacks visuales
                        try:
                            soup_prod = BeautifulSoup(res_prod.text, "html.parser")
                        except Exception:
                            try:
                                soup_prod = BeautifulSoup(res_prod.text, "lxml")
                            except Exception:
                                print(
                                    f"      ⚠️ Fallo al parsear HTML de {url_prod}. Saltando producto."
                                )
                                continue

                        if not datos_producto:
                            datos_producto = {}

                        # 1. Nombre (Ajuste para coger el og:title real)
                        nombre = datos_producto.get("name") if datos_producto else None
                        if not nombre:
                            title_tags = soup_prod.find_all("meta", property="og:title")
                            if title_tags:
                                nombre = (
                                    title_tags[-1]
                                    .get("content", "")
                                    .split("|")[0]
                                    .strip()
                                )
                            else:
                                title_h1 = soup_prod.find("h1", class_="page-title")
                                nombre = (
                                    title_h1.get_text(strip=True) if title_h1 else None
                                )

                        if not nombre:
                            continue  # Si no podemos sacar ni el título, descartamos

                        # 2. Imagen y Descripción
                        imagen = datos_producto.get("image")
                        if not imagen:
                            img_tag = soup_prod.find("meta", property="og:image")
                            imagen = img_tag.get("content", "") if img_tag else ""

                        desc_cruda = datos_producto.get("description")
                        if not desc_cruda:
                            desc_tag = soup_prod.find("meta", property="og:description")
                            desc_cruda = desc_tag.get("content", "") if desc_tag else ""

                        # 🎯 EXTRACCIÓN DE MARCA (4 FASES): A prueba de fallos absolutos
                        brand_raw = "HSN"

                        # 1. FASE 1: JSON-LD (Schema.org)
                        if datos_producto:
                            brand_info = datos_producto.get("brand")
                            if isinstance(brand_info, dict):
                                brand_candidata = brand_info.get("name", "")
                                if (
                                    brand_candidata
                                    and brand_candidata.strip().upper() != "HSN"
                                ):
                                    brand_raw = brand_candidata.strip().title()
                            elif (
                                isinstance(brand_info, str)
                                and brand_info.strip().upper() != "HSN"
                            ):
                                brand_raw = brand_info.strip().title()

                        # 2. FASE 2: ESTRUCTURA DE LA URL (Soporte para /marcas/)
                        if brand_raw.upper() == "HSN":
                            if "/marcas/" in url_prod:
                                try:
                                    partes_url = url_prod.split("/marcas/")
                                    if len(partes_url) > 1:
                                        posible_marca = (
                                            partes_url[1].split("/")[0].strip().lower()
                                        )
                                        gamas_hsn = [
                                            "hsn",
                                            "hsn-accessories",
                                            "essential-series",
                                            "raw-series",
                                            "sport-series",
                                            "food-series",
                                        ]
                                        if (
                                            posible_marca
                                            and posible_marca not in gamas_hsn
                                        ):
                                            brand_raw = posible_marca.replace(
                                                "-", " "
                                            ).title()
                                except Exception:
                                    pass

                        # 3. FASE 3: FRANCOTIRADOR VISUAL HTML (Cualquier enlace que apunte a /marcas/)
                        if (
                            brand_raw.upper() == "HSN"
                            and "soup_prod" in locals()
                            and soup_prod
                        ):
                            # Buscamos de forma flexible cualquier enlace que contenga /marcas/ en su href
                            enlaces_marca = soup_prod.find_all(
                                "a", href=re.compile(r"/marcas/([^/]+)", re.I)
                            )
                            for a in enlaces_marca:
                                href_val = a.get("href", "")
                                # Extraer la marca directamente del href si es limpia (ej: /marcas/swanson)
                                match_href = re.search(
                                    r"/marcas/([^/?]+)", href_val, re.I
                                )
                                if match_href:
                                    posible = match_href.group(1).strip().lower()
                                    gamas_hsn = [
                                        "hsn",
                                        "hsn-accessories",
                                        "essential-series",
                                        "raw-series",
                                        "sport-series",
                                        "food-series",
                                    ]
                                    if posible and posible not in gamas_hsn:
                                        brand_raw = posible.replace("-", " ").title()
                                        break
                                # Fallback al texto del enlace si es corto y válido
                                texto = a.get_text(strip=True)
                                if texto and texto.upper() != "HSN" and len(texto) < 25:
                                    brand_raw = texto
                                    break

                        # 4. FASE 4: MOTOR REGEX DE LISTA BLANCA (Nombre, URL, Title y Descripción HTML)
                        if brand_raw.upper() == "HSN":
                            marcas_blancas = [
                                r"Swanson",
                                r"Lamberts",
                                r"Amix",
                                r"NOW Foods",
                                r"Vitaminalia",
                                r"Optimum Nutrition",
                                r"Scitec Nutrition",
                                r"BiotechUSA",
                                r"Cellucor",
                                r"Dymatize",
                                r"Muscletech",
                                r"Quamtrax",
                                r"Life Pro",
                                r"Big Nutrition",
                                r"Solgar",
                                r"Soria Natural",
                                r"Ana Maria Lajusticia",
                                r"Solaray",
                                r"Natrol",
                                r"Jarrow Formulas",
                                r"Life Extension",
                                r"Weider",
                            ]
                            patron_regex = r"\b(" + "|".join(marcas_blancas) + r")\b"

                            # A) Buscar en el nombre del producto
                            match = re.search(
                                patron_regex, nombre if nombre else "", re.IGNORECASE
                            )

                            # B) Buscar en la URL del producto
                            if not match:
                                match = re.search(patron_regex, url_prod, re.IGNORECASE)

                            # C) Buscar en la etiqueta <title> de la página
                            if (
                                not match
                                and "soup_prod" in locals()
                                and soup_prod.find("title")
                            ):
                                match = re.search(
                                    patron_regex,
                                    soup_prod.find("title").text,
                                    re.IGNORECASE,
                                )

                            # D) Buscar en el texto general del HTML (por si la marca aparece en la descripción de fabricante)
                            if not match and "soup_prod" in locals() and soup_prod:
                                match = re.search(
                                    patron_regex, soup_prod.get_text(), re.IGNORECASE
                                )

                            if match:
                                brand_raw = match.group(1).title()

                        marca_final = normalizar_marca(brand_raw)
                        marca_actual = (
                            db.query(models.Marca).filter_by(nombre=marca_final).first()
                        )
                        if not marca_actual:
                            try:
                                marca_actual = models.Marca(nombre=marca_final)
                                db.add(marca_actual)
                                db.commit()
                                db.refresh(marca_actual)
                            except Exception:
                                db.rollback()
                                marca_actual = marca_hsn

                        # HARD SKIP: Detección de Agotados vía meta tag estructurado
                        disp_meta = soup_prod.find(
                            "meta", property="product:availability"
                        )
                        if (
                            disp_meta
                            and "outofstock" in disp_meta.get("content", "").lower()
                        ):
                            continue  # El producto está agotado, lo saltamos

                        precio = 0.0
                        precio_anterior = None

                        # Extracción de precios limpia y directa desde el <head>
                        sale_tag = soup_prod.find(
                            "meta", property="product:sale_price:amount"
                        )
                        base_tag = soup_prod.find(
                            "meta", property="product:price:amount"
                        )

                        try:
                            p_sale = (
                                float(sale_tag["content"])
                                if sale_tag and sale_tag.get("content")
                                else 0.0
                            )
                            p_base = (
                                float(base_tag["content"])
                                if base_tag and base_tag.get("content")
                                else 0.0
                            )

                            if p_sale > 0 and p_base > p_sale:
                                precio = p_sale
                                precio_anterior = p_base
                            elif p_base > 0:
                                precio = p_base
                            elif p_sale > 0:
                                precio = p_sale
                        except (ValueError, TypeError):
                            pass

                        if precio <= 0:
                            continue  # Descarte de seguridad si el producto no tiene un precio válido

                        # --- NUEVO: CAZADOR DE PESOS OCULTOS PARA HSN ---
                        # Campos adicionales desde HTML solo si tenemos soup_prod
                        titulo_pagina = ""
                        texto_talla = ""
                        if "soup_prod" in locals():
                            try:
                                titulo_pagina = (
                                    soup_prod.find("title").text
                                    if soup_prod.find("title")
                                    else ""
                                )
                                opcion_marcada = soup_prod.find(
                                    class_=re.compile(r"swatch-option.*selected")
                                )
                                texto_talla = (
                                    opcion_marcada.text if opcion_marcada else ""
                                )
                            except Exception:
                                titulo_pagina = ""
                                texto_talla = ""
                        nombre_ampliado = (
                            f"{nombre} {titulo_pagina} {texto_talla}".lower()
                        )
                        # ------------------------------------------------

                        # --- NUEVO: CAZADOR DE SABORES OCULTOS PARA HSN ---
                        opciones_sabor = soup_prod.find_all(
                            attrs={"option-label": True}
                        )
                        textos_sabores = [
                            op.get("option-label", "") for op in opciones_sabor
                        ]

                        # Plan B por si usan clases en lugar de option-label
                        if not textos_sabores:
                            swatches = soup_prod.find_all(
                                class_=re.compile(r"swatch-option")
                            )
                            textos_sabores = [s.text for s in swatches]

                        texto_sabores_extra = " ".join(textos_sabores).lower()
                        # ------------------------------------------------------------

                        desc_limpia = limpiar_texto(desc_cruda)
                        # Fusionamos la descripción limpia con los sabores ocultos que hemos cazado
                        desc_ampliada_para_cerebro = (
                            f"{desc_limpia} {texto_sabores_extra}"
                        )
                        etiquetas = clasificar_producto(
                            nombre, desc_ampliada_para_cerebro
                        )

                        if not etiquetas or not etiquetas.get("categoria"):
                            continue

                        metricas = calcular_metricas_precio(
                            nombre_ampliado, desc_limpia, precio
                        )
                        url_afiliado = generar_enlace_afiliado(url_prod)

                        # Normalizar tipos y proteger contra valores no serializables
                        try:
                            nombre_norm = str(nombre)[:255]
                            descripcion_norm = str(desc_limpia)[:900]
                            precio_norm = float(precio or 0.0)
                            precio_ant_norm = (
                                float(precio_anterior)
                                if precio_anterior not in (None, "", 0)
                                else None
                            )
                            slug_norm = generar_slug(nombre_norm)
                            peso_norm = (
                                int(metricas.get("peso_gramos"))
                                if metricas.get("peso_gramos")
                                else None
                            )
                            preciokg_norm = (
                                float(metricas.get("precio_por_kg"))
                                if metricas.get("precio_por_kg")
                                else None
                            )
                            porcentaje_proteina = etiquetas.get("porcentaje_proteina")
                            try:
                                porcentaje_proteina = (
                                    int(porcentaje_proteina)
                                    if porcentaje_proteina is not None
                                    else None
                                )
                            except Exception:
                                porcentaje_proteina = None

                            objetivo_norm = etiquetas.get("objetivo")
                            if isinstance(objetivo_norm, str):
                                objetivo_norm = [objetivo_norm]
                            sabor_norm = etiquetas.get("sabor")
                            if sabor_norm is None:
                                sabor_norm = []

                            categoria_id = mapa_categorias.get(
                                etiquetas.get("categoria")
                            )
                            if not categoria_id:
                                continue

                            if slug_norm in productos_bd:
                                p_existente = productos_bd[slug_norm]
                                p_existente.nombre = nombre_norm
                                p_existente.descripcion = descripcion_norm
                                p_existente.imagen_url = str(imagen) if imagen else None
                                p_existente.afiliado_url = url_afiliado
                                # 🛡️ ESCUDO UPSERT PARA MARCAS:
                                # Si el producto ya tenía una marca externa y el scraper devuelve HSN, NO lo pisamos.
                                if (
                                    p_existente.marca_id != marca_hsn.id
                                    and marca_actual.id == marca_hsn.id
                                ):
                                    pass  # Respetamos la marca externa
                                else:
                                    p_existente.marca_id = marca_actual.id
                                p_existente.categoria_id = categoria_id
                                p_existente.sabor = sabor_norm
                                p_existente.formato = etiquetas.get("formato")
                                p_existente.objetivo = objetivo_norm
                                p_existente.es_vegano = bool(etiquetas.get("es_vegano"))
                                p_existente.sin_gluten = bool(
                                    etiquetas.get("sin_gluten")
                                )
                                p_existente.sin_lactosa = bool(
                                    etiquetas.get("sin_lactosa")
                                )
                                p_existente.sello_calidad = etiquetas.get(
                                    "sello_calidad"
                                )
                                p_existente.tipo_proteina = etiquetas.get(
                                    "tipo_proteina"
                                )
                                p_existente.porcentaje_proteina = porcentaje_proteina
                                p_existente.tipo_creatina = etiquetas.get(
                                    "tipo_creatina"
                                )
                                p_existente.perfil_aminoacidos = etiquetas.get(
                                    "perfil_aminoacidos"
                                )
                                p_existente.tipo_vitamina = etiquetas.get(
                                    "tipo_vitamina"
                                )
                                p_existente.peso_gramos = peso_norm
                                p_existente.precio_por_kg = preciokg_norm

                                if precio_ant_norm is not None:
                                    p_existente.precio_anterior = precio_ant_norm
                                    p_existente.precio = precio_norm
                                else:
                                    if precio_norm < p_existente.precio:
                                        p_existente.precio_anterior = float(
                                            p_existente.precio
                                        )
                                        p_existente.precio = precio_norm
                                    elif precio_norm > p_existente.precio:
                                        p_existente.precio_anterior = None
                                        p_existente.precio = precio_norm
                            else:
                                nuevo_prod = models.Producto(
                                    nombre=nombre_norm,
                                    descripcion=descripcion_norm,
                                    precio=precio_norm,
                                    precio_anterior=precio_ant_norm,
                                    imagen_url=str(imagen) if imagen else None,
                                    afiliado_url=url_afiliado,
                                    tienda="HSN",
                                    marca_id=marca_actual.id,
                                    categoria_id=categoria_id,
                                    sabor=sabor_norm,
                                    formato=etiquetas.get("formato"),
                                    objetivo=objetivo_norm,
                                    es_vegano=bool(etiquetas.get("es_vegano")),
                                    sin_gluten=bool(etiquetas.get("sin_gluten")),
                                    sin_lactosa=bool(etiquetas.get("sin_lactosa")),
                                    sello_calidad=etiquetas.get("sello_calidad"),
                                    tipo_proteina=etiquetas.get("tipo_proteina"),
                                    porcentaje_proteina=porcentaje_proteina,
                                    tipo_creatina=etiquetas.get("tipo_creatina"),
                                    perfil_aminoacidos=etiquetas.get(
                                        "perfil_aminoacidos"
                                    ),
                                    tipo_vitamina=etiquetas.get("tipo_vitamina"),
                                    peso_gramos=peso_norm,
                                    precio_por_kg=preciokg_norm,
                                    slug=slug_norm,
                                )
                                productos_nuevos.append(nuevo_prod)
                                productos_bd[slug_norm] = nuevo_prod
                            # Ya lo hemos gestionado arriba
                            pass
                        except Exception as e_prod:
                            print(
                                f"      ⚠️ Error al normalizar/crear producto {url_prod}: {e_prod}"
                            )
                            traceback.print_exc()
                            continue

                        cat_count += 1
                        total_general += 1

                        # --- ESCUDO ANTI-FALLOS DE BBDD ---
                        if total_general > 0 and total_general % 20 == 0:
                            try:
                                if productos_nuevos:
                                    db.add_all(productos_nuevos)
                                db.commit()  # ¡El commit ahora se hace SIEMPRE!
                            except Exception as db_err:
                                db.rollback()
                                print(
                                    f"      ⚠️ Advertencia BD: {db_err.__class__.__name__}: {db_err}. Reintentando en el próximo lote."
                                )
                                traceback.print_exc()
                            finally:
                                productos_nuevos = []

                        time.sleep(0.3 + random.random() * 0.5)

                    except Exception:
                        continue

            except Exception as net_err:
                # --- ESCUDO ANTI-APAGONES DE RED ---
                print(
                    f"   ⚠️ Corte de internet detectado en página {pagina}: {net_err}. Saltando..."
                )
                time.sleep(2)  # Pausa para que el router se recupere
                break
            except Exception as e:
                print(f"   ⚠️ Fallo inesperado en página {pagina}: {e}")
                break

            pagina += 1

        print(f"   ✅ {cat_count} productos procesados en esta categoría.")

    # Guardado Final Seguro
    try:
        if productos_nuevos:
            db.add_all(productos_nuevos)
        db.commit()  # ¡Forzamos el guardado final siempre!
    except Exception as e:
        db.rollback()
        print(
            f"⚠️ Aviso: No se pudieron guardar los últimos productos. Error: {e.__class__.__name__}: {e}"
        )
        traceback.print_exc()

    print(
        f"\n🎉 ¡MISIÓN CUMPLIDA! Catálogo inyectado: {total_general} productos robustos."
    )

    db.close()
    print("🚪 Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    inyectar_en_bd()
