# src/scraper/myprotein_scraper.py
import time
import re
import unicodedata
from src.models.product import Product
from .base_scraper import BaseScraper

def normalize_text(text: str) -> str:
    """Normaliza texto a Unicode NFC, preservando tildes y caracteres especiales."""
    if not text:
        return ""
    # Normalización Unicode
    text = unicodedata.normalize("NFC", text)
    return text.strip()

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
            },
            "vitaminas-minerales": {
                "url": "/c/nutrition/vitamins-minerals/",
                "category": "vitaminas y minerales",
                "subcategory": "multivitaminas"
            },
            "barritas-snacks": {
                "url": "/c/nutrition/healthy-food-drinks/",
                "category": "barritas y snacks",
                "subcategory": "barritas-proteicas"
            },
            "recuperacion": {
                "url": "/c/nutrition/recovery/",
                "category": "recuperación",
                "subcategory": "post-entreno"
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
        
        objetivo_mapping = {
            "proteína": "aumento-masa-muscular",
            "creatina": "energía-rendimiento",
            "pre-entreno": "energía-rendimiento", 
            "aminoácidos": "recuperación-muscular",
            "vitaminas y minerales": "salud-general",
            "barritas y snacks": "control-peso",
            "recuperación": "recuperación-muscular"
        }
        
        caracteristicas_mapping = {
            "vegano": "vegano",
            "vegetal": "vegano", 
            "sin lactosa": "sin-lactosa",
            "lactose free": "sin-lactosa",
            "sin gluten": "sin-gluten",
            "gluten free": "sin-gluten",
            "zero": "sin-azúcar",
            "sin azúcar": "sin-azúcar",
            "sugar free": "sin-azúcar",
            "orgánico": "orgánico",
            "organic": "orgánico",
            "natural": "orgánico",
            "non gmo": "sin-OGM",
            "sin ogm": "sin-OGM",
            "low calorie": "bajo-calorías",
            "bajas calorías": "bajo-calorías"
        }
        
        for card in product_cards:
            try:
                # Extraer nombre normalizado
                raw_name = card.get('aria-label', 'Producto sin nombre')
                name = normalize_text(raw_name)

                price_text = card.get_text()
                cleaned_text = normalize_text(price_text)
                
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
                
                # Subcategorías
                subcategory = default_subcategory
                name_lower = name.lower()
                subcategory_map = {
                    "proteína": {
                       
                        "vegan": "proteína-vegana",
                        "vegetal": "proteína-vegana",
                        "casein": "caseína",
                        "caseína": "caseína",
                        "clear": "whey-aislado",
                        "aislado": "whey-aislado",
                        "whey": "whey-protein",
                        "colágeno": "colágeno",
                        "collagen": "colágeno"
                        

                    },
                    "vitaminas y minerales": {
                        "vitamin": "multivitaminas",
                        "mineral": "minerales",
                        "magnesio": "minerales",
                        "zinc": "minerales",
                        "hierro": "minerales",
                        "calcio": "minerales",
                        "vitamina d": "vitamina-d",
                        "vitamina c": "vitamina-c"
                    },
                    "barritas y snacks": {
                        "barrita": "barritas-proteicas",
                        "bar": "barritas-proteicas",
                        "snack": "snacks-proteicos",
                        "proteico": "barritas-proteicas"
                    }
                }
                
                if category in subcategory_map:
                    for keyword, subcat in subcategory_map[category].items():
                        if keyword in name_lower:
                            subcategory = subcat
                            break
                
                # Determinar características
                caracteristicas = []
                for keyword, caracteristica in caracteristicas_mapping.items():
                    if keyword in name_lower:
                        caracteristicas.append(caracteristica)
                caracteristicas = list(set(caracteristicas))
                
                # Tamaño y sabor
                size = ""
                flavor = ""
                size_match = re.search(r'(\d+\.?\d*)\s*(kg|g|lb|oz)', name, re.IGNORECASE)
                if size_match:
                    size = f"{size_match.group(1)}{size_match.group(2)}"
                
                flavor_keywords = ["chocolate", "vainilla", "fresa", "plátano", "cookies", "natural", "limón", "naranja", "coco", "café"]
                for keyword in flavor_keywords:
                    if keyword in name_lower:
                        flavor = keyword.capitalize()
                        break
                
                protein_per_serving = None
                servings_per_container = None
                if category == "proteína":
                    protein_per_serving = 24.0
                
                product_data = {
                    'name': name,
                    'category': normalize_text(category),
                    'subcategory': normalize_text(subcategory),
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
                    'servings_per_container': servings_per_container
                }
                
                products.append(product_data)
                print(f"✅ {name} - {price}€ - Categoría: {category}/{subcategory}")
                
            except Exception as e:
                print(f"❌ Error en producto: {e}")
                continue
        
        return products
