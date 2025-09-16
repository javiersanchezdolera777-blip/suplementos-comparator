# src/scraper/myprotein_scraper.py
import time
import re
import unicodedata
from src.models.product import Product
from .base_scraper import BaseScraper

class MyProteinScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.myprotein.es"
        self.store = "MyProtein"
    
    def scrape_all_products(self):
        categories = {
            "proteina": {
                "url": "/c/nutrition/protein/",
                "category": "proteína",
                "subcategory": "whey-protein"
            },
            "creatina": {
                "url": "/c/nutrition/creatine/", 
                "category": "creatina",
                "subcategory": "monohidrato"
            },
            "pre-entreno": {
                "url": "/c/nutrition/pre-post-workout/pre-workout/",
                "category": "pre-entreno",
                "subcategory": "con-cafeina"
            },
            "aminoacidos": {
                "url": "/c/nutrition/amino-acids/",
                "category": "aminoácidos",
                "subcategory": "bcaa"
            }
        }
        
        all_products = []
        
        for category_name, category_info in categories.items():
            print(f"Scrapeando categoría: {category_name}")
            products = self.scrape_category(
                self.base_url + category_info["url"], 
                category_info["category"],
                category_info["subcategory"]
            )
            all_products.extend(products)
            time.sleep(2)
        
        return all_products
    
    def scrape_category(self, url, category, default_subcategory):
        soup = self.get_page(url)
        if not soup:
            return []
        
        products = []
        product_cards = soup.select('product-card-wrapper')
        print(f"Encontradas {len(product_cards)} tarjetas de producto")
        
        # Mapeo de objetivos según categoría
        objetivo_mapping = {
            "proteína": "aumento-masa-muscular",
            "creatina": "energía-rendimiento",
            "pre-entreno": "energía-rendimiento", 
            "aminoácidos": "recuperación-muscular"
        }
        
        # Mapeo de características según palabras clave en el nombre
        caracteristicas_mapping = {
            "vegano": "vegano",
            "vegetal": "vegano", 
            "sin lactosa": "sin-lactosa",
            "sin gluten": "sin-gluten",
            "zero": "sin-azúcar",
            "orgánico": "orgánico",
            "natural": "orgánico"
        }
        
        for card in product_cards:
            try:
                # Extraer nombre
                name = card.get('aria-label', 'Producto sin nombre')
                name = unicodedata.normalize('NFKD', name).encode('latin-1', 'ignore').decode('utf-8', 'ignore')
                
                # Extraer precio
                price_text = card.get_text()
                cleaned_text = price_text.encode('latin-1').decode('utf-8', errors='ignore')
                
                price_match = re.search(r'(\d+[\.,]\d+)\s*€', cleaned_text)
                if not price_match:
                    price_match = re.search(r'discounted price\s*(\d+[\.,]\d+)', cleaned_text)
                
                if price_match:
                    price = float(price_match.group(1).replace(',', '.'))
                else:
                    print(f"❌ No se pudo extraer precio de: {cleaned_text[:50]}...")
                    continue
                
                # Precio original
                original_price = price
                original_match = re.search(r'Antes\s*(\d+[\.,]\d+)', cleaned_text)
                if original_match:
                    original_price = float(original_match.group(1).replace(',', '.'))
                
                # Rating
                rating = 4.0
                rating_match = re.search(r'(\d+[\.,]\d+)\s*out of 5 stars', cleaned_text)
                if rating_match:
                    rating = float(rating_match.group(1).replace(',', '.'))
                
                # URL
                link_elem = card.find('a')
                product_url = self.base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
                
                # Imagen
                img_elem = card.find('img')
                image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''
                
                # Determinar subcategoría basada en el nombre
                subcategory = default_subcategory
                name_lower = name.lower()
                
                if "vegan" in name_lower or "vegetal" in name_lower:
                    subcategory = "proteína-vegana"
                elif "casein" in name_lower or "caseína" in name_lower:
                    subcategory = "caseína"
                elif "clear" in name_lower or "aislado" in name_lower:
                    subcategory = "whey-aislado"
                elif "gain" in name_lower or "ganar" in name_lower:
                    subcategory = "ganador-de-peso"
                
                # Determinar características
                caracteristicas = []
                for keyword, caracteristica in caracteristicas_mapping.items():
                    if keyword in name_lower:
                        caracteristicas.append(caracteristica)
                
                # Determinar tamaño y sabor (aproximado)
                size = ""
                flavor = ""
                size_match = re.search(r'(\d+\.?\d*)\s*(kg|g|lb|oz)', name, re.IGNORECASE)
                if size_match:
                    size = f"{size_match.group(1)}{size_match.group(2)}"
                
                # Extraer sabor de nombre (ej: "Chocolate", "Vainilla")
                flavor_keywords = ["chocolate", "vainilla", "fresa", "plátano", "cookies", "natural", "limón"]
                for keyword in flavor_keywords:
                    if keyword in name_lower:
                        flavor = keyword.capitalize()
                        break
                
                # Proteína por porción (estimación basada en categoría)
                protein_per_serving = None
                if category == "proteína":
                    protein_per_serving = 24.0  # Valor promedio
                
                product_data = {
                    'name': name.strip(),
                    'category': category,
                    'subcategory': subcategory,
                    'brand': 'MyProtein',
                    'price': price,
                    'original_price': original_price,
                    'rating': rating,
                    'store': self.store,
                    'product_url': product_url,
                    'image_url': image_url,
                    'size': size,
                    'flavor': flavor,
                    'objetivo': objetivo_mapping.get(category, ""),
                    'caracteristicas': ",".join(caracteristicas),
                    'protein_per_serving': protein_per_serving,
                    'servings_per_container': None  # Se puede intentar extraer después
                }
                
                products.append(product_data)
                print(f"✅ {name} - {price}€ - Categoría: {category}/{subcategory}")
                
            except Exception as e:
                print(f"❌ Error en producto: {e}")
                continue
        
        return products