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
    name = product["name"]
    brand = product["brand"] or "Oficial"
    store = product["store"] or brand
    category = product.get("category") or ""
    current_price = product["current_price"]
    previous_price = product["previous_price"]
    discount = product["discount"]
    price_per_kg = product["price_per_kg"]
    affiliate_url = product["affiliate_url"]

    caption = f"⚡ <b>OFERTA DESTACADA</b>\n\n"
    caption += f"📦 <b><a href='{affiliate_url}'>{name}</a></b>\n"
    caption += f"🏷️ Tienda: <b>{store}</b>\n\n"
    caption += f"❌ Antes: <s>{previous_price:.2f}€</s>\n"
    caption += f"💎 <b>Ahora: {current_price:.2f}€</b> <code>(-{discount}%)</code>\n"

    if price_per_kg and price_per_kg > 0:
        palabras_clave = [
            "proteina",
            "creatina",
            "carbohidrato",
            "ganador",
            "mass",
            "gainer",
            "whey",
        ]
        name_lower = name.lower()
        cat_lower = category.lower()
        es_core = any(p in name_lower for p in palabras_clave) or any(
            p in cat_lower for p in palabras_clave
        )

        if es_core and 2 <= price_per_kg <= 100:
            caption += f"📊 Ratio de oro: <code>{price_per_kg:.2f} €/kg</code>\n"

    caption += f"\n🛒 <a href='{affiliate_url}'>Ver oferta en la web</a>"

    return caption


def send_telegram_deal(photo_url, caption, affiliate_url):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(
            "❌ CRÍTICO: Variables de entorno de Telegram vacías. Revisa los Secrets del Repositorio."
        )
        sys.exit(1)

    if ":" not in TELEGRAM_BOT_TOKEN:
        print(
            f"❌ CRÍTICO: El Token inyectado es inválido (no tiene formato de bot): {TELEGRAM_BOT_TOKEN[:4]}..."
        )
        sys.exit(1)

    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    # Botón inline interactivo y visible
    reply_markup = {
        "inline_keyboard": [[{"text": "🛒 Ver oferta en la web", "url": affiliate_url}]]
    }

    try:
        # Intentar con foto
        if photo_url:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": reply_markup,
            }
            res = requests.post(
                f"{base_url}/sendPhoto", json=payload, timeout=15
            ).json()
            if res.get("ok"):
                print("✅ Chollo publicado (Con foto y botón inline).")
                return True
            print(
                f"⚠️ Aviso: Falló la foto ({res.get('description')}). Intentando solo texto..."
            )

        # Fallback solo texto
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": reply_markup,
        }
        res = requests.post(f"{base_url}/sendMessage", json=payload, timeout=15).json()
        if res.get("ok"):
            print("✅ Chollo publicado (Solo texto con botón).")
            return True
        else:
            print(f"❌ ERROR TELEGRAM API: {res.get('description')}")
            sys.exit(1)

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
                   p.precio_anterior, p.precio_por_kg, m.nombre AS marca, p.tienda, c.nombre AS categoria
            FROM productos p
            LEFT JOIN marcas m ON p.marca_id = m.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
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
            deals.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "image_url": r[2],
                    "affiliate_url": r[3],
                    "current_price": float(r[4]),
                    "previous_price": float(r[5]),
                    "price_per_kg": float(r[6]) if r[6] else None,
                    "brand": r[7],
                    "store": r[8],
                    "category": r[9],
                    "discount": int(
                        round(((float(r[5]) - float(r[4])) / float(r[5])) * 100)
                    ),
                }
            )
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
        cursor.execute(
            "UPDATE productos SET publicado_telegram = TRUE WHERE id = %s;",
            (product_id,),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR AL ACTUALIZAR DB: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print(
        f"🔒 AUDITORÍA DE ENTORNO: Token inyectado inicia por '{TELEGRAM_BOT_TOKEN[:4] if TELEGRAM_BOT_TOKEN else 'NULL'}'"
    )
    print("🔍 Buscando chollos pendientes en la base de datos...")

    # Valores de producción restaurados
    chollos = fetch_best_deals(limit=3, min_discount=15)

    if not chollos:
        print("ℹ️ Todo al día. No hay nuevos chollos pendientes.")
    else:
        for chollo in chollos:
            print(f"🎯 Evaluando: {chollo['name']} (-{chollo['discount']}%)")
            if send_telegram_deal(chollo["image_url"], format_deal_message(chollo)):
                mark_as_published(chollo["id"])
                print(f"✅ DB actualizada.")
