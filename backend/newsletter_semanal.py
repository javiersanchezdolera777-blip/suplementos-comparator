import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Fail-Fast: Validación de entorno crítico
if not os.getenv("DATABASE_URL"):
    print(
        "❌ ERROR CRÍTICO: DATABASE_URL no está definida en el entorno. Interrumpiendo ejecución."
    )
    sys.exit(1)

# Asegurar path de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from sqlalchemy import or_
from services.email_service import enviar_newsletter_suscripcion


def obtener_top_5_chollos(db):
    # Productos en oferta
    base_query = db.query(models.Producto).filter(
        models.Producto.precio_anterior != None,
        models.Producto.precio_anterior > models.Producto.precio,
    )

    # 1. Buscar prioritarios: Proteínas o Creatina
    prioritarios = (
        base_query.join(models.Categoria)
        .filter(
            or_(
                models.Categoria.nombre.ilike("%prote%"),
                models.Categoria.nombre.ilike("%creatin%"),
                models.Producto.nombre.ilike("%prote%"),
                models.Producto.nombre.ilike("%creatin%"),
            )
        )
        .order_by((models.Producto.precio_anterior - models.Producto.precio).desc())
        .limit(3)
        .all()
    )

    # Extraer IDs para no repetir
    ids_prioritarios = [p.id for p in prioritarios]

    # 2. Buscar el resto para completar los 5
    faltantes = 5 - len(prioritarios)
    resto = []
    if faltantes > 0:
        query_resto = (
            base_query.filter(
                ~models.Producto.id.in_(ids_prioritarios) if ids_prioritarios else True
            )
            .order_by((models.Producto.precio_anterior - models.Producto.precio).desc())
            .limit(faltantes)
        )
        resto = query_resto.all()

    return prioritarios + resto


def enviar_newsletter_email(chollos):
    db = SessionLocal()
    try:
        suscriptores = (
            db.query(models.SuscripcionNewsletter)
            .filter(models.SuscripcionNewsletter.activo == True)
            .all()
        )
        if not suscriptores:
            print("ℹ️ No hay suscriptores activos para la newsletter.")
            return

        frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")

        html_productos = ""
        medallas_html = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for idx, prod in enumerate(chollos):
            medalla = medallas_html[idx] if idx < 5 else f"{idx+1}️⃣"
            ahorro = round(prod.precio_anterior - prod.precio, 2)
            porcentaje = int(
                round(
                    ((prod.precio_anterior - prod.precio) / prod.precio_anterior) * 100
                )
            )

            # Miniatura de la foto del producto (Estilo flexbox limpio)
            img_thumb = (
                f'<img src="{prod.imagen_url}" alt="" style="width: 60px; height: 60px; object-fit: contain; margin-right: 16px; border-radius: 6px; background-color: #ffffff;" />'
                if prod.imagen_url
                else ""
            )

            html_productos += f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; margin-bottom: 16px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; align-items: center; position: relative;">
                <div style="position: absolute; top: -10px; left: -10px; font-size: 24px; background-color: #f8fafc; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; z-index: 10;">
                    {medalla}
                </div>
                {img_thumb}
                <div style="flex-grow: 1; margin-left: 10px;">
                    <div style="display: inline-block; background-color: #fee2e2; color: #ef4444; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">
                        -{porcentaje}% DTO
                    </div>
                    <h3 style="margin-top: 0; color: #0f172a; font-size: 16px; font-weight: 700; line-height: 1.2; margin-bottom: 8px;">{prod.nombre}</h3>
                    <div style="display: flex; align-items: baseline; margin-bottom: 12px;">
                        <span style="font-size: 22px; font-weight: 900; color: #059669; line-height: 1;">{prod.precio:.2f}€</span>
                        <span style="font-size: 13px; color: #94a3b8; text-decoration: line-through; margin-left: 8px;">{prod.precio_anterior:.2f}€</span>
                    </div>
                    <a href="{frontend_url}/producto/{prod.slug}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 13px; text-transform: uppercase;">
                        Ver Oferta
                    </a>
                </div>
            </div>
            """

        html_body = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; line-height: 1.6; background-color: #f8fafc; padding: 24px 24px 40px 24px;">
            <div style="text-align: center; margin-bottom: 32px;">
                <img src="https://www.tussuplementos.com/Logo_icon2.png" alt="Tus Suplementos" width="36" height="36" style="display: block; margin: 0 auto 6px auto; border-radius: 6px;" />
                <h1 style="color: #0f172a; font-size: 26px; font-weight: 900; margin: 12px 0 8px 0; letter-spacing: -1px;">Top 5 Chollos Semanales</h1>
                <p style="color: #64748b; font-size: 15px; margin: 0;">Selección élite de ofertas en nutrición deportiva para maximizar tu ahorro.</p>
            </div>
            
            <div style="margin-top: 24px;">
                {html_productos}
            </div>
            
            <div style="margin-top: 40px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 24px;">
                <p style="font-size: 13px; color: #94a3b8; margin: 0;">
                    Recibes este correo como suscriptor de Tus Suplementos.<br/>
                    <em>Entrena duro, compra inteligente.</em>
                </p>
            </div>
        </div>
        """

        enviados = 0
        for suscripcion in suscriptores:
            if enviar_newsletter_suscripcion(suscripcion.email, html_body):
                enviados += 1

        print(
            f"✅ Newsletter enviada a {enviados}/{len(suscriptores)} suscriptores por email."
        )
    finally:
        db.close()


def enviar_newsletter_telegram(chollos):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")

    if not token or not chat_id:
        print("⚠️ Faltan credenciales de Telegram. Envío al canal omitido.")
        return

    # IMPORTANTE: Telegram tiene un límite de 1024 caracteres para los "captions" (textos debajo de foto).
    # Hemos optimizado el layout para que el Top 5 encaje perfectamente y proteja este límite.
    mensaje = "🏆 <b>TOP 5 CHOLLOS DE LA SEMANA</b> 🏆\n"
    mensaje += "<i>Esta es la selección élite del catálogo:</i>\n\n"

    medallas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

    for idx, prod in enumerate(chollos):
        porcentaje = int(
            round(((prod.precio_anterior - prod.precio) / prod.precio_anterior) * 100)
        )
        url = f"{frontend_url}/producto/{prod.slug}"
        medalla = medallas[idx] if idx < 5 else f"{idx+1}️⃣"
        
        # Recorte de seguridad para nombres extra largos (protección límite 1024 chars)
        nombre_corto = prod.nombre[:65] + "..." if len(prod.nombre) > 65 else prod.nombre

        mensaje += f"{medalla} <b><a href='{url}'>{nombre_corto}</a></b>\n"
        mensaje += f"💰 <s>{prod.precio_anterior:.2f}€</s> ➡️ <b>{prod.precio:.2f}€</b> (-{porcentaje}%)\n\n"

    mensaje += "⚡️ <i>Las ofertas destacadas suelen agotarse rápido.</i>"

    # Inyección Visual: Usamos la imagen del chollo #1 como portada del mensaje
    imagen_portada = chollos[0].imagen_url if chollos[0].imagen_url else "https://www.tussuplementos.com/Logo_icon2.png"

    # Cambiamos el endpoint a sendPhoto en lugar de sendMessage
    url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": imagen_portada,
        "caption": mensaje,
        "parse_mode": "HTML",
    }

    try:
        # PLAN A: Intentar enviar como Foto Nativa (Banner)
        response = requests.post(url_api, json=payload)
        res_data = response.json()

        if response.status_code == 200 and res_data.get("ok"):
            print("✅ Top 5 Chollos publicados en Telegram con IMAGEN nativa.")
        else:
            print(f"⚠️ Aviso: Telegram rechazó la imagen nativa ({res_data.get('description')}). HSN/Cloudflare bloqueó al bot. Ejecutando Plan B...")
            
            # PLAN B: Fallback a mensaje de texto, forzando la previsualización del enlace
            fallback_url = f"https://api.telegram.org/bot{token}/sendMessage"
            fallback_payload = {
                "chat_id": chat_id,
                "text": mensaje,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,  # False obliga a Telegram a extraer la miniatura de la web
            }
            res_fb = requests.post(fallback_url, json=fallback_payload)
            if res_fb.status_code == 200:
                print("✅ Top 5 publicado (Modo texto con previsualización web).")
            else:
                print(f"❌ Error crítico en Fallback de Telegram: {res_fb.text}")
                
    except Exception as e:
        print(f"❌ Excepción de red al conectar con Telegram: {e}")


def main():
    print("🚀 Iniciando generador del Top 5 Chollos Semanal...")
    db = SessionLocal()
    try:
        chollos = obtener_top_5_chollos(db)
        if not chollos:
            print("ℹ️ No hay productos en oferta actualmente. Cancelando newsletter.")
            return

        print(f"📊 Encontrados {len(chollos)} productos para el Top.")
        for c in chollos:
            print(f"  - {c.nombre} (Ahorro: {round(c.precio_anterior - c.precio, 2)}€)")

        # 1. Enviar por Email[cite: 16]
        enviar_newsletter_email(chollos)

        # 2. Enviar por Telegram[cite: 16]
        enviar_newsletter_telegram(chollos)

    except Exception as e:
        print(f"❌ Error crítico en el proceso principal: {e}")
    finally:
        db.close()
        print("🏁 Proceso finalizado. Conexión cerrada.")


if __name__ == "__main__":
    main()
