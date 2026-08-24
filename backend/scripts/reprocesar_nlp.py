import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Producto, Categoria
from ingestores.utils import clasificar_producto


def reprocesar_todo():
    db = SessionLocal()
    print("🧠 Iniciando reprocesamiento masivo con NLP en Producción...")

    productos = db.query(Producto).all()
    mapa_cats = {c.nombre: c.id for c in db.query(Categoria).all()}
    actualizados = 0

    for p in productos:
        if not p.nombre:
            continue

        # Usamos la descripción que ya está en la base de datos
        desc = p.descripcion or ""

        # Pasamos el producto por tu cerebro NLP actualizado
        etiquetas = clasificar_producto(p.nombre, desc)

        if etiquetas and etiquetas.get("categoria"):
            cat_nombre = etiquetas.get("categoria")
            if cat_nombre in mapa_cats:
                p.categoria_id = mapa_cats[cat_nombre]

            p.formato = etiquetas.get("formato")

            # Aseguramos que el sabor se guarde como array si no lo es
            sabor_nuevo = etiquetas.get("sabor")
            p.sabor = (
                sabor_nuevo
                if isinstance(sabor_nuevo, list)
                else ([sabor_nuevo] if sabor_nuevo else [])
            )

            p.objetivo = etiquetas.get("objetivo")
            p.es_vegano = bool(etiquetas.get("es_vegano"))
            p.sin_gluten = bool(etiquetas.get("sin_gluten"))
            p.sin_lactosa = bool(etiquetas.get("sin_lactosa"))
            p.sello_calidad = etiquetas.get("sello_calidad")
            p.tipo_proteina = etiquetas.get("tipo_proteina")
            p.tipo_creatina = etiquetas.get("tipo_creatina")
            p.perfil_aminoacidos = etiquetas.get("perfil_aminoacidos")
            p.tipo_vitamina = etiquetas.get("tipo_vitamina")

            actualizados += 1

    db.commit()
    print(
        f"✅ ¡Completado! {actualizados} productos han sido re-etiquetados con éxito."
    )
    db.close()


if __name__ == "__main__":
    reprocesar_todo()
