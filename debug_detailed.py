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
        product_cards = soup.select('product-card-wrapper')
        print(f"📦 Encontradas {len(product_cards)} tarjetas")
        
        # Analizar las PRIMERAS 3 tarjetas en detalle
        for i, card in enumerate(product_cards[:3]):
            print(f"\n{'='*60}")
            print(f"🔍 TARJETA {i+1}:")
            print(f"{'='*60}")
            
            # 1. Mostrar todos los atributos de la tarjeta
            print("📋 ATRIBUTOS DE LA TARJETA:")
            for attr_name, attr_value in card.attrs.items():
                print(f"   {attr_name}: {attr_value}")
            
            # 2. Buscar elementos específicos de precio
            print("\n💰 BUSCANDO PRECIOS:")
            # Buscar en data attributes
            price_elems = card.find_all(attrs={'data-price': True})
            for elem in price_elems:
                print(f"   Data-price encontrado: {elem['data-price']}")
                print(f"   Elemento: {elem}")
            
            # Buscar spans con clases de precio
            price_spans = card.find_all('span', class_=lambda x: x and 'price' in str(x).lower())
            for span in price_spans:
                print(f"   Span con precio: {span.text}")
            
            # 3. Mostrar TODO el texto de la tarjeta
            print(f"\n📝 TEXTO COMPLETO ({len(card.get_text())} caracteres):")
            print(card.get_text()[:200] + "..." if len(card.get_text()) > 200 else card.get_text())
            
            # 4. Buscar meta tags de precio
            meta_prices = card.find_all('meta', attrs={'itemprop': 'price'})
            for meta in meta_prices:
                print(f"   Meta precio: {meta.get('content')}")
            
            print(f"{'='*60}\n")
            
    else:
        print("❌ No se pudo cargar la página")