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
from ingestores.utils import (
    normalizar_descripcion_ui,
    extraer_presentacion,
    clasificar_producto,
    extraer_porcentaje_proteina,
    calcular_metricas_precio
)

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
    actualizados = 0
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

        presentacion_ext = extraer_presentacion(nombre)

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

        categoria_id = mapa_categorias.get(etiquetas.get("categoria"))
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
            p_existente.sabor = etiquetas.get("sabor")
            p_existente.formato = etiquetas.get("formato")
            p_existente.objetivo = etiquetas.get("objetivo")
            p_existente.es_vegano = bool(etiquetas.get("es_vegano"))
            p_existente.sin_gluten = bool(etiquetas.get("sin_gluten"))
            p_existente.sin_lactosa = bool(etiquetas.get("sin_lactosa"))
            p_existente.sello_calidad = etiquetas.get("sello_calidad")
            p_existente.tipo_proteina = etiquetas.get("tipo_proteina")
            p_existente.porcentaje_proteina = etiquetas.get("porcentaje_proteina")
            p_existente.tipo_creatina = etiquetas.get("tipo_creatina")
            p_existente.perfil_aminoacidos = etiquetas.get("perfil_aminoacidos")
            p_existente.tipo_vitamina = etiquetas.get("tipo_vitamina")
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

            p_existente.presentacion = presentacion_ext
            db.add(p_existente)
            actualizados += 1
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
                sabor=etiquetas.get("sabor"),
                formato=etiquetas.get("formato"),
                objetivo=etiquetas.get("objetivo"),
                es_vegano=bool(etiquetas.get("es_vegano")),
                sin_gluten=bool(etiquetas.get("sin_gluten")),
                sin_lactosa=bool(etiquetas.get("sin_lactosa")),
                sello_calidad=etiquetas.get("sello_calidad"),
                tipo_proteina=etiquetas.get("tipo_proteina"),
                porcentaje_proteina=etiquetas.get("porcentaje_proteina"),
                tipo_creatina=etiquetas.get("tipo_creatina"),
                perfil_aminoacidos=etiquetas.get("perfil_aminoacidos"),
                tipo_vitamina=etiquetas.get("tipo_vitamina"),
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
        f"\n🎉 ¡Inyección de Farma2Go completada! {len(productos_nuevos)} suplementos nuevos guardados, {actualizados} actualizados."
    )


if __name__ == "__main__":
    inyectar_en_bd()
