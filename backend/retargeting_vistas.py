import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import resend

# Asegurar path de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from sqlalchemy import or_

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")


def generar_html_retargeting(productos, frontend_url):
    html_productos = ""
    for prod in productos:
        producto_url = f"{frontend_url}/producto/{prod.slug}"
        precio = prod.precio if prod.precio else 0.0

        # Miniatura de la foto del producto
        img_thumb = (
            f'<img src="{prod.imagen_url}" alt="" style="width: 60px; height: 60px; object-fit: contain; margin-right: 16px; border-radius: 6px; background-color: #ffffff;" />'
            if getattr(prod, "imagen_url", None)
            else ""
        )

        html_productos += f"""
        <div style="background-color: #ffffff; padding: 16px; border-radius: 10px; margin-bottom: 14px; border: 1px solid #e2e8f0; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            {img_thumb}
            <div style="flex-grow: 1;">
                <h4 style="margin: 0 0 6px 0; color: #0f172a; font-size: 15px; font-weight: 700; line-height: 1.2;">{prod.nombre}</h4>
                <span style="font-size: 18px; font-weight: 900; color: #059669;">{precio:.2f}€</span>
            </div>
            <div style="margin-left: 12px;">
                <a href="{producto_url}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 10px 16px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 13px; text-transform: uppercase;">
                    Volver a ver
                </a>
            </div>
        </div>
        """

    return f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; line-height: 1.6; background-color: #f8fafc; padding: 24px; border-radius: 12px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <img src="https://www.tussuplementos.com/Logo_icon2.png" alt="Tus Suplementos" width="42" height="42" style="display: block; margin: 0 auto 8px auto; border-radius: 8px;" />
            <h2 style="color: #0f172a; font-size: 22px; font-weight: 900; margin-bottom: 6px; letter-spacing: -0.5px;">¿Sigues pensando en estos suplementos?</h2>
            <p style="font-size: 15px; color: #475569; margin: 0;">Notamos que estuviste echando un vistazo a estos productos recientemente. ¡No dejes que se agoten!</p>
        </div>
        <div style="margin: 20px 0;">
            {html_productos}
        </div>
        <div style="text-align: center; margin-top: 28px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
            <p style="font-size: 12px; color: #94a3b8; margin: 0;">
                Tus Suplementos &bull; Tu radar personal de ofertas
            </p>
        </div>
    </div>
    """


def ejecutar_retargeting():
    print("🚀 Iniciando script de retargeting...")

    if not resend.api_key:
        print("⚠️ Faltan credenciales de Resend. Cancelando ejecución.")
        return

    db = SessionLocal()
    frontend_url = os.getenv("FRONTEND_URL", "https://www.tussuplementos.com")
    ahora = datetime.utcnow()
    limite_spam = ahora - timedelta(days=7)

    try:
        # Buscar usuarios con vistas que puedan recibir email (nunca recibieron o hace más de 7 días)
        # Solo necesitamos usuarios únicos
        usuarios_validos = (
            db.query(models.Usuario)
            .join(models.HistorialVistas)
            .filter(
                or_(
                    models.Usuario.fecha_ultimo_retargeting == None,
                    models.Usuario.fecha_ultimo_retargeting <= limite_spam,
                )
            )
            .distinct()
            .all()
        )

        if not usuarios_validos:
            print("ℹ️ Ningún usuario es elegible para retargeting hoy.")
            return

        print(f"📊 Evaluando {len(usuarios_validos)} usuarios para retargeting...")

        enviados = 0
        for usuario in usuarios_validos:
            # Obtener hasta 10 vistas recientes para garantizar que sacamos al menos 3 productos únicos
            vistas = (
                db.query(models.HistorialVistas)
                .filter(models.HistorialVistas.usuario_id == usuario.id)
                .order_by(models.HistorialVistas.ultima_vista.desc())
                .limit(10)
                .all()
            )

            if not vistas:
                continue

            # Filtro inteligente para asegurar productos únicos
            productos_unicos = []
            ids_vistos = set()

            for vista in vistas:
                if vista.producto and vista.producto.id not in ids_vistos:
                    productos_unicos.append(vista.producto)
                    ids_vistos.add(vista.producto.id)
                # Cortar cuando ya tengamos 3 productos diferentes
                if len(productos_unicos) == 3:
                    break

            if not productos_unicos:
                continue

            print(
                f"🔍 DEBUG: Evaluando {len(productos_unicos)} productos únicos para {usuario.email}"
            )
            for p in productos_unicos:
                precio_debug = p.precio if p.precio else "0.0 (None)"
                print(
                    f"   -> Producto: '{p.nombre}' | Precio: {precio_debug} | Slug: '{p.slug}'"
                )
                if not p.nombre or not p.slug:
                    print(
                        "   ⚠️ ADVERTENCIA: Producto con datos críticos (nombre o slug) vacíos o inválidos."
                    )

            try:
                html_body = generar_html_retargeting(productos_unicos, frontend_url)
                print(
                    f"🔍 DEBUG HTML: Generados {len(html_body)} caracteres. ¿Estructura base correcta?: {'Sí' if '<div' in html_body and 'Tus Suplementos' in html_body else 'No'}"
                )

                print("⏳ Enviando petición a la API de Resend...")
                response = resend.Emails.send(
                    {
                        "from": "Tus Suplementos <chollos@tussuplementos.com>",
                        "to": usuario.email,
                        "subject": "¿Sigues pensando en estos suplementos?",
                        "html": html_body,
                    }
                )

                print(f"🔍 DEBUG RESEND RESPONSE: {response}")

                # Actualizar control anti-spam si tiene éxito
                usuario.fecha_ultimo_retargeting = ahora
                db.commit()
                enviados += 1
                print(f"📧 Retargeting procesado y enviado a {usuario.email}")
            except Exception as e:
                db.rollback()  # Hacer rollback por si falló tras modificar
                print(f"❌ Error al enviar retargeting a {usuario.email}: {e}")

        print(f"✅ Proceso finalizado. Emails enviados: {enviados}")
    except Exception as e:
        print(f"❌ Error crítico en retargeting: {e}")
    finally:
        db.close()
        print("🏁 Conexión a base de datos cerrada.")


if __name__ == "__main__":
    ejecutar_retargeting()
