import sys
import os
from sqlalchemy import func, case

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def auditar_ofertas_global():
    db = SessionLocal()
    try:
        print("🔍 Rastreando chollos reales en la base de datos...\n")

        # Contamos total de productos y total de ofertas (>0) por tienda en una sola consulta
        resultados = (
            db.query(
                models.Producto.tienda,
                func.count(models.Producto.id).label("total_productos"),
                func.sum(
                    case(
                        (models.Producto.precio_anterior > models.Producto.precio, 1),
                        else_=0,
                    )
                ).label("total_ofertas"),
            )
            .group_by(models.Producto.tienda)
            .all()
        )

        total_global_ofertas = 0

        print("🏆 ESTADO ACTUAL DE LAS OFERTAS POR TIENDA:")
        print("-" * 60)
        for tienda, total, ofertas in resultados:
            ofertas = int(ofertas) if ofertas else 0
            total_global_ofertas += ofertas
            porcentaje = (ofertas / total) * 100 if total > 0 else 0
            print(
                f" 🏪 {tienda:<12} | {ofertas:>4} chollos de {total:>4} prod. ({porcentaje:>5.1f}%)"
            )

        print("-" * 60)
        print(f"🔥 TOTAL GLOBAL DE OFERTAS: {total_global_ofertas}")

    except Exception as e:
        print(f"❌ Error al consultar la BD: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditar_ofertas_global()
