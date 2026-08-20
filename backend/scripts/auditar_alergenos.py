import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def auditar_alergenos():
    db = SessionLocal()
    try:
        print("🔍 Rastreando intolerancias ocultas en el catálogo...\n")

        # Productos que mencionan "sin gluten" (o variaciones) en su descripción o nombre
        mencionan_gluten = (
            db.query(models.Producto)
            .filter(
                (models.Producto.descripcion.ilike("%sin gluten%"))
                | (models.Producto.descripcion.ilike("%gluten free%"))
                | (models.Producto.nombre.ilike("%sin gluten%"))
            )
            .count()
        )

        mencionan_lactosa = (
            db.query(models.Producto)
            .filter(
                (models.Producto.descripcion.ilike("%sin lactosa%"))
                | (models.Producto.descripcion.ilike("%lactose free%"))
                | (models.Producto.nombre.ilike("%sin lactosa%"))
            )
            .count()
        )

        marcados_gluten = (
            db.query(models.Producto).filter(models.Producto.sin_gluten == True).count()
        )
        marcados_lactosa = (
            db.query(models.Producto)
            .filter(models.Producto.sin_lactosa == True)
            .count()
        )

        print("🌾 GLUTEN:")
        print(f"   - Mencionan explícitamente 'sin gluten': {mencionan_gluten}")
        print(f"   - Marcados en BD actualmente: {marcados_gluten}")

        print("-" * 40)
        print("🥛 LACTOSA:")
        print(f"   - Mencionan explícitamente 'sin lactosa': {mencionan_lactosa}")
        print(f"   - Marcados en BD actualmente: {marcados_lactosa}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditar_alergenos()
