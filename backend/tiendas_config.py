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
    },
    "Bulk": {
        "url_feed": "https://example.com/feeds/bulk_feed.csv",
        "formato": "csv",
        "delimitador": ",",
        "encoding": "utf-8",
        "marca_modo": "fija",
        "marca_defecto": "Bulk",
        "columna_marca": None,
        "base_url_imagen": None,
        "columnas": {
            "nombre": "Title",
            "descripcion": "Description",
            "precio": "Price",
            "precio_anterior": "Retail Price",
            "imagen_url": "Image URL",
            "afiliado_url": "Product URL",
            "peso_gramos": "Grammage"
        }
    },
    "MyProtein": {
        "url_feed": "https://example.com/feeds/myprotein_feed.tsv",
        "formato": "tsv",
        "delimitador": "\t",
        "encoding": "utf-8",
        "marca_modo": "fija",
        "marca_defecto": "MyProtein",
        "columna_marca": None,
        "base_url_imagen": None,
        "columnas": {
            "nombre": "product_name",
            "descripcion": "description",
            "precio": "price",
            "precio_anterior": "regular_price",
            "imagen_url": "image_url",
            "afiliado_url": "affiliate_url",
            "peso_gramos": "weight_g"
        }
    }
}
