import requests
from bs4 import BeautifulSoup
import re

urls = [
    "https://www.hsnstore.com/marcas/essential-series/sulforafano-de-brocoli-10mg-200mg-sulfodyne",
    "https://www.hsnstore.com/marcas/food-series/hummus-proteico-en-polvo"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for url in urls:
    nombre = url.split('/')[-1]
    print(f"\n{'='*50}\n🔍 ANALIZANDO: {nombre}\n{'='*50}")
    
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 1. Búsqueda de Stock
    print("\n📦 --- ESTADO DE STOCK ---")
    meta = soup.find('meta', {'itemprop': 'availability'})
    print(f"Meta 'availability': {meta.get('content') if meta else 'NO ENCONTRADO'}")
    
    stock_div = soup.find(class_=re.compile(r'stock|availability'))
    if stock_div:
        print(f"Contenedor visual de stock: <{stock_div.name} class='{stock_div.get('class')}'> -> '{stock_div.text.strip()}'")

    # 2. Búsqueda de Precios en el contenedor principal
    print("\n💰 --- ESTRUCTURA DE PRECIOS ---")
    main = soup.find(class_='product-info-main')
    
    if main:
        # Buscamos cualquier elemento que tenga la palabra 'price' en su clase
        precios = main.find_all(class_=re.compile(r'price', re.I))
        visitados = set()
        
        for p in precios:
            # Limpiamos el texto para que se lea bien en la consola
            texto = p.text.replace('\n', '').replace(' ', '').strip()
            if texto and texto not in visitados:
                print(f"Etiqueta: <{p.name} class='{p.get('class')}'> | Texto: '{texto}'")
                visitados.add(texto)
                
        # Cazador directo de símbolos de Euro por si no usan la clase 'price'
        euros = main.find_all(string=lambda t: '€' in t if t else False)
        print("\n🔎 Elementos sueltos con símbolo '€':")
        for e in euros:
            padre = e.parent
            texto = e.strip()
            if texto:
                print(f"Texto: '{texto}' | Tag padre: <{padre.name} class='{padre.get('class')}'>")
    else:
        print("❌ No se encontró la caja principal 'product-info-main'. ¡Han cambiado toda la web!")
