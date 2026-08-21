import sys
import os
from sqlalchemy import or_

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def auditar_alergenos_avanzado():
    db = SessionLocal()
    try:
        print("🔍 Rastreando intolerancias con el escáner avanzado...\n")

        # Mencionan Gluten (Ampliado para igualar al ingestor)
        mencionan_gluten = (
            db.query(models.Producto)
            .filter(
                or_(
                    models.Producto.descripcion.ilike("%sin gluten%"),
                    models.Producto.descripcion.ilike("%gluten free%"),
                    models.Producto.descripcion.ilike("%gluten-free%"),
                    models.Producto.descripcion.ilike("%libre de gluten%"),
                    models.Producto.descripcion.ilike("%0% gluten%"),
                    models.Producto.nombre.ilike("%sin gluten%"),
                    models.Producto.nombre.ilike("%gluten free%"),
                )
            )
            .count()
        )

        # Mencionan Lactosa (Ampliado)
        mencionan_lactosa = (
            db.query(models.Producto)
            .filter(
                or_(
                    models.Producto.descripcion.ilike("%sin lactosa%"),
                    models.Producto.descripcion.ilike("%lactose free%"),
                    models.Producto.descripcion.ilike("%lactose-free%"),
                    models.Producto.descripcion.ilike("%libre de lactosa%"),
                    models.Producto.descripcion.ilike("%0% lactosa%"),
                    models.Producto.descripcion.ilike("%zero lactose%"),
                    models.Producto.nombre.ilike("%sin lactosa%"),
                )
            )
            .count()
        )

        print("📊 TOTALES REALES (Desarrollo):")
        print(
            f"🌾 GLUTEN  -> Menciones: {mencionan_gluten} | Marcados en BD: {db.query(models.Producto).filter(models.Producto.sin_gluten == True).count()}"
        )
        print(
            f"🥛 LACTOSA -> Menciones: {mencionan_lactosa} | Marcados en BD: {db.query(models.Producto).filter(models.Producto.sin_lactosa == True).count()}"
        )

        print("\n🏪 DESGLOSE DE PRODUCTOS MARCADOS POR TIENDA:")
        print("-" * 50)
        tiendas = ["HSN", "Farma2Go", "Sportlive"]
        for tienda in tiendas:
            g = (
                db.query(models.Producto)
                .filter(
                    models.Producto.tienda == tienda, models.Producto.sin_gluten == True
                )
                .count()
            )
            l = (
                db.query(models.Producto)
                .filter(
                    models.Producto.tienda == tienda,
                    models.Producto.sin_lactosa == True,
                )
                .count()
            )
            print(f" 🛒 {tienda:<10} -> 🌾 {g:>3} Sin Gluten | 🥛 {l:>3} Sin Lactosa")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditar_alergenos_avanzado()
