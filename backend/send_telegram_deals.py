import os
import sys
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def format_deal_message(product):
    name = product['name']
    brand = product['brand'] or 'Oficial'
    store = product['store'] or 'Tienda oficial'
    current_price = product['current_price']
    previous_price = product['previous_price']
    discount = product['discount']
    price_per_kg = product['price_per_kg']
    affiliate_url = product['affiliate_url']

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
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ CRÍTICO: Variables de entorno de Telegram vacías. Revisa los Secrets del Repositorio.")
        sys.exit(1)
        
    if ":" not in TELEGRAM_BOT_TOKEN:
        print(f"❌ CRÍTICO: El Token inyectado es inválido (no tiene formato de bot): {TELEGRAM_BOT_TOKEN[:4]}...")
        sys.exit(1)

    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "parse_mode": "HTML"}

    try:
        # Intentar con foto
        if photo_url:
            payload["photo"] = photo_url
            payload["caption"] = caption
            res = requests.post(f"{base_url}/sendPhoto", json=payload, timeout=15).json()
            if res.get("ok"):
                print("✅ Chollo publicado (Con foto).")
                return True
            print(f"⚠️ Aviso: Falló la foto ({res.get('description')}). Intentando solo texto...")
        
        # Fallback solo texto
        payload.pop("photo", None)
        payload.pop("caption", None)
        payload["text"] = caption
        
        res = requests.post(f"{base_url}/sendMessage", json=payload, timeout=15).json()
        if res.get("ok"):
            print("✅ Chollo publicado (Solo texto).")
            return True
        else:
            print(f"❌ ERROR TELEGRAM API: {res.get('description')}")
            sys.exit(1) # Forzamos el fallo rojo en GitHub Actions
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE RED: Falló la conexión con Telegram -> {e}")
        sys.exit(1)

def fetch_best_deals(limit=3, min_discount=15):
    if not DB_URL:
        print("❌ CRÍTICO: DATABASE_URL no configurada.")
        sys.exit(1)

    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        query = """
            SELECT p.id, p.nombre, p.imagen_url, p.afiliado_url, p.precio, 
                   p.precio_anterior, p.precio_por_kg, m.nombre AS marca, p.tienda
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
            deals.append({
                "id": r[0], "name": r[1], "image_url": r[2], "affiliate_url": r[3],
                "current_price": float(r[4]), "previous_price": float(r[5]),
                "price_per_kg": float(r[6]) if r[6] else None,
                "brand": r[7], "store": r[8], 
                "discount": int(round(((float(r[5]) - float(r[4])) / float(r[5])) * 100))
            })
        cursor.close()
        conn.close()
        return deals
    except Exception as e:
        print(f"❌ ERROR DE BASE DE DATOS: {e}")
        sys.exit(1)

def mark_as_published(product_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET publicado_telegram = TRUE WHERE id = %s;", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR AL ACTUALIZAR DB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"🔒 AUDITORÍA DE ENTORNO: Token inyectado inicia por '{TELEGRAM_BOT_TOKEN[:4] if TELEGRAM_BOT_TOKEN else 'NULL'}'")
    print("🔍 Buscando chollos pendientes en la base de datos...")
    
    # Valores de producción restaurados
    chollos = fetch_best_deals(limit=3, min_discount=15)

    if not chollos:
        print("ℹ️ Todo al día. No hay nuevos chollos pendientes.")
    else:
        for chollo in chollos:
            print(f"🎯 Evaluando: {chollo['name']} (-{chollo['discount']}%)")
            if send_telegram_deal(chollo['image_url'], format_deal_message(chollo)):
                mark_as_published(chollo['id'])
                print(f"✅ DB actualizada.")