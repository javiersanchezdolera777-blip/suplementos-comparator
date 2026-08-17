import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_email_bienvenida(email: str):
    if not resend.api_key:
        print("⚠️ No hay RESEND_API_KEY. Correo de bienvenida omitido para:", email)
        return
        
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
    if not resend.api_key:
        print(f"⚠️ No hay RESEND_API_KEY. Alerta de precio omitida para {email} sobre {nombre_producto}")
        return
        
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    producto_url = f"{frontend_url}/producto/{slug}"
    
    try:
        r = resend.Emails.send({
            "from": "onboarding@resend.dev",
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
