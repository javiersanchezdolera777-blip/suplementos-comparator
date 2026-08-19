import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse

def auditoria_forense_marca(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    }

    print(f"\n🔍 INICIANDO RADIOGRAFÍA DE: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Error de red: Código {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        html_raw = response.text
        
        # 1. ANÁLISIS DE LA URL
        print("\n🌐 1. ANÁLISIS DE LA URL:")
        path = urlparse(url).path
        match_url = re.search(r'/marcas/([^/]+)/', path)
        if match_url:
            print(f"   ✅ ¡BINGO! Marca detectada en la URL: '{match_url.group(1)}'")
        else:
            print("   ❌ No se encontró patrón de marca en la URL.")

        # 2. ANÁLISIS DEL JSON-LD (El método oficial)
        print("\n📦 2. ANÁLISIS DEL JSON-LD (Schema.org):")
        bloques = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html_raw, flags=re.S|re.I)
        encontrado_json = False
        for i, bloque in enumerate(bloques):
            try:
                data = json.loads(bloque.strip())
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get('@type') == 'Product':
                        brand = item.get('brand')
                        print(f"   ✅ Bloque Product encontrado.")
                        print(f"   👉 Contenido crudo de 'brand': {brand}")
                        encontrado_json = True
            except Exception:
                pass
        if not encontrado_json:
            print("   ❌ No hay etiqueta 'brand' válida en el JSON-LD.")

        # 3. ANÁLISIS DEL DATALAYER (Variables de Analytics ocultas)
        print("\n📊 3. ANÁLISIS DE DATALAYER / VARIABLES JS:")
        match_dl = re.search(r'["\']?item_brand["\']?\s*:\s*["\']([^"\']+)["\']', html_raw)
        if match_dl:
            print(f"   ✅ Encontrado 'item_brand': '{match_dl.group(1)}'")
        else:
            print("   ❌ No se encontró 'item_brand'.")

        # 4. ANÁLISIS DEL HTML ESTRUCTURAL (Lo que se ve en pantalla)
        print("\n👁️ 4. ANÁLISIS HTML VISUAL:")
        
        # Buscamos clases típicas de marcas en Magento/HSN
        elementos_marca = soup.find_all(attrs={"class": re.compile(r'brand|marca|manufacturer', re.I)})
        for el in elementos_marca:
            texto = el.get_text(strip=True)
            if texto and len(texto) < 30:
                print(f"   ✅ Posible marca en HTML (clase '{el.get('class')}'): '{texto}'")
                
        # Buscamos enlaces a la sección de marcas
        enlaces_marca = soup.find_all('a', href=re.compile(r'/marcas/', re.I))
        for a in enlaces_marca:
            texto = a.get_text(strip=True)
            if texto:
                print(f"   ✅ Enlace de marca encontrado: '{texto}' -> {a.get('href')}")

        print("-" * 60)
        print("🏁 RADIOGRAFÍA TERMINADA\n")

    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")

if __name__ == "__main__":
    url_test = "https://www.hsnstore.com/marcas/swanson/msm-500mg?utm_source=hsnaffiliate&utm_medium=SUPARATOR&utm_campaign=product_0"
    auditoria_forense_marca(url_test)