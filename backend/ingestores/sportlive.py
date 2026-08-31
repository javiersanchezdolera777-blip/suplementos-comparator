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
    calcular_metricas_precio,
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
            for p in db.query(models.Producto)
            .join(models.Oferta)
            .filter(models.Oferta.tienda == "Sportlive")
            .all()
        }
        print(f"✨ {len(productos_bd)} productos en memoria. Iniciando ingesta...")

        datos = descargar_datos()
        productos_nuevos = []
        actualizados = 0

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

            categoria_id = mapa_categorias.get(etiquetas.get("categoria"))
            if not categoria_id:
                categoria_id = next(iter(mapa_categorias.values()))

            slug_norm = generar_slug(nombre)
            if slug_norm in productos_bd:
                p_existente = productos_bd[slug_norm]
                p_existente.nombre = nombre
                p_existente.descripcion = descripcion_ui
                p_existente.imagen_url = imagen_url
                p_existente.marca_id = marca_oficial.id
                p_existente.categoria_id = categoria_id
                p_existente.sabor = etiquetas.get("sabor")
                p_existente.formato = etiquetas.get("formato")
                p_existente.objetivo = etiquetas.get("objetivo")
                p_existente.es_vegano = bool(etiquetas.get("es_vegano"))
                p_existente.sello_calidad = etiquetas.get("sello_calidad")
                p_existente.tipo_proteina = etiquetas.get("tipo_proteina")
                p_existente.porcentaje_proteina = etiquetas.get("porcentaje_proteina")
                p_existente.tipo_creatina = etiquetas.get("tipo_creatina")
                p_existente.perfil_aminoacidos = etiquetas.get("perfil_aminoacidos")
                p_existente.tipo_vitamina = etiquetas.get("tipo_vitamina")
                p_existente.peso_gramos = metricas["peso_gramos"]
                p_existente.presentacion = presentacion_ext

                # --- NUEVA LÓGICA DE OFERTAS MULTI-TIENDA ---
                oferta_sl = next(
                    (o for o in p_existente.ofertas if o.tienda == "Sportlive"), None
                )

                if oferta_sl:
                    oferta_sl.afiliado_url = afiliado_url
                    oferta_sl.precio_por_kg = metricas["precio_por_kg"]
                    oferta_sl.activo = True

                    if precio_anterior is not None:
                        oferta_sl.precio_anterior = precio_anterior
                        oferta_sl.precio = precio
                    else:
                        if precio < oferta_sl.precio:
                            oferta_sl.precio_anterior = float(oferta_sl.precio)
                            oferta_sl.precio = precio
                        elif precio > oferta_sl.precio:
                            oferta_sl.precio_anterior = None
                            oferta_sl.precio = precio
                else:
                    nueva_oferta = models.Oferta(
                        tienda="Sportlive",
                        precio=precio,
                        precio_anterior=precio_anterior,
                        precio_por_kg=metricas["precio_por_kg"],
                        afiliado_url=afiliado_url,
                        activo=True,
                    )
                    p_existente.ofertas.append(nueva_oferta)

                db.add(p_existente)
                actualizados += 1
            else:
                nuevo_producto = models.Producto(
                    nombre=nombre,
                    descripcion=descripcion_ui,
                    imagen_url=imagen_url,
                    marca_id=marca_oficial.id,
                    categoria_id=categoria_id,
                    sabor=etiquetas.get("sabor"),
                    formato=etiquetas.get("formato"),
                    objetivo=etiquetas.get("objetivo"),
                    es_vegano=bool(etiquetas.get("es_vegano")),
                    sello_calidad=etiquetas.get("sello_calidad"),
                    tipo_proteina=etiquetas.get("tipo_proteina"),
                    porcentaje_proteina=etiquetas.get("porcentaje_proteina"),
                    tipo_creatina=etiquetas.get("tipo_creatina"),
                    perfil_aminoacidos=etiquetas.get("perfil_aminoacidos"),
                    tipo_vitamina=etiquetas.get("tipo_vitamina"),
                    peso_gramos=metricas["peso_gramos"],
                    presentacion=presentacion_ext,
                    slug=slug_norm,
                )
                nueva_oferta = models.Oferta(
                    tienda="Sportlive",
                    precio=precio,
                    precio_anterior=precio_anterior,
                    precio_por_kg=metricas["precio_por_kg"],
                    afiliado_url=afiliado_url,
                    activo=True,
                )
                nuevo_producto.ofertas.append(nueva_oferta)

                productos_nuevos.append(nuevo_producto)
                productos_bd[slug_norm] = nuevo_producto

        db.add_all(productos_nuevos)
        db.commit()
        print(
            f"\n🎉 ¡Limpieza completada! {len(productos_nuevos)} productos nuevos y {actualizados} actualizados de {nombre_marca}."
        )

    except Exception as e:
        print(f"❌ ERROR INESPERADO en Sportlive: {e}")
        db.rollback()
    finally:
        db.close()
        print("🚪 Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    inyectar_en_bd()
