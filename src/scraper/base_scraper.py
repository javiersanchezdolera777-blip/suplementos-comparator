import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
from src import db
from src.models.product import Product

class BaseScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
    
    def get_page(self, url, retries=3, delay=2):
        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f"Intento {attempt + 1} fallido para {url}: {e}")
                time.sleep(delay)
        return None
    
    def scrape_all_products(self):
        """Método que debe ser implementado por cada scraper específico"""
        raise NotImplementedError("Cada scraper debe implementar este método")
    
    def save_product(self, product_data):
        """Guardar o actualizar producto en la base de datos"""
        try:
            # Buscar producto existente
            product = Product.query.filter_by(
                name=product_data['name'],
                store=product_data['store'],
                size=product_data.get('size', '')
            ).first()
            
            if product:
                # Actualizar precio si ha cambiado
                if product.price != product_data['price']:
                    product.update_price(product_data['price'])
                    print(f"Precio actualizado: {product.name} - {product.price}€")
                return product
            else:
                # Crear nuevo producto
                new_product = Product(**product_data)
                new_product.price_history = json.dumps([{
                    'price': product_data['price'],
                    'date': datetime.utcnow().isoformat()
                }])
                db.session.add(new_product)
                print(f"Producto añadido: {product_data['name']}")
                return new_product
                
        except Exception as e:
            print(f"Error guardando producto {product_data['name']}: {e}")
            return None
    
    def run_scraping(self):
        """Ejecutar el scraping y guardar resultados"""
        print(f"Iniciando scraping para {self.__class__.__name__}...")
        products = self.scrape_all_products()
        
        if products:
            for product_data in products:
                self.save_product(product_data)
            
            db.session.commit()
            print(f"Scraping completado. {len(products)} productos procesados.")
        else:
            print("No se encontraron productos.")