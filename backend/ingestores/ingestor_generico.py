import os
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

# Asegurar path de backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import SessionLocal
from ingestores.feed_parser import descargar_y_parsear_feed, sanitizar_precio
from ingestores.utils import (
    limpiar_texto, generar_slug, calcular_metricas_precio, clasificar_producto
)
from schemas import CategoriaEnum, normalizar_marca


def obtener_valor_columna(item: dict, col_spec: Any) -> Any:
    """
    Navega en un diccionario o lista de fallbacks usando notación de puntos (ej: 'offers.0.price.value').
    """
    if not col_spec or not item:
        return None

    if isinstance(col_spec, list):
        for spec in col_spec:
            val = obtener_valor_columna(item, spec)
            if val not in (None, "", [], {}):
                return val
        return None

    if not isinstance(col_spec, str):
        return None

    # Notación simple o de puntos
    partes = col_spec.split('.')
    actual = item
    for parte in partes:
        if isinstance(actual, dict):
            actual = actual.get(parte)
        elif isinstance(actual, list):
            try:
                idx = int(parte)
                actual = actual[idx] if 0 <= idx < len(actual) else None
            except ValueError:
                return None
        else:
            return None
        if actual is None:
            break
    return actual


def ingestar_tienda_generica(nombre_tienda: str, config: dict) -> Dict[str, Any]:
    """
    Ejecuta el proceso atómico de ingestión para una tienda configurable.
    Garantiza la preservación de datos en caso de fallo en la descarga o feed vacío.
    """
    inicio_tiempo = time.time()
    print(f"\n🚀 Iniciando ingestión para tienda: [{nombre_tienda}]...")

    url_feed = config.get("url_feed")
    formato = config.get("formato", "json")
    delimitador = config.get("delimitador", ",")
    encoding = config.get("encoding", "utf-8")
    marca_modo = config.get("marca_modo", "fija")
    marca_defecto = config.get("marca_defecto", nombre_tienda)
    columna_marca = config.get("columna_marca")
    base_url_imagen = config.get("base_url_imagen")
    columnas = config.get("columnas", {})

    # Ruta de caché temporal por tienda
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cache_ingestores")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{nombre_tienda.lower().replace(' ', '_')}_temporal.json")

    # La validez y fallback de caché de 12h se gestiona directamente en http_client.download_json_with_cache

    # 1. DESCARGA Y PARSEO PREVIOS

    try:
        filas = descargar_y_parsear_feed(
            url=url_feed,
            formato=formato,
            delimitador=delimitador,
            encoding=encoding,
            cache_path=cache_path if formato.lower() == "json" else None
        )
    except Exception as err_descarga:
        print(f"❌ CANCELADO: Falló la descarga del feed de {nombre_tienda}: {err_descarga}")
        return {
            "success": False,
            "productos_inyectados": 0,
            "mensaje": f"Error de descarga: {err_descarga}"
        }

    if not filas or len(filas) == 0:
        print(f"⚠️ CANCELADO: El feed de {nombre_tienda} está vacío. No se realizarán cambios en la BBDD.")
        return {
            "success": False,
            "productos_inyectados": 0,
            "mensaje": "Feed vacío"
        }

    print(f"📦 Feed obtenido con {len(filas)} filas. Procesando productos en memoria...")

    db = SessionLocal()

    try:
        # Pre-cargar o crear Categorías
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

        # Caché de marcas en memoria para esta ejecución
        marcas_cache = {}

        productos_nuevos = []

        for item in filas:
            if not isinstance(item, dict):
                continue

            # Extracción de campos crudos
            nombre_crudo = obtener_valor_columna(item, columnas.get("nombre"))
            if not nombre_crudo:
                continue

            nombre = str(nombre_crudo).strip()
            desc_cruda = obtener_valor_columna(item, columnas.get("descripcion")) or ""
            desc_limpia = limpiar_texto(desc_cruda)

            # Sanitizar precios
            raw_precio = obtener_valor_columna(item, columnas.get("precio"))
            precio = sanitizar_precio(raw_precio)
            if precio is None or precio <= 0:
                continue

            raw_precio_ant = obtener_valor_columna(item, columnas.get("precio_anterior"))
            precio_anterior = sanitizar_precio(raw_precio_ant)
            if precio_anterior is not None and precio_anterior <= precio:
                precio_anterior = None

            # Clasificación de producto
            categorias_item = item.get("categories") or item.get("category") or item.get("categoria")
            etiquetas = clasificar_producto(nombre, desc_limpia, categorias_item)
            if not etiquetas or not etiquetas.get("categoria"):
                continue

            # Gestión de marca en BBDD / Caché
            if marca_modo == "columna" and columna_marca:
                raw_marca = obtener_valor_columna(item, columna_marca)
                nombre_marca_str = str(raw_marca).strip() if raw_marca else marca_defecto
            else:
                nombre_marca_str = marca_defecto

            nombre_marca_norm = normalizar_marca(nombre_marca_str)

            if nombre_marca_norm not in marcas_cache:
                marca_obj = db.query(models.Marca).filter_by(nombre=nombre_marca_norm).first()
                if not marca_obj:
                    try:
                        marca_obj = models.Marca(nombre=nombre_marca_norm)
                        db.add(marca_obj)
                        db.commit()
                        db.refresh(marca_obj)
                    except Exception:
                        db.rollback()
                        marca_obj = db.query(models.Marca).filter_by(nombre=nombre_marca_norm).first()
                        if not marca_obj:
                            continue
                marcas_cache[nombre_marca_norm] = marca_obj.id

            marca_id = marcas_cache[nombre_marca_norm]

            # URLs de Imagen y Afiliado
            img_raw = obtener_valor_columna(item, columnas.get("imagen_url")) or ""
            imagen_url = str(img_raw).strip()
            if imagen_url and base_url_imagen and imagen_url.startswith("/"):
                imagen_url = f"{base_url_imagen}{imagen_url}"

            afiliado_url = str(obtener_valor_columna(item, columnas.get("afiliado_url")) or "").strip()

            # Cálculo de métricas de precio
            peso_expl = obtener_valor_columna(item, columnas.get("peso_gramos"))
            item_con_peso = dict(item)
            if peso_expl is not None:
                item_con_peso["peso_gramos"] = peso_expl

            metricas = calcular_metricas_precio(item_con_peso, precio, desc_limpia)

            # Mapeo de Categoría
            categoria_id = mapa_categorias.get(etiquetas.get("categoria"))
            if not categoria_id:
                continue

            slug = generar_slug(nombre)

            # Construcción del objeto Producto
            nuevo_prod = models.Producto(
                nombre=nombre[:255],
                descripcion=desc_limpia[:900],
                precio=precio,
                precio_anterior=precio_anterior,
                imagen_url=imagen_url[:500] if imagen_url else None,
                afiliado_url=afiliado_url[:500] if afiliado_url else None,
                tienda=nombre_tienda,
                marca_id=marca_id,
                categoria_id=categoria_id,
                sabor=etiquetas.get("sabor", []),
                formato=etiquetas.get("formato"),
                presentacion=etiquetas.get("presentacion"),
                objetivo=etiquetas.get("objetivo"),
                es_vegano=bool(etiquetas.get("es_vegano")),
                sello_calidad=etiquetas.get("sello_calidad"),
                tipo_proteina=etiquetas.get("tipo_proteina"),
                porcentaje_proteina=etiquetas.get("porcentaje_proteina"),
                tipo_creatina=etiquetas.get("tipo_creatina"),
                perfil_aminoacidos=etiquetas.get("perfil_aminoacidos"),
                tipo_vitamina=etiquetas.get("tipo_vitamina"),
                peso_gramos=metricas.get("peso_gramos"),
                precio_por_kg=metricas.get("precio_por_kg"),
                slug=slug
            )
            productos_nuevos.append(nuevo_prod)

        # 3. INYECCIÓN ATÓMICA EN BBDD
        print(f"🧹 Limpiando productos antiguos de la tienda [{nombre_tienda}]...")
        db.query(models.Producto).filter(models.Producto.tienda == nombre_tienda).delete()

        print(f"💾 Inyectando {len(productos_nuevos)} nuevos productos para [{nombre_tienda}]...")
        db.add_all(productos_nuevos)
        db.commit()

        duracion = round(time.time() - inicio_tiempo, 2)
        print(f"✅ ¡Éxito en {nombre_tienda}! {len(productos_nuevos)} productos inyectados en {duracion}s.")

        return {
            "success": True,
            "productos_inyectados": len(productos_nuevos),
            "tiempo_segundos": duracion,
            "mensaje": "Inyección completada"
        }

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR ATÓMICO en {nombre_tienda}: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "productos_inyectados": 0,
            "mensaje": f"Error en inyección DB: {e}"
        }
    finally:
        db.close()
