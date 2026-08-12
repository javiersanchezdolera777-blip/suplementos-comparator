import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuración de Entorno
DB_URL = os.getenv("DATABASE_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def format_deal_message(product):
    """Genera la plantilla del mensaje en formato HTML de Telegram"""
    name = product['name']
    brand = product['brand'] or 'Oficial'
    store = product['store'] or 'Tienda oficial'
    current_price = product['current_price']
    previous_price = product['previous_price']
    discount = product['discount']
    price_per_kg = product['price_per_kg']
    affiliate_url = product['affiliate_url']

    # Encabezado y precios
    caption = f"🔥 <b>¡CHOLLO DESTACADO!</b> 🔥\n\n"
    caption += f"💊 <b>{name}</b>\n"
    caption += f"🏷️ <b>Marca:</b> {brand}\n"
    caption += f"🛒 <b>Vendido por:</b> {store}\n\n"
    
    caption += f"💥 <b>Precio:</b> <code>{current_price:.2f} €</code> "
    if previous_price:
        caption += f"<s>{previous_price:.2f} €</s> "
    caption += f"(<b>-{discount}%</b>)\n"

    if price_per_kg and price_per_kg > 0:
        caption += f"📊 <b>Ratio:</b> <code>{price_per_kg:.2f} € / kg</code>\n"

    caption += f"\n🔗 <a href='{affiliate_url}'>👉 VER OFERTA EN LA TIENDA</a>"
    
    return caption

def send_telegram_deal(photo_url, caption):
    """Envía la foto y el texto del chollo a Telegram mediante la API HTTP"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Error: Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el .env")
        return False

    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML"
    }

    try:
        if photo_url:
            # Intentar enviar foto primero
            payload["photo"] = photo_url
            payload["caption"] = caption
            response = requests.post(f"{base_url}/sendPhoto", json=payload, timeout=10)
            res_data = response.json()
            if res_data.get("ok"):
                print("✅ Chollo (con foto) publicado con éxito en Telegram.")
                return True
            else:
                print(f"⚠️ Error enviando foto, haciendo fallback a texto: {res_data.get('description')}")
        
        # Fallback a texto si no hay foto o si sendPhoto falla (ej: URL inválida)
        payload.pop("photo", None)
        payload.pop("caption", None)
        payload["text"] = caption
        
        response = requests.post(f"{base_url}/sendMessage", json=payload, timeout=10)
        res_data = response.json()
        if res_data.get("ok"):
            print("✅ Chollo (solo texto) publicado con éxito en Telegram.")
            return True
        else:
            print(f"⚠️ Error enviando a Telegram: {res_data.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error de red al conectar con Telegram: {e}")
        return False

def fetch_best_deals(limit=1, min_discount=15):
    """Consulta la base de datos en busca de los mejores chollos no publicados recientemente"""
    if not DB_URL:
        print("❌ Error: DATABASE_URL no está configurada.")
        return []

    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    # Query para sacar productos con oferta mayor o igual al min_discount %
    query = """
        SELECT 
            p.id,
            p.nombre,
            p.imagen_url,
            p.afiliado_url,
            p.precio,
            p.precio_anterior,
            p.precio_por_kg,
            m.nombre AS marca,
            p.tienda
        FROM productos p
        LEFT JOIN marcas m ON p.marca_id = m.id
        WHERE p.precio_anterior IS NOT NULL 
          AND p.precio_anterior > p.precio
          AND p.publicado_telegram = FALSE
          AND ROUND(((p.precio_anterior - p.precio) / p.precio_anterior) * 100) >= %s
        ORDER BY ROUND(((p.precio_anterior - p.precio) / p.precio_anterior) * 100) DESC
        LIMIT %s;
    """

    cursor.execute(query, (min_discount, limit))
    rows = cursor.fetchall()

    deals = []
    for r in rows:
        prev_p = float(r[5])
        curr_p = float(r[4])
        disc = int(round(((prev_p - curr_p) / prev_p) * 100))
        
        deals.append({
            "id": r[0],
            "name": r[1],
            "image_url": r[2],
            "affiliate_url": r[3],
            "current_price": curr_p,
            "previous_price": prev_p,
            "price_per_kg": float(r[6]) if r[6] else None,
            "brand": r[7],
            "store": r[8],
            "discount": disc
        })

    cursor.close()
    conn.close()
    return deals

def mark_as_published(product_id):
    """Marca un producto como publicado en Telegram para no repetir"""
    if not DB_URL:
        return
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET publicado_telegram = TRUE WHERE id = %s;", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("🔍 Buscando chollos en la base de datos...")
    chollos = fetch_best_deals(limit=1, min_discount=10)

    if not chollos:
        print("ℹ️ No se encontraron productos nuevos para publicar con ese descuento.")
    else:
        for chollo in chollos:
            print(f"🎯 Publicando: {chollo['name']} (-{chollo['discount']}%)")
            caption = format_deal_message(chollo)
            success = send_telegram_deal(chollo['image_url'], caption)
            if success:
                mark_as_published(chollo['id'])
                print(f"✅ Producto marcado como publicado en BD.")