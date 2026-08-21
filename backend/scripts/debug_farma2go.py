import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestores.pharma2go import descargar_datos


def auditar_json_farma2go():
    print("🔄 Descargando feed de Tradedoubler para Farma2Go...")
    datos = descargar_datos()

    if not datos:
        print("❌ Falló la descarga.")
        return

    print("\n🔍 Analizando los precios de 5 productos al azar...")
    for item in datos.get("products", [])[:5]:
        nombre = item.get("name", "Sin nombre")
        ofertas = item.get("offers", [])

        print(f"\n📦 Producto: {nombre}")
        # Imprimimos el bloque de ofertas formateado para leerlo bien
        print(json.dumps(ofertas, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    auditar_json_farma2go()
