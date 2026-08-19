import sys
import os
import re
import json
from bs4 import BeautifulSoup

# Añadir ruta del backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestores.http_client import create_session, get_with_backoff


def probar_extraccion_swanson():
    # Usar las cabeceras exactas del scraper maestro para evitar el 403
    session = create_session(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Referer": "https://www.hsnstore.com/",
        }
    )

    url = "https://www.hsnstore.com/l-triptofano-500mg"
    print(f"🌐 Conectando de forma furtiva a: {url}")

    res = get_with_backoff(session, url)
    print(f"✅ Estado HTTP recibido: {res.status_code}")

    soup = BeautifulSoup(res.text, "html.parser")

    print("\n--- 1. TITLE DE LA PÁGINA ---")
    title_tag = soup.find("title")
    print(title_tag.text if title_tag else "No hay etiqueta title")

    print("\n--- 2. ENLACES DE MARCA (/marcas/) EN EL HTML ---")
    enlaces_marca = soup.find_all("a", href=re.compile(r"/marcas/([^/]+)", re.I))
    for a in enlaces_marca:
        print(
            f"  👉 Encontrado enlace: href='{a.get('href')}' | Texto: '{a.get_text(strip=True)}'"
        )

    print("\n--- 3. BLOQUES JSON-LD (Schema.org) ---")
    bloques = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        res.text,
        flags=re.S | re.I,
    )
    encontrado_brand = False
    for b in bloques:
        try:
            contenido = json.loads(b.strip())
            if isinstance(contenido, dict) and contenido.get("@type") == "Product":
                print("  📦 Producto JSON-LD detectado:")
                print(f"     - Nombre: {contenido.get('name')}")
                print(f"     - Brand: {contenido.get('brand')}")
                encontrado_brand = True
            elif isinstance(contenido, list):
                for item in contenido:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        print("  📦 Producto JSON-LD (en lista) detectado:")
                        print(f"     - Nombre: {item.get('name')}")
                        print(f"     - Brand: {item.get('brand')}")
                        encontrado_brand = True
        except Exception:
            pass
    if not encontrado_brand:
        print("  ⚠️ No se encontró la entidad Product en el JSON-LD.")


if __name__ == "__main__":
    probar_extraccion_swanson()
