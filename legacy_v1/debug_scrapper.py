# debug_scraper.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app
from scraper.myprotein_scraper import MyProteinScraper

app = create_app()

with app.app_context():
    scraper = MyProteinScraper()
    
    # Probar una categoría específica con debugging
    url = "https://www.myprotein.es/c/nutrition/protein/"
    print(f"🔍 Probando URL: {url}")
    
    soup = scraper.get_page(url)
    if soup:
        print("✅ Página cargada correctamente")
        
        # Guardar el HTML para analizarlo
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("📁 HTML guardado en 'debug_page.html'")
        
        # Buscar todos los elementos con clases que contengan "product"
        product_elements = soup.find_all(class_=lambda x: x and 'product' in x.lower())
        print(f"🔍 Elementos con 'product' en clase: {len(product_elements)}")
        
        for i, elem in enumerate(product_elements[:5]):  # Mostrar primeros 5
            print(f"Elemento {i}: {elem.get('class')}")
            
    else:
        print("❌ No se pudo cargar la página")