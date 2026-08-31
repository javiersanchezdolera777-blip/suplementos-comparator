import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
from sqlalchemy import func


def auditar_catalogo():
    db = SessionLocal()
    print("🔍 INICIANDO AUDITORÍA MULTI-TIENDA...\n")

    try:
        # 1. Conteo total de entidades
        total_productos = db.query(models.Producto).count()
        total_ofertas = db.query(models.Oferta).count()
        print(f"📦 Total de Productos Maestro: {total_productos}")
        print(f"🏷️ Total de Ofertas Activas: {total_ofertas}")

        # 2. Desglose de Ofertas por Tienda
        ofertas_por_tienda = (
            db.query(models.Oferta.tienda, func.count(models.Oferta.id))
            .group_by(models.Oferta.tienda)
            .all()
        )
        print("\n📊 Desglose de Ofertas por Tienda:")
        for tienda, count in ofertas_por_tienda:
            print(f"  - {tienda}: {count} ofertas")

        # 3. Detectar productos huérfanos (sin ofertas)
        huerfanos = (
            db.query(models.Producto).filter(~models.Producto.ofertas.any()).count()
        )
        print(f"\n⚠️ Productos Huérfanos (Sin precio/tienda): {huerfanos}")

        # 4. Inspección Visual de 1 Producto Aleatorio de Farma2Go
        print("\n🔬 Inspección de Rayos X (Ejemplo de Farma2Go):")
        ejemplo = (
            db.query(models.Producto)
            .join(models.Oferta)
            .filter(models.Oferta.tienda == "Farma2Go")
            .first()
        )

        if ejemplo:
            print(f"  🔹 Producto: {ejemplo.nombre}")
            print(f"  🔹 ID Maestro: {ejemplo.id}")
            print(
                f"  🔹 Categoría: {ejemplo.categoria.nombre if ejemplo.categoria else 'N/A'}"
            )
            print(f"  🔹 Ofertas anidadas conectadas ({len(ejemplo.ofertas)}):")
            for o in ejemplo.ofertas:
                print(
                    f"     -> Tienda: {o.tienda} | Precio: {o.precio}€ | Link: {o.afiliado_url[:30]}..."
                )
        else:
            print("  ❌ No se encontró ningún producto de Farma2Go para inspeccionar.")

    except Exception as e:
        print(f"❌ Error en la auditoría: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditar_catalogo()
