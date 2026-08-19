import sys
import os
from sqlalchemy import func

# Añadimos la ruta del backend para que reconozca los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models

def auditar_marcas_hsn():
    db = SessionLocal()
    try:
        print("🔍 Consultando la base de datos (Neon DB)...\n")

        # 1. Total de productos escrapeados de la tienda HSN
        total_hsn = db.query(models.Producto).filter(models.Producto.tienda == "HSN").count()
        print(f"📦 Total de productos ingestados desde la tienda HSN: {total_hsn}")

        # 2. Desglose agrupado por marca real
        print("\n📊 Desglose de marcas asignadas a estos productos:")
        desglose = db.query(
            models.Marca.nombre,
            func.count(models.Producto.id)
        ).join(models.Producto.marca).filter(
            models.Producto.tienda == "HSN"
        ).group_by(models.Marca.nombre).order_by(func.count(models.Producto.id).desc()).all()

        for marca, cantidad in desglose:
            print(f"   - {marca}: {cantidad} productos")

        # 3. Muestra de prueba empírica
        marcas_externas = [m for m, c in desglose if m.lower() != "hsn"]
        if marcas_externas:
            print("\n🎯 Ejemplos de productos rescatados con marcas externas:")
            ejemplos = db.query(models.Producto).join(models.Producto.marca).filter(
                models.Producto.tienda == "HSN",
                models.Marca.nombre.in_(marcas_externas)
            ).limit(5).all()
            
            for p in ejemplos:
                print(f"   👉 [{p.marca.nombre}] {p.nombre} - {p.precio}€")
        else:
            print("\n⚠️ Ojo: No hay marcas externas. Todos los productos de la tienda HSN tienen la marca 'HSN'.")
            print("   (Si esto sale así, significa que necesitas lanzar el ingestor 'hsn.py' para que haga el Upsert con el nuevo código).")

    except Exception as e:
        print(f"❌ Error en la auditoría: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    auditar_marcas_hsn()