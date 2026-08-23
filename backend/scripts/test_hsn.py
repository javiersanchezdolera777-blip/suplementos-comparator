import requests
from bs4 import BeautifulSoup
import json

# Pega aquí la URL del producto de Swanson que falla
url = "https://www.hsnstore.com/marcas/swanson/gaba-250mg?utm_source=hsnaffiliate&utm_medium=SUPARATOR&utm_campaign=product_0"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"🔍 Analizando URL: {url}\n")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 1. Comprobar qué dice el JSON-LD (Schema.org)
print("--- 📦 DATOS JSON-LD ---")
found_json_ld = False
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string)
        if isinstance(data, dict) and data.get("@type") == "Product":
            found_json_ld = True
            print(json.dumps(data, indent=2))
            print(f"-> Marca detectada en JSON-LD: {data.get('brand')}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    found_json_ld = True
                    print(json.dumps(item, indent=2))
                    print(f"-> Marca detectada en JSON-LD (lista): {item.get('brand')}")
    except Exception:
        pass

if not found_json_ld:
    print("⚠️ No se ha encontrado ningún bloque Product en JSON-LD.")

# 2. Comprobar si hay rastros de la marca en el HTML visual (Francotirador)
print("\n--- 🎯 BUSCANDO PATRONES DE MARCA EN EL HTML ---")
# Buscamos enlaces o bloques que suelan contener la marca en HSN
brand_links = soup.find_all("a", href=lambda href: href and "/marcas/" in href)
for link in brand_links:
    print(f"Enlace de marca encontrado: {link.get_text(strip=True)} (Href: {link.get('href')})")