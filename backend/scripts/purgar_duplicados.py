import sys
import os
import html
import re
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def generar_slug(nombre: str) -> str:
    texto = (
        unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("utf-8")
    )
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def purgar_duplicados_html(ejecutar_borrado=False):
    db = SessionLocal()
    try:
        print("🔍 Buscando productos duplicados por culpa de entidades HTML...\n")

        productos = (
            db.query(models.Producto)
            .filter(models.Producto.tienda.in_(["Sportlive", "Farma2Go"]))
            .all()
        )

        slugs_existentes = {p.slug for p in productos}
        a_borrar = []

        for p in productos:
            nombre_limpio = html.unescape(p.nombre)
            slug_ideal = generar_slug(nombre_limpio)

            if p.slug != slug_ideal:
                if slug_ideal in slugs_existentes:
                    # AQUÍ ESTÁ EL ARREGLO: Guardamos la tupla junta
                    a_borrar.append((p, slug_ideal))

        if not a_borrar:
            print("✅ ¡No se encontraron duplicados sucios! La BD está limpia.")
            return

        print(
            f"⚠️ Se han encontrado {len(a_borrar)} productos viejos que ya tienen una versión limpia."
        )

        # Ahora desempaquetamos la tupla y siempre coincidirán
        for p, ideal in a_borrar:
            print(
                f"   🗑️ A borrar el sucio: [{p.slug}] -> Se conservará el limpio: [{ideal}]"
            )

        print("-" * 50)

        if ejecutar_borrado:
            print(f"🔥 MODO BORRADO ACTIVADO. Eliminando {len(a_borrar)} productos...")
            for p, _ in a_borrar:
                db.delete(p)
            db.commit()
            print("✅ ¡Limpieza completada con éxito!")
        else:
            print("🛡️ MODO SIMULACIÓN. No se ha tocado la base de datos.")
            print(
                "👉 Si la lista de arriba te parece correcta, cambia 'ejecutar_borrado=True' en la última línea del script."
            )

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la purga: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    purgar_duplicados_html(ejecutar_borrado=True)
