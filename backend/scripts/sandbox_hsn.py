import sys
import os
import requests
import re

# Conectamos con el clasificador real de tu proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestores.utils import clasificar_producto, limpiar_texto


def simulacion_completa_hsn():
    url = "https://www.hsnstore.com/marcas/sport-series/evowhey-protein-2-0"
    print(f"🔬 CONECTANDO A HSN: {url} ...")

    # Le ponemos el "disfraz" completo idéntico al de tu hsn.py para saltar el anti-bots
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.hsnstore.com/",
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Error de red. HSN devolvió el código HTTP: {res.status_code}")
        return

    print("✅ Conexión establecida. Extrayendo datos...")

    # 1. Simular la extracción de datos básicos
    nombre = "Evowhey Protein 2.0"
    desc_cruda = (
        "<p>Proteína concentrada de suero de leche. Hasta 80% de proteínas.</p>"
    )
    desc_limpia = limpiar_texto(desc_cruda)

    # 2. El Cazador de Javascript Decodificado
    etiquetas_js = re.findall(r'"label"\s*:\s*"([^"]+)"', res.text, re.IGNORECASE)
    sabores_limpios = []
    for etiqueta in etiquetas_js:
        try:
            # Magia para transformar \u00f3 en ó, etc.
            decodificado = etiqueta.encode("utf-8").decode("unicode_escape")
            sabores_limpios.append(decodificado)
        except:
            sabores_limpios.append(etiqueta)

    texto_sabores_extra = " ".join(sabores_limpios).lower()

    # 3. Fusionamos
    desc_ampliada_para_cerebro = f"{desc_limpia} {texto_sabores_extra}"

    # 4. Pasamos el texto al cerebro
    print("🧠 PASANDO DATOS AL CEREBRO CLASIFICADOR (utils.py)...")
    etiquetas = clasificar_producto(nombre, desc_ampliada_para_cerebro)

    print("\n" + "=" * 50)
    print("🎯 RESULTADO DE LA SIMULACIÓN PARA EVOWHEY")
    print("=" * 50)
    print(f"📦 FORMATO DETECTADO: {etiquetas.get('formato')}")
    print(f"👅 SABORES DETECTADOS: {etiquetas.get('sabor')}")
    print(f"💪 CATEGORÍA:       {etiquetas.get('categoria')}")
    print(f"📈 % PROTEÍNA:      {etiquetas.get('porcentaje_proteina')}%")
    print("=" * 50)


if __name__ == "__main__":
    simulacion_completa_hsn()
