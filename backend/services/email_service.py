import os
import sys
import resend

if not os.getenv("RESEND_API_KEY"):
    print("❌ ERROR CRÍTICO: RESEND_API_KEY no está definida en el entorno. Interrumpiendo ejecución.")
    sys.exit(1)

resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_email_bienvenida(email: str):
        
    try:
        r = resend.Emails.send({
            "from": "Alertas Tus Suplementos <chollos@tussuplementos.com>",
            "to": email,
            "subject": "¡Bienvenido a Tus Suplementos! 🎉",
            "html": """
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                <h2 style="color: #0f172a;">¡Bienvenido a la comunidad de chollos!</h2>
                <p>Hola,</p>
                <p>Gracias por suscribirte a la newsletter de <strong>Tus Suplementos</strong>.</p>
                <p>A partir de ahora, serás el primero en enterarte de las mejores ofertas y bajadas de precio en tus suplementos favoritos.</p>
                <p>¡Prepárate para ahorrar!</p>
                <br/>
                <p>El equipo de Tus Suplementos.</p>
            </div>
            """
        })
        print(f"📧 Email de bienvenida enviado a {email}")
    except Exception as e:
        print(f"❌ Error enviando email de bienvenida a {email}: {e}")

def enviar_alerta_bajada_precio(email: str, nombre_producto: str, precio_viejo: float, precio_nuevo: float, slug: str):
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")
    producto_url = f"{frontend_url}/producto/{slug}"
    
    try:
        r = resend.Emails.send({
            "from": "Alertas Tus Suplementos <chollos@tussuplementos.com>",
            "to": email,
            "subject": f"🔥 ¡Bajada de precio! {nombre_producto}",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                <h2 style="color: #ef4444;">¡Uno de tus favoritos ha bajado de precio!</h2>
                <p>El producto <strong>{nombre_producto}</strong> que tienes guardado en tus favoritos acaba de recibir un descuento.</p>
                <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                    <p style="margin: 0; font-size: 16px;">Precio anterior: <del style="color: #94a3b8;">{precio_viejo}€</del></p>
                    <p style="margin: 8px 0 0 0; font-size: 20px; font-weight: bold; color: #10b981;">Nuevo precio: {precio_nuevo}€</p>
                </div>
                <p>
                    <a href="{producto_url}" style="display: inline-block; background-color: #1e293b; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        Ver oferta ahora
                    </a>
                </p>
            </div>
            """
        })
        print(f"📧 Alerta de precio enviada a {email} para {nombre_producto}")
    except Exception as e:
        print(f"❌ Error enviando alerta de precio a {email}: {e}")

def enviar_resumen_alertas_favoritos(email: str, productos: list):
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")
    
    html_productos = ""
    for prod in productos:
        producto_url = f"{frontend_url}/producto/{prod['slug']}"
        html_productos += f"""
        <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #3b82f6;">
            <h3 style="margin-top: 0; color: #1e293b;">{prod['nombre']}</h3>
            <p style="margin: 0; font-size: 14px;">Precio anterior: <del style="color: #94a3b8;">{prod['precio_viejo']}€</del></p>
            <p style="margin: 4px 0 12px 0; font-size: 18px; font-weight: bold; color: #10b981;">Nuevo precio: {prod['precio_nuevo']}€</p>
            <a href="{producto_url}" style="display: inline-block; background-color: #1e293b; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">
                Ver oferta
            </a>
        </div>
        """
        
    try:
        r = resend.Emails.send({
            "from": "Alertas Tus Suplementos <chollos@tussuplementos.com>",
            "to": email,
            "subject": f"🔥 ¡Han bajado de precio {len(productos)} de tus favoritos!",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                <h2 style="color: #ef4444;">¡Tenemos buenas noticias!</h2>
                <p>Algunos productos que tienes guardados en tus favoritos acaban de recibir un descuento.</p>
                <div style="margin: 20px 0;">
                    {html_productos}
                </div>
                <p style="font-size: 12px; color: #64748b; margin-top: 30px;">
                    Has recibido este correo porque tienes estos productos en tu lista de favoritos.
                </p>
            </div>
            """
        })
        print(f"📧 Resumen de {len(productos)} alertas enviado a {email}")
    except Exception as e:
        print(f"❌ Error enviando resumen de alertas a {email}: {e}")

def enviar_newsletter_suscripcion(email: str, html_body: str):
    """
    Envía el correo de newsletter a un único suscriptor.
    La lógica de iteración de suscriptores y construcción del cuerpo
    se mantiene en el cron script para separar responsabilidades.
    """
    try:
        r = resend.Emails.send({
            "from": "Tus Suplementos <chollos@tussuplementos.com>",
            "to": email,
            "subject": "🔥 Los 5 Mejores Chollos de la Semana",
            "html": html_body
        })
        return True
    except Exception as e:
        print(f"❌ Error al enviar newsletter a {email}: {e}")
        return False
