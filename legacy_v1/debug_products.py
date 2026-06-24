import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app
from scraper.myprotein_scraper import MyProteinScraper

app = create_app()

with app.app_context():
    scraper = MyProteinScraper()
    
    # Probar solo una categoría
    url = "https://www.myprotein.es/c/nutrition/protein/"
    print(f"🔍 Analizando: {url}")
    
    soup = scraper.get_page(url)
    if soup:
        # Buscar TODAS las tarjetas de producto
        product_cards = soup.select('product-card-wrapper') or \
                       soup.select('[data-e2e="product-list"] product-card-wrapper') or \
                       soup.select('.product-list-contents product-card-wrapper')
        
        print(f"📦 Encontradas {len(product_cards)} tarjetas")
        
        # Analizar la PRIMERA tarjeta en detalle
        if product_cards:
            first_card = product_cards[0]
            print("\n" + "="*50)
            print("🔍 CONTENIDO DE LA PRIMERA TARJETA:")
            print("="*50)
            
            # Mostrar HTML de la tarjeta
            print("HTML:", str(first_card)[:200] + "...")
            
            # Mostrar texto completo
            print("\n📝 TEXTO COMPLETO:", first_card.get_text()[:100] + "...")
            
            # Buscar elementos comunes
            print("\n🔎 ELEMENTOS ENCONTRADOS:")
            print("Nombre (h3):", first_card.find('h3'))
            print("Nombre (h4):", first_card.find('h4'))
            print("Precio (span):", first_card.find('span'))
            print("Enlace (a):", first_card.find('a'))
            print("Imagen (img):", first_card.find('img'))
            
            # Buscar por atributos data
            print("\n💰 ATRIBUTOS DATA:")
            for elem in first_card.find_all(attrs={'data-price': True}):
                print("Data-price:", elem['data-price'])
            
    else:
        print("❌ No se pudo cargar la página")