import time
from .base_scraper import BaseScraper

class MyProteinScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.myprotein.es"
        self.store = "MyProtein"
    
    def scrape_all_products(self):
        categories = {
            "proteina": "/c/nutrition/protein/",
            "creatina": "/c/nutrition/creatine/", 
            "pre-entreno": "/c/nutrition/pre-post-workout/pre-workout/",
            "aminoacidos": "/c/nutrition/amino-acids/"
        }
        
        all_products = []
        
        for category, url_path in categories.items():
            print(f"Scrapeando categoría: {category}")
            products = self.scrape_category(self.base_url + url_path, category)
            all_products.extend(products)
            time.sleep(2)
        
        return all_products
    
    def scrape_category(self, url, category):  # ← ¡ESTA LÍNEA DEBE ESTAR ALINEADA!
        soup = self.get_page(url)
        if not soup:
            return []
        
        products = []
        
        # SELECTORES CORRECTOS
        product_cards = soup.select('product-card-wrapper')
        
        print(f"Encontradas {len(product_cards)} tarjetas de producto")
        
        for card in product_cards:
            try:
                # ✅ NOMBRE - del atributo aria-label
                name = card.get('aria-label', 'Producto sin nombre')
        
                 # ✅ CORREGIR CARACTERES ESPECIALES - AÑADE ESTO
                import unicodedata
                name = unicodedata.normalize('NFKD', name).encode('latin-1', 'ignore').decode('utf-8', 'ignore')
                
                # ✅ PRECIO - Extraer del texto (arreglando caracteres)
                price_text = card.get_text()
                
                # Limpiar caracteres extraños y buscar precio
                import re
                cleaned_text = price_text.encode('latin-1').decode('utf-8', errors='ignore')
                
                # Buscar patrones de precio: "23,99 €" o "discounted price 23,99"
                price_match = re.search(r'(\d+[\.,]\d+)\s*€', cleaned_text)
                if not price_match:
                    price_match = re.search(r'discounted price\s*(\d+[\.,]\d+)', cleaned_text)
                
                if price_match:
                    price = float(price_match.group(1).replace(',', '.'))
                else:
                    print(f"❌ No se pudo extraer precio de: {cleaned_text[:50]}...")
                    continue
                
                # ✅ PRECIO ORIGINAL - Buscar precio anterior
                original_price = price
                original_match = re.search(r'Antes\s*(\d+[\.,]\d+)', cleaned_text)
                if original_match:
                    original_price = float(original_match.group(1).replace(',', '.'))
                
                # ✅ RATING - Buscar rating de estrellas
                rating = 4.0
                rating_match = re.search(r'(\d+[\.,]\d+)\s*out of 5 stars', cleaned_text)
                if rating_match:
                    rating = float(rating_match.group(1).replace(',', '.'))
                
                # ✅ URL - del enlace
                link_elem = card.find('a')
                product_url = self.base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
                
                # ✅ IMAGEN - de la etiqueta img
                img_elem = card.find('img')
                image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''
                
                product_data = {
                    'name': name.strip(),
                    'category': category,
                    'brand': 'MyProtein',
                    'price': price,
                    'original_price': original_price,
                    'rating': rating,
                    'store': self.store,
                    'product_url': product_url,
                    'image_url': image_url,
                    'size': '',
                    'flavor': ''
                }
                
                products.append(product_data)
                print(f"✅ {name} - {price}€ - ⭐ {rating} - Antes {original_price}€")
                
            except Exception as e:
                print(f"❌ Error en producto: {e}")
                continue
        
        return products