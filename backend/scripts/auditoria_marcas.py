import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def listar_todas_las_marcas():
    db = SessionLocal()
    try:
        print("🔍 Extrayendo el catálogo completo de marcas activas...\n")

        # Sacamos todas las marcas que tienen al menos 1 producto
        marcas = (
            db.query(models.Marca.nombre)
            .join(models.Producto, models.Marca.id == models.Producto.marca_id)
            .distinct()
            .order_by(models.Marca.nombre)
            .all()
        )

        nombres = [m[0] for m in marcas]

        print(f"📦 TENEMOS {len(nombres)} MARCAS EN TOTAL:")
        print("-" * 60)

        # Imprimimos en columnas para que sea fácil de leer en tu terminal
        for i in range(0, len(nombres), 3):
            fila = nombres[i : i + 3]
            print(" | ".join(f"{nombre:<25}" for nombre in fila))

        print("-" * 60)

    except Exception as e:
        print(f"❌ Error al consultar la BD: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    listar_todas_las_marcas()
