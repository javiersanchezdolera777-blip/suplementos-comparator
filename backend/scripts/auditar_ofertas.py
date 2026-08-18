import json
import os

def auditar_cache(archivo_json, nombre_tienda):
    ruta = os.path.join(os.path.dirname(__file__), '..', 'cache_ingestores', archivo_json)
    
    if not os.path.exists(ruta):
        print(f"❌ No se encontró el archivo {ruta}")
        return

    with open(ruta, 'r', encoding='utf-8') as f:
        try:
            datos = json.load(f)
            # Farma2Go y Sportlive a veces guardan un array directo o un dict con clave 'products'
            productos = datos if isinstance(datos, list) else datos.get('products', [])
        except json.JSONDecodeError:
            print(f"❌ Error al leer el JSON de {nombre_tienda}")
            return

    total = len(productos)
    ofertas_reales = 0

    print(f"\n🔍 Analizando datos crudos de {nombre_tienda}...")
    for p in productos:
        # Extraemos precios según el formato del feed de Tradedoubler
        precio_actual = p.get('price', {}).get('value') if isinstance(p.get('price'), dict) else p.get('price')
        precio_antiguo = p.get('previousPrice', {}).get('value') if isinstance(p.get('previousPrice'), dict) else p.get('previousPrice')

        try:
            p_act = float(precio_actual) if precio_actual else 0.0
            p_ant = float(precio_antiguo) if precio_antiguo else 0.0
            
            if p_ant > p_act:
                ofertas_reales += 1
        except (ValueError, TypeError):
            continue

    print(f"📦 Total productos en el feed: {total}")
    print(f"🏷️  Productos que declaran un descuento real: {ofertas_reales}")

if __name__ == "__main__":
    auditar_cache('farma2go_temporal.json', 'Farma2Go')
    auditar_cache('sportlive_temporal.json', 'Sportlive')