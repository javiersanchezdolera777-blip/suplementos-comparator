import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models
from ingestores.utils import clasificar_producto


def reclasificar_todo():
    db = SessionLocal()
    try:
        print("🚀 Iniciando reclasificación ultrarrápida en la Base de Datos...")
        productos = db.query(models.Producto).all()
        actualizados = 0

        for p in productos:
            # Usamos el cerebro de utils.py pasándole los datos que ya tenemos guardados
            etiquetas = clasificar_producto(p.nombre, p.descripcion)

            if etiquetas:
                p.formato = etiquetas.get("formato")
                p.sabor = etiquetas.get("sabor", [])
                actualizados += 1

        db.commit()
        print(f"✅ ¡Completado! {actualizados} productos actualizados en 2 segundos.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reclasificar_todo()
