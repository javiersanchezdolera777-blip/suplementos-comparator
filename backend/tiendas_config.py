"""
Configuración centralizada para las tiendas de afiliados e ingestión de feeds.
"""
import os

TIENDAS_AFILIADOS = {
    "SportLive": {
        "url_feed": "https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=108208?token=D496D89D3425492898437BED5EE5EEB677232059",
        "formato": "json",
        "marca_modo": "fija",
        "marca_defecto": "Drasanví",
        "columnas": {
            "nombre": "name",
            "descripcion": "description",
            "precio": "offers.0.price.value",
            "precio_anterior": "offers.0.previousPrice.value",
            "imagen_url": "productImage.url",
            "afiliado_url": "offers.0.productUrl"
        }
    },
    "Pharma2Go": {
        "url_feed": os.getenv("URL_FEED_PHARMA2GO", "https://api.tradedoubler.com/1.0/productsUnlimited.json;fid=256625?token=D496D89D3425492898437BED5EE5EEB677232059"),
        "formato": "json",
        "delimitador": ",",
        "encoding": "utf-8",
        "marca_modo": "columna",
        "marca_defecto": "Desconocida",
        "columna_marca": "brand",
        "base_url_imagen": None,
        "columnas": {
            "nombre": "name",
            "descripcion": "description",
            "precio": ["offers.0.priceHistory.0.price.value", "offers.0.price.value", "price"],
            "precio_anterior": ["offers.0.previousPrice.value", "offers.0.priceHistory.0.previousPrice.value"],
            "imagen_url": "productImage.url",
            "afiliado_url": ["offers.0.productUrl", "offers.0.feedOfferUrl"],
            "peso_gramos": "weight"
        }
    }
}
