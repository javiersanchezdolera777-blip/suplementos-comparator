"""
Configuración centralizada para las tiendas de afiliados e ingestión de feeds.
"""
import os


def _get_tradedoubler_feed_url(fid: str) -> str:
    token = (os.environ.get("TRADEDOUBLER_PRODUCTS_TOKEN") or "").strip()
    return f"https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid={fid}?token={token}" if token else ""


TIENDAS_AFILIADOS = {
    "SportLive": {
        "url_feed": _get_tradedoubler_feed_url("108208"),
        "formato": "json",
        "marca_modo": "fija",
        "marca_defecto": "Drasanví",
        "columnas": {
            "nombre": "name",
            "descripcion": "description",
            "precio": "offers.0.price.value",
            "precio_anterior": "offers.0.previousPrice.value",
            "imagen_url": "productImage.url",
            "afiliado_url": "offers.0.productUrl",
        },
    },
    "Pharma2Go": {
        "url_feed": os.getenv("URL_FEED_PHARMA2GO", _get_tradedoubler_feed_url("256625")),
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
            "peso_gramos": "weight",
        },
    },
}
