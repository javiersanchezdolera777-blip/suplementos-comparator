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
        html_productos += f"""
        <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #3b82f6;">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 16px;">{prod.nombre}</h3>
            <p style="margin: 4px 0 12px 0; font-size: 18px; font-weight: bold; color: #10b981;">
                Por solo {precio}€
            </p>
            <a href="{producto_url}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">
                Volver a ver
            </a>
        </div>
        """

    return f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #0f172a;">¿Sigues pensando en estos suplementos?</h1>
            <p style="color: #64748b;">Notamos que estuviste echando un vistazo a estos productos recientemente. ¡No te quedes sin ellos!</p>
        </div>
        {html_productos}
        <div style="margin-top: 30px; text-align: center; font-size: 12px; color: #94a3b8;">
            <p>Tus Suplementos - El comparador líder.</p>
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
        usuarios_validos = db.query(models.Usuario).join(models.HistorialVistas).filter(
            or_(
                models.Usuario.fecha_ultimo_retargeting == None,
                models.Usuario.fecha_ultimo_retargeting <= limite_spam
            )
        ).distinct().all()
        
        if not usuarios_validos:
            print("ℹ️ Ningún usuario es elegible para retargeting hoy.")
            return
            
        print(f"📊 Evaluando {len(usuarios_validos)} usuarios para retargeting...")
        
        enviados = 0
        for usuario in usuarios_validos:
            # Obtener hasta 3 productos más recientes vistos por este usuario
            vistas = db.query(models.HistorialVistas).filter(
                models.HistorialVistas.usuario_id == usuario.id
            ).order_by(models.HistorialVistas.ultima_vista.desc()).limit(3).all()
            
            if not vistas:
                continue
                
            productos = [vista.producto for vista in vistas if vista.producto]
            if not productos:
                continue
                
            try:
                html_body = generar_html_retargeting(productos, frontend_url)
                resend.Emails.send({
                    "from": "Tus Suplementos <chollos@tussuplementos.com>",
                    "to": usuario.email,
                    "subject": "¿Sigues pensando en estos suplementos?",
                    "html": html_body
                })
                
                # Actualizar control anti-spam si tiene éxito
                usuario.fecha_ultimo_retargeting = ahora
                db.commit()
                enviados += 1
                print(f"📧 Retargeting enviado a {usuario.email}")
            except Exception as e:
                db.rollback() # Hacer rollback por si falló tras modificar
                print(f"❌ Error al enviar retargeting a {usuario.email}: {e}")
                
        print(f"✅ Proceso finalizado. Emails enviados: {enviados}")
    except Exception as e:
        print(f"❌ Error crítico en retargeting: {e}")
    finally:
        db.close()
        print("🏁 Conexión a base de datos cerrada.")

if __name__ == "__main__":
    ejecutar_retargeting()
