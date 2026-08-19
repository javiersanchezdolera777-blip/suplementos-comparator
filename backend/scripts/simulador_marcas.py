import sys
import os
import re
import json
from bs4 import BeautifulSoup

# Añadir ruta del backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestores.http_client import create_session, get_with_backoff


def simular_extraccion():
    session = create_session(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
    )

    # Probamos con la URL exacta de tu captura
    url_prod = "https://www.hsnstore.com/marcas/swanson/l-triptofano-500mg"
    print(f"🌐 Conectando a: {url_prod}...")

    res = get_with_backoff(session, url_prod)
    if res.status_code != 200:
        print("❌ Error de conexión.")
        return

    soup_prod = BeautifulSoup(res.text, "html.parser")

    # Simulamos lo que lee el scraper de nombre y JSON-LD
    nombre = (
        soup_prod.find("title").text
        if soup_prod.find("title")
        else "L-triptófano 500mg"
    )
    datos_producto = {}
    bloques = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        res.text,
        flags=re.S | re.I,
    )
    for b in bloques:
        try:
            c = json.loads(b.strip())
            if isinstance(c, dict) and c.get("@type") == "Product":
                datos_producto = c
        except:
            pass

    # ========================================================
    # 🎯 AQUÍ VA EL CÓDIGO EXACTO DE LAS 4 FASES QUE ESTAMOS PROBANDO
    # ========================================================
    brand_raw = "HSN"

    # FASE 1: JSON-LD
    brand_info = datos_producto.get("brand")
    if isinstance(brand_info, dict):
        if brand_info.get("name", "").strip().upper() != "HSN":
            brand_raw = brand_info.get("name", "").strip().title()

    # FASE 2: URL
    if brand_raw.upper() == "HSN" and "/marcas/" in url_prod:
        partes = url_prod.split("/marcas/")
        if len(partes) > 1:
            posible = partes[1].split("/")[0].strip().lower()
            if posible not in [
                "hsn",
                "hsn-accessories",
                "essential-series",
                "raw-series",
                "sport-series",
                "food-series",
            ]:
                brand_raw = posible.replace("-", " ").title()

    # FASE 3: HTML
    if brand_raw.upper() == "HSN":
        enlaces_marca = soup_prod.find_all(
            "a", href=re.compile(r"/marcas/([^/]+)", re.I)
        )
        for a in enlaces_marca:
            match_href = re.search(r"/marcas/([^/?]+)", a.get("href", ""), re.I)
            if match_href:
                posible = match_href.group(1).strip().lower()
                if posible not in [
                    "hsn",
                    "hsn-accessories",
                    "essential-series",
                    "raw-series",
                    "sport-series",
                    "food-series",
                ]:
                    brand_raw = posible.replace("-", " ").title()
                    break

    # FASE 4: REGEX
    if brand_raw.upper() == "HSN":
        marcas_blancas = [r"Swanson", r"NOW Foods", r"Amix", r"Weider", r"Lamberts"]
        patron = r"\b(" + "|".join(marcas_blancas) + r")\b"
        match = re.search(patron, nombre, re.IGNORECASE)
        if not match:
            match = re.search(patron, url_prod, re.IGNORECASE)
        if not match and soup_prod.find("title"):
            match = re.search(patron, soup_prod.find("title").text, re.IGNORECASE)
        if not match:
            match = re.search(patron, soup_prod.get_text(), re.IGNORECASE)
        if match:
            brand_raw = match.group(1).title()

    print(f"\n✅ RESULTADO DEL SIMULADOR:")
    print(f"   La marca que se guardaría en BD es: {brand_raw}")


if __name__ == "__main__":
    simular_extraccion()
