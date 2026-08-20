import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def comprobar_descripciones():
    db = SessionLocal()
    try:
        print("🔍 Consultando las nuevas descripciones en BD...\n")

        # Pillamos 3 productos de Sportlive para ver cómo han quedado
        productos = (
            db.query(models.Producto)
            .filter(models.Producto.tienda == "Sportlive")
            .limit(3)
            .all()
        )

        for p in productos:
            print(f"📦 PRODUCTO: {p.nombre}")
            print(f"📝 DESCRIPCIÓN (Longitud: {len(p.descripcion)} caracteres):")
            print(f"   {p.descripcion}\n")
            print("-" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    comprobar_descripciones()
