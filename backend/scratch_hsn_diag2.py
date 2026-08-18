import requests
from bs4 import BeautifulSoup
import re

urls = [
    "https://www.hsnstore.com/marcas/essential-series/sulforafano-de-brocoli-10mg-200mg-sulfodyne",
    "https://www.hsnstore.com/marcas/food-series/hummus-proteico-en-polvo"
]
headers = {'User-Agent': 'Mozilla/5.0'}

for url in urls:
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    print(f"\n== {url.split('/')[-1]} ==")
    
    # ¿Hay algún elemento con data-price-amount?
    precios = soup.select('[data-price-amount]')
    print(f"Elementos con data-price-amount: {len(precios)}")
    for p in precios:
        print(f" - {p.name} class={p.get('class')} | data-price-amount={p.get('data-price-amount')}")
        
    # ¿Y qué hay de stock?
    stock_btn = soup.select_one('#product-addtocart-button')
    print(f"Botón de añadir al carrito: {stock_btn is not None}")
    
    # Out of stock div?
    oos = soup.find(class_=re.compile(r'outofstock|unavailable|agotado', re.I))
    print(f"Div de agotado: {oos.text.strip() if oos else 'NO ENCONTRADO'}")
