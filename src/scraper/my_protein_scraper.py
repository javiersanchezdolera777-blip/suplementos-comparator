from .base_scraper import BaseScraper

class MyProteinScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.myprotein.es"
        self.store = "MyProtein"
    
    def scrape_all_products(self):
        categories = {
            "proteina": "/nutrition-deportiva/proteinas.list",
            "creatina": "/nutrition-deportiva/creatina.list", 
            "pre-entreno": "/nutrition-deportiva/pre-entreno.list"
        }
        
        all_products = []
        
        for category, url_path in categories.items():
            print(f"Scrapeando categoría: {category}")
            products = self.scrape_category(self.base_url + url_path, category)
            all_products.extend(products)
            time.sleep(1)  # Respeta el robots.txt
            
        return all_products
    
    def scrape_category(self, url, category):
        soup = self.get_page(url)
        if not soup:
            return []
        
        products = []
        product_cards = soup.find_all('div', class_='productListProducts_product')[:10]  # Limitar para pruebas
        
        for card in product_cards:
            try:
                name = card.find('h3').text.strip()
                price_text = card.find('span', class_='productPrice_price').text.strip()
                price = float(price_text.replace('€', '').replace(',', '.').strip())
                
                product_data = {
                    'name': name,
                    'category': category,
                    'brand': 'MyProtein',
                    'price': price,
                    'store': self.store,
                    'product_url': self.base_url + card.find('a')['href'],
                    'image_url': card.find('img')['src'] if card.find('img') else None
                }
                
                products.append(product_data)
            except Exception as e:
                print(f"Error procesando producto: {e}")
                continue
        
        return products