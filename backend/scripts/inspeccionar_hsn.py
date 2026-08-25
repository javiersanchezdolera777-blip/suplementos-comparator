import os
import sys
import re
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestores.http_client import create_session, get_with_backoff
from ingestores.utils import extraer_presentacion


def inspeccionar_dom_hsn():
    print("🔍 Inspeccionando el DOM y texto de HSN en busca de tamaños ocultos...")
    session = create_session(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.hsnstore.com/",
        }
    )

    url_prueba = "https://www.hsnstore.com/marcas/sport-series/evodren"
    print(f"🌐 Descargando: {url_prueba}")

    try:
        res = get_with_backoff(session, url_prueba, timeout=20)
        if res.status_code != 200:
            print(f"❌ Error HTTP: {res.status_code}")
            return

        soup = BeautifulSoup(res.text, "html.parser")

        print("\n--- 1. BUSCANDO PATRONES DE TAMAÑO EN TODO EL TEXTO DE LA PÁGINA ---")
        texto_completo = soup.get_text()

        # Probamos a aplicar nuestro extractor de NLP directamente sobre el texto plano de la web
        pres_encontrada = extraer_presentacion(texto_completo)
        print(
            f"🎯 Resultado de aplicar extraer_presentacion al texto completo: {pres_encontrada}"
        )

        # Buscamos líneas cortas específicas que contengan números y unidades comunes
        print(
            "\n--- 2. LÍNEAS CANDIDATAS EN EL TEXTO (con unidades de peso/volumen/unidades) ---"
        )
        lineas = texto_completo.split("\n")
        candidatas = []
        for linea in lineas:
            l_limpia = linea.strip()
            if re.search(
                r"\d+\s*(kg|g|gr|ml|cápsulas|caps|perlas|comprimidos|tabletas|pastillas|viales|sobres|dosis)\b",
                l_limpia,
                re.I,
            ):
                if len(l_limpia) < 60:  # Evitar bloques de texto largos de los párrafos
                    candidatas.append(l_limpia)

        # Eliminar duplicados manteniendo el orden
        candidatas_unicas = list(dict.fromkeys(candidatas))
        for c in candidatas_unicas[:20]:
            print(f"   • {c}")

        print("\n--- 3. BUSCANDO ELEMENTOS SELECT (Desplegables de formatos) ---")
        selects = soup.find_all("select")
        print(f"Encontrados {len(selects)} elementos <select>.")
        for sel in selects:
            print(f"   - Select ID/Name: {sel.get('id')} / {sel.get('name')}")
            options = sel.find_all("option")
            for opt in options:
                print(f"     -> Opción: '{opt.get_text(strip=True)}'")

        print("\n--- 4. BUSCANDO CLASES DE SWATCHES / VARIANTES EN EL HTML ---")
        botones = soup.find_all(
            class_=re.compile(r"option|swatch|size|variant|item", re.I)
        )
        print(f"Elementos encontrados con esas clases ({len(botones)}):")
        for b in botones[:15]:
            t = b.get_text(strip=True)
            if t and len(t) < 40:
                print(f"   - Clase: {b.get('class')} | Texto: '{t}'")

    except Exception as e:
        print(f"❌ Error durante la inspección del DOM: {e}")


if __name__ == "__main__":
    inspeccionar_dom_hsn()
