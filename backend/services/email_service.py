import os
import sys
import resend

if not os.getenv("RESEND_API_KEY"):
    print(
        "❌ ERROR CRÍTICO: RESEND_API_KEY no está definida en el entorno. Interrumpiendo ejecución."
    )
    sys.exit(1)

resend.api_key = os.getenv("RESEND_API_KEY")


def enviar_email_bienvenida(email: str):
    try:
        r = resend.Emails.send(
            {
                "from": "Tus Suplementos <chollos@tussuplementos.com>",
                "to": email,
                "subject": "¡Bienvenido a Tus Suplementos! 🚀 Tu radar de precios está activo",
                "html": """
            <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; line-height: 1.6; background-color: #ffffff; padding: 32px; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                
                <!-- Encabezado con el Logo de la Web -->
                <div style="text-align: center; margin-bottom: 24px; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px;">
                    <img src="https://www.tussuplementos.com/Logo_icon2.png" alt="Tus Suplementos" width="42" height="42" style="display: block; margin: 0 auto 8px auto; border-radius: 8px;" />
                    <span style="font-size: 16px; font-weight: 900; color: #0f172a; letter-spacing: -0.5px; text-transform: uppercase;">TUS SUPLEMENTOS</span>
                </div>
                
                <h2 style="color: #0f172a; text-align: center; margin-bottom: 16px; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">¡Gracias por registrarte!</h2>
                
                <p style="font-size: 15px; color: #475569; margin-bottom: 16px;">
                    Hola,
                </p>
                
                <p style="font-size: 15px; color: #475569; margin-bottom: 24px;">
                    Te damos la bienvenida a <strong>Tus Suplementos</strong>. A partir de ahora cuentas con un asistente inteligente que rastrea y monitoriza de forma continua los precios del mercado para que nunca pagues de más por tu nutrición y tus objetivos de entrenamiento.
                </p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #0f172a; margin-bottom: 28px;">
                    <h3 style="margin-top: 0; font-size: 15px; color: #0f172a; font-weight: 700;">¿Cómo sacarle el máximo partido?</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 14px; line-height: 1.5;">
                        <li style="margin-bottom: 6px;">Guarda tus productos de interés en tu lista de favoritos.</li>
                        <li style="margin-bottom: 6px;">Nuestro sistema audita las principales tiendas automáticamente cada 6 horas.</li>
                        <li>Recibirás una alerta directa en cuanto se detecte una bajada real de precio.</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 32px; margin-bottom: 36px;">
                    <a href="https://www.tussuplementos.com" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; letter-spacing: 0.5px; text-transform: uppercase;">Explorar Plataforma</a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin-bottom: 24px;" />
                
                <!-- Pie de página corporativo -->
                <div style="text-align: center;">
                    <p style="font-size: 14px; font-weight: 700; color: #0f172a; margin: 0 0 4px 0;">Tus Suplementos</p>
                    <p style="font-size: 12px; color: #64748b; margin: 0 0 12px 0;">
                        El comparador inteligente de precios para nutrición deportiva.
                    </p>
                    <p style="font-size: 12px; color: #94a3b8; margin: 0;">
                        <a href="https://www.tussuplementos.com" style="color: #3b82f6; text-decoration: none;">Visitar sitio web</a> &bull; 
                        <a href="https://www.tussuplementos.com" style="color: #3b82f6; text-decoration: none;">Tus Favoritos</a>
                    </p>
                </div>
                
            </div>
            """,
            }
        )
        print(f"📧 Email de bienvenida enviado al correo")
    except Exception as e:
        print(f"❌ Error enviando email de bienvenida: {e}")


def enviar_alerta_bajada_precio(
    email: str,
    nombre_producto: str,
    precio_viejo: float,
    precio_nuevo: float,
    slug: str,
    imagen_url: str = None,
):
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")
    producto_url = f"{frontend_url}/producto/{slug}"

    ahorro = round(precio_viejo - precio_nuevo, 2)
    porcentaje = int(round(((precio_viejo - precio_nuevo) / precio_viejo) * 100))
    img_tag = (
        f'<div style="text-align: center; margin-bottom: 16px;"><img src="{imagen_url}" alt="{nombre_producto}" style="max-height: 120px; object-fit: contain;" /></div>'
        if imagen_url
        else ""
    )

    try:
        r = resend.Emails.send(
            {
                "from": "Tus Suplementos <chollos@tussuplementos.com>",
                "to": email,
                "subject": f"🔥 ¡Rebaja del {porcentaje}% en {nombre_producto}!",
                "html": f"""
            <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; line-height: 1.6; background-color: #ffffff; padding: 28px; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="text-align: center; margin-bottom: 16px;">
                    <span style="display: inline-block; background-color: #ecfdf5; color: #059669; padding: 4px 14px; border-radius: 999px; font-weight: bold; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">OFERTA DESTACADA</span>
                </div>
                
                {img_tag}
                
                <h2 style="color: #0f172a; text-align: center; margin-bottom: 8px; font-size: 20px; font-weight: 800; line-height: 1.3;">{nombre_producto}</h2>
                <p style="font-size: 15px; color: #475569; text-align: center; margin-bottom: 24px;">El producto que sigues de cerca acaba de registrar una bajada de precio.</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 28px;">
                    <p style="margin: 0; font-size: 14px; color: #64748b; text-transform: uppercase;">Antes: <del style="color: #94a3b8;">{precio_viejo:.2f}€</del></p>
                    <p style="margin: 6px 0; font-size: 32px; font-weight: 900; color: #0f172a; line-height: 1;">{precio_nuevo:.2f}€</p>
                    <p style="margin: 0; font-size: 14px; font-weight: 700; color: #059669; background-color: #d1fae5; display: inline-block; padding: 4px 10px; border-radius: 6px;">¡Ahorras {ahorro:.2f}€ (-{porcentaje}%)!</p>
                </div>
                
                <div style="text-align: center; margin-bottom: 20px;">
                    <a href="{producto_url}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">
                        Ver Oferta en la Web
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
                <div style="text-align: center;">
                    <p style="font-size: 12px; color: #94a3b8; margin: 0;">
                        Tus Suplementos &bull; Monitoreo automático de precios
                    </p>
                </div>
            </div>
            """,
            }
        )
        print(f"📧 Alerta de precio enviada para {nombre_producto}")
    except Exception as e:
        print(f"❌ Error enviando alerta de precio: {e}")


