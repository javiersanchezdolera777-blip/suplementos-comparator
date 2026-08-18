import requests
import re
import json

urls = [
    "https://www.hsnstore.com/marcas/essential-series/sulforafano-de-brocoli-10mg-200mg-sulfodyne",
    "https://www.hsnstore.com/marcas/food-series/hummus-proteico-en-polvo"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for url in urls:
    print(f"\n{'='*50}\n🔍 JSON-LD: {url.split('/')[-1]}\n{'='*50}")
    res = requests.get(url, headers=headers)
    
    bloques = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', res.text, flags=re.S|re.I)
    encontrado = False
    for bloque in bloques:
        try:
            contenido = json.loads(bloque.strip())
            if isinstance(contenido, dict) and contenido.get('@type') == 'Product':
                print(f"✅ PRODUCTO ENCONTRADO:")
                print(f"Nombre: {contenido.get('name')}")
                
                offers = contenido.get('offers')
                print(f"Offers type: {type(offers)}")
                if isinstance(offers, dict):
                    print(f"Precio: {offers.get('price')}")
                    print(f"Disponibilidad: {offers.get('availability')}")
                elif isinstance(offers, list):
                    print(f"Múltiples offers ({len(offers)})")
                    for o in offers:
                        print(f" - {o.get('price')} / {o.get('availability')}")
                        
                encontrado = True
            elif isinstance(contenido, list):
                for item in contenido:
                    if isinstance(item, dict) and item.get('@type') == 'Product':
                        print(f"✅ PRODUCTO (en lista) ENCONTRADO: {item.get('name')}")
                        offers = item.get('offers')
                        if isinstance(offers, dict):
                            print(f"Precio: {offers.get('price')} | Disp: {offers.get('availability')}")
                        encontrado = True
        except Exception as e:
            pass
            
    if not encontrado:
        print("❌ NO HAY JSON-LD DE TIPO PRODUCT!")
