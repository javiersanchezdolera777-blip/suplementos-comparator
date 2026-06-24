# run_scrapping.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from src.scraper.myprotein_scraper import MyProteinScraper

def run_scraping():
    app = create_app()
    
    with app.app_context():  # ← Asegurar el contexto de la aplicación
        print("🚀 Iniciando scraping de MyProtein...")
        
        scraper = MyProteinScraper()
        scraper.run_scraping()
        
        print("✅ Scraping completado!")
        
        # Verificar resultados
        from src.models.product import Product
        count = Product.query.count()
        print(f"📊 Total de productos en la base de datos: {count}")

if __name__ == '__main__':
    run_scraping()