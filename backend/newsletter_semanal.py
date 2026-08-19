import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Fail-Fast: Validación de entorno crítico
if not os.getenv("DATABASE_URL"):
    print("❌ ERROR CRÍTICO: DATABASE_URL no está definida en el entorno. Interrumpiendo ejecución.")
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
        models.Producto.precio_anterior > models.Producto.precio
    )
    
    # 1. Buscar prioritarios: Proteínas o Creatina
    prioritarios = base_query.join(models.Categoria).filter(
        or_(
            models.Categoria.nombre.ilike("%prote%"),
            models.Categoria.nombre.ilike("%creatin%"),
            models.Producto.nombre.ilike("%prote%"),
            models.Producto.nombre.ilike("%creatin%")
        )
    ).order_by((models.Producto.precio_anterior - models.Producto.precio).desc()).limit(3).all()
    
    # Extraer IDs para no repetir
    ids_prioritarios = [p.id for p in prioritarios]
    
    # 2. Buscar el resto para completar los 5
    faltantes = 5 - len(prioritarios)
    resto = []
    if faltantes > 0:
        query_resto = base_query.filter(
            ~models.Producto.id.in_(ids_prioritarios) if ids_prioritarios else True
        ).order_by((models.Producto.precio_anterior - models.Producto.precio).desc()).limit(faltantes)
        resto = query_resto.all()
        
    return prioritarios + resto

def enviar_newsletter_email(chollos):
    # (El token de Resend ya es validado con fail-fast dentro de email_service.py al importar)
        
    db = SessionLocal()
    try:
        suscriptores = db.query(models.SuscripcionNewsletter).filter(models.SuscripcionNewsletter.activo == True).all()
        if not suscriptores:
            print("ℹ️ No hay suscriptores activos para la newsletter.")
            return

        frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")
        
        # Generar HTML
        html_productos = ""
        for prod in chollos:
            html_productos += f"""
            <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #ef4444;">
                <h3 style="margin-top: 0; color: #1e293b; font-size: 16px;">{prod.nombre}</h3>
                <p style="margin: 0; color: #64748b; font-size: 14px;">
                    Precio anterior: <del>{prod.precio_anterior}€</del>
                </p>
                <p style="margin: 4px 0 12px 0; font-size: 18px; font-weight: bold; color: #10b981;">
                    Solo {prod.precio}€
                </p>
                <a href="{frontend_url}/producto/{prod.slug}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">
                    Ver Oferta
                </a>
            </div>
            """

        html_body = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #0f172a;">🔥 Top 5 Chollos de la Semana</h1>
                <p style="color: #64748b;">La mejor selección de ofertas para que ahorres al máximo en tus suplementos.</p>
            </div>
            {html_productos}
            <div style="margin-top: 30px; text-align: center; font-size: 12px; color: #94a3b8;">
                <p>Recibes este correo porque te suscribiste a las alertas de Tus Suplementos.</p>
            </div>
        </div>
        """

        enviados = 0
        for suscripcion in suscriptores:
            if enviar_newsletter_suscripcion(suscripcion.email, html_body):
                enviados += 1
                
        print(f"✅ Newsletter enviada a {enviados}/{len(suscriptores)} suscriptores por email.")
    finally:
        db.close()

def enviar_newsletter_telegram(chollos):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")
    
    if not token or not chat_id:
        print("⚠️ Faltan credenciales de Telegram. Envío al canal omitido.")
        return
        
    mensaje = "🔥 <b>TOP 5 CHOLLOS DE LA SEMANA</b> 🔥\n\n"
    
    medallas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for idx, prod in enumerate(chollos):
        descuento = round(prod.precio_anterior - prod.precio, 2)
        url = f"{frontend_url}/producto/{prod.slug}"
        medalla = medallas[idx] if idx < 5 else f"{idx+1}️⃣"
        
        mensaje += f"{medalla} <b><a href='{url}'>{prod.nombre}</a></b>\n"
        mensaje += f"❌ Antes: <s>{prod.precio_anterior}€</s>\n"
        mensaje += f"✅ Ahora: <b>{prod.precio}€</b> (Ahorras {descuento}€)\n\n"
        
    url_api = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url_api, json=payload)
        if response.status_code == 200:
            print("✅ Top 5 Chollos publicados en el canal de Telegram.")
        else:
            print(f"❌ Error de Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Excepción al conectar con Telegram: {e}")

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
            
        # 1. Enviar por Email
        enviar_newsletter_email(chollos)
        
        # 2. Enviar por Telegram
        enviar_newsletter_telegram(chollos)
        
    except Exception as e:
        print(f"❌ Error crítico en el proceso principal: {e}")
    finally:
        db.close()
        print("🏁 Proceso finalizado. Conexión cerrada.")

if __name__ == "__main__":
    main()
