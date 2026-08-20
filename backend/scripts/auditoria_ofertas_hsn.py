import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def auditar_ofertas_hsn():
    db = SessionLocal()
    try:
        print("🔍 Analizando el mapa de descuentos de HSN...\n")

        # Filtramos solo productos de HSN que tengan precio_anterior y que sea mayor al precio actual
        productos_oferta = (
            db.query(models.Producto)
            .filter(
                models.Producto.tienda == "HSN",
                models.Producto.precio_anterior != None,
                models.Producto.precio_anterior > models.Producto.precio,
            )
            .all()
        )

        total_ofertas = len(productos_oferta)

        if total_ofertas == 0:
            print("🤷‍♂️ No hay ofertas de HSN en la base de datos ahora mismo.")
            return

        # Diccionario para agrupar los rangos
        rangos = {
            "0-10%": 0,
            "10-20%": 0,
            "20-30%": 0,
            "30-40%": 0,
            "40-50%": 0,
            "+50%": 0,
        }

        # Calculamos el descuento de cada producto y lo metemos en su cajón
        for p in productos_oferta:
            descuento = ((p.precio_anterior - p.precio) / p.precio_anterior) * 100

            if descuento < 10:
                rangos["0-10%"] += 1
            elif descuento < 20:
                rangos["10-20%"] += 1
            elif descuento < 30:
                rangos["20-30%"] += 1
            elif descuento < 40:
                rangos["30-40%"] += 1
            elif descuento < 50:
                rangos["40-50%"] += 1
            else:
                rangos["+50%"] += 1

        print(f"📊 TOTAL DE OFERTAS HSN DETECTADAS: {total_ofertas} productos")
        print("-" * 65)

        # Imprimimos los resultados con una barra visual simple
        for rango, cantidad in rangos.items():
            porcentaje = (cantidad / total_ofertas) * 100
            barra = "█" * int(porcentaje / 2)  # Cada bloque visual representa un 2%
            print(
                f"🏷️ {rango:>6}: {cantidad:>4} ofertas ({porcentaje:>5.1f}%) | {barra}"
            )

        print("-" * 65)
        print(
            "💡 Los productos que perderían su etiqueta de chollo (si capamos al 20%) son los de los dos primeros rangos."
        )

    except Exception as e:
        print(f"❌ Error al consultar la BD: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditar_ofertas_hsn()
