import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Producto, Categoria
from ingestores.utils import clasificar_producto
from schemas import CategoriaEnum


def arreglar_categorias():
    db = SessionLocal()
    print("🛠️ Iniciando reparación de Categorías Principales en Producción...")

    # 1. Asegurar que TODAS las categorías existen en la base de datos
    print("📦 Verificando tabla de Categorías...")
    for cat_enum in CategoriaEnum:
        cat_db = db.query(Categoria).filter(Categoria.nombre == cat_enum.value).first()
        if not cat_db:
            print(f"   ➕ Creando categoría faltante en BD: {cat_enum.value}")
            nueva_cat = Categoria(nombre=cat_enum.value)
            db.add(nueva_cat)

    # Guardamos para que se generen los IDs de las categorías nuevas
    db.commit()

    # 2. Recargar el diccionario de categorías con los IDs frescos
    mapa_cats = {c.nombre: c.id for c in db.query(Categoria).all()}

    # 3. Reasignar categorías a los productos
    productos = db.query(Producto).all()
    actualizados = 0

    print(f"🔄 Re-evaluando {len(productos)} productos...")
    for p in productos:
        if not p.nombre:
            continue

        desc = p.descripcion or ""
        etiquetas = clasificar_producto(p.nombre, desc)

        if etiquetas and etiquetas.get("categoria"):
            cat_nombre = etiquetas.get("categoria")

            # Si la categoría existe en el mapa, se la asignamos
            if cat_nombre in mapa_cats:
                nuevo_id = mapa_cats[cat_nombre]
                if p.categoria_id != nuevo_id:
                    p.categoria_id = nuevo_id
                    actualizados += 1

    db.commit()
    print(
        f"✅ ¡Reparación completada! {actualizados} productos han sido movidos a su categoría principal correcta."
    )
    db.close()


if __name__ == "__main__":
    arreglar_categorias()
