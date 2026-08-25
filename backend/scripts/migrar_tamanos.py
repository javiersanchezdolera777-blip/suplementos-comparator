import sys
import os

# Añadimos la raíz al path para poder importar todo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
from ingestores.utils import extraer_presentacion


def retroactivo_tamanos():
    db = SessionLocal()
    print("🚀 Iniciando volcado retroactivo masivo de tamaños en la Base de Datos...")

    # 1. Cogemos TODOS los productos que tienen el tamaño vacío (NULL)
    productos_vacios = (
        db.query(models.Producto).filter(models.Producto.presentacion == None).all()
    )

    print(
        f"📦 Encontrados {len(productos_vacios)} productos huérfanos de tamaño en todo el catálogo."
    )

    actualizados = 0
    # 2. Los pasamos por el NLP y forzamos el guardado directo
    for p in productos_vacios:
        nuevo_tamano = extraer_presentacion(p.nombre)
        if nuevo_tamano:
            p.presentacion = nuevo_tamano
            actualizados += 1

    # 3. Guardamos todo de golpe
    if actualizados > 0:
        db.commit()

    print(f"✅ ¡Éxito! Se han rellenado {actualizados} productos permanentemente.")
    db.close()


if __name__ == "__main__":
    retroactivo_tamanos()