def enviar_resumen_alertas_favoritos(email: str, productos: list):
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")

    html_productos = ""
    ahorro_total = 0
    for prod in productos:
        ahorro = prod["precio_viejo"] - prod["precio_nuevo"]
        ahorro_total += ahorro
        producto_url = f"{frontend_url}/producto/{prod['slug']}"
        img_url = prod.get("imagen_url")
        img_thumb = (
            f'<img src="{img_url}" alt="" style="width: 50px; height: 50px; object-fit: contain; margin-right: 12px; border-radius: 6px;" />'
            if img_url
            else ""
        )

        html_productos += f"""
        <div style="background-color: #ffffff; padding: 16px; border-radius: 10px; margin-bottom: 14px; border: 1px solid #e2e8f0; display: flex; align-items: center;">
            {img_thumb}
            <div style="flex-grow: 1; margin-left: { '0px' if img_url else '0px' };">
                <h4 style="margin: 0 0 6px 0; color: #0f172a; font-size: 15px; font-weight: 700; line-height: 1.2;">{prod['nombre']}</h4>
                <span style="font-size: 13px; color: #64748b; text-decoration: line-through; margin-right: 8px;">{prod['precio_viejo']:.2f}€</span>
                <span style="font-size: 18px; font-weight: 900; color: #0f172a;">{prod['precio_nuevo']:.2f}€</span>
                <span style="font-size: 12px; font-weight: 700; color: #059669; background-color: #d1fae5; padding: 2px 6px; border-radius: 4px; margin-left: 8px;">-{ahorro:.2f}€</span>
            </div>
            <div style="margin-left: 12px;">
                <a href="{producto_url}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 10px 16px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 13px; text-transform: uppercase;">
                    Ver
                </a>
            </div>
        </div>
        """

    try:
        r = resend.Emails.send(
            {
                "from": "Tus Suplementos <chollos@tussuplementos.com>",
                "to": email,
                "subject": f"🔥 ¡Han bajado {len(productos)} favoritos! (Ahorras {ahorro_total:.2f}€)",
                "html": f"""
            <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; line-height: 1.6; background-color: #f8fafc; padding: 24px; border-radius: 12px;">
                <div style="text-align: center; margin-bottom: 24px;">
                    <img src="https://www.tussuplementos.com/Logo_icon2.png" alt="Tus Suplementos" width="36" height="36" style="display: block; margin: 0 auto 6px auto; border-radius: 6px;" />
                    <h2 style="color: #0f172a; font-size: 22px; font-weight: 900; margin-bottom: 6px; letter-spacing: -0.5px;">Tu radar de chollos 🎯</h2>
                    <p style="font-size: 15px; color: #475569; margin: 0;">Hay <strong>{len(productos)} productos</strong> en tu lista de favoritos que acaban de bajar de precio.</p>
                </div>
                
                <div style="margin: 20px 0;">
                    {html_productos}
                </div>
                
                <div style="text-align: center; margin-top: 28px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                    <p style="font-size: 12px; color: #94a3b8; margin: 0;">
                        Recibes este correo porque sigues estos productos en Tus Suplementos.<br/>
                        <a href="{frontend_url}" style="color: #3b82f6; text-decoration: none;">Ir a mis favoritos</a>
                    </p>
                </div>
            </div>
            """,
            }
        )
        print(f"📧 Resumen de {len(productos)} alertas enviado")
    except Exception as e:
        print(f"❌ Error enviando resumen de alertas: {e}")


def enviar_newsletter_suscripcion(email: str, html_body: str):
    try:
        r = resend.Emails.send(
            {
                "from": "Tus Suplementos <chollos@tussuplementos.com>",
                "to": email,
                "subject": "🔥 Los 5 Mejores Chollos de la Semana",
                "html": html_body,
            }
        )
        return True
    except Exception as e:
        print(f"❌ Error al enviar newsletter: {e}")
        return False
