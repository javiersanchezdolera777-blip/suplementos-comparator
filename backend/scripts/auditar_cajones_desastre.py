import sys
import os
from sqlalchemy import func

# Asegurar path de importación
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models


def auditar_categorias_fantasma():
    db = SessionLocal()
    print("🔍 AUDITORÍA DE CAJONES DESASTRE ('Otros' y 'Accesorios')\n" + "=" * 50)

    try:
        # Buscar los IDs de las categorías sospechosas
        categorias_objetivo = (
            db.query(models.Categoria)
            .filter(models.Categoria.nombre.in_(["Otros", "Accesorios"]))
            .all()
        )

        if not categorias_objetivo:
            print(
                "✅ No existen las categorías 'Otros' ni 'Accesorios' en la base de datos."
            )
            return

        total_atrapados = 0
        for cat in categorias_objetivo:
            # Quitamos la condición de 'activo == True'
            productos = (
                db.query(models.Producto)
                .filter(models.Producto.categoria_id == cat.id)
                .all()
            )

            count = len(productos)
            total_atrapados += count

            print(f"\n📂 Categoría: {cat.nombre.upper()} ({count} productos)")
            if count > 0:
                print("-" * 40)
                # Mostrar los 15 primeros para analizar patrones
                for p in productos[:15]:
                    marca = p.marca.nombre if p.marca else "Sin Marca"
                    print(f"  👉 [{marca}] {p.nombre} (Tienda: {p.tienda})")
                if count > 15:
                    print(f"  ... y {count - 15} productos más.")

        print("\n" + "=" * 50)
        print(f"🚨 TOTAL DE PRODUCTOS ATRAPADOS: {total_atrapados}")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    auditar_categorias_fantasma()
