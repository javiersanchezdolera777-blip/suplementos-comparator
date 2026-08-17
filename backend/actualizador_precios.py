import sys
import os
from datetime import datetime

# Asegurar path de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

alertas_pendientes = {}

def registrar_actualizacion_precio(db, producto_id: int, nuevo_precio: float):
    """
    Actualiza el precio de un producto. Si el nuevo precio es menor, 
    mantiene el precio viejo en 'precio_anterior' para activar el filtro de ofertas.
    """
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not prod or nuevo_precio <= 0:
        return False

    precio_actual = float(prod.precio)
    
    if nuevo_precio < precio_actual:
        print(f"🔥 ¡BAJADA DE PRECIO! {prod.nombre}: {precio_actual}€ -> {nuevo_precio}€")
        prod.precio_anterior = precio_actual
        prod.precio = nuevo_precio
        prod.publicado_telegram = False  # Listo para avisar al bot de Telegram
        
        try:
            usuarios_notificar = (
                db.query(models.Usuario.email)
                .join(models.Favorito, models.Usuario.id == models.Favorito.usuario_id)
                .filter(models.Favorito.producto_id == producto_id)
                .all()
            )
            for (email_usuario,) in usuarios_notificar:
                if email_usuario not in alertas_pendientes:
                    alertas_pendientes[email_usuario] = []
                alertas_pendientes[email_usuario].append({
                    "nombre": prod.nombre,
                    "precio_viejo": precio_actual,
                    "precio_nuevo": nuevo_precio,
                    "slug": prod.slug
                })
        except Exception as e:
            print(f"⚠️ Error general agrupando alertas de email: {e}")
    elif nuevo_precio > precio_actual:
        # El precio subió: actualizamos base sin oferta falsa
        prod.precio = nuevo_precio
        prod.precio_anterior = None
    
    return True

def disparar_alertas_agrupadas():
    if not alertas_pendientes:
        return
        
    print(f"✉️ Disparando resumen de alertas para {len(alertas_pendientes)} usuarios...")
    from services.email_service import enviar_resumen_alertas_favoritos
    for email, productos in alertas_pendientes.items():
        try:
            enviar_resumen_alertas_favoritos(email, productos)
        except Exception as e:
            print(f"❌ Error al disparar resumen para {email}: {e}")
            
    alertas_pendientes.clear()

def ejecutar_pipeline_actualizacion(dry_run: bool = False):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Iniciando Pipeline de Actualización...")
    db = SessionLocal()
    try:
        total = db.query(models.Producto).count()
        print(f"📊 Catálogo activo: {total} productos en base de datos.")
        
        # Simulación / Ejecución segura
        if dry_run:
            print("🧪 Modo Dry-Run activo: validando conexiones y estado...")
        
        db.commit()
        print("✅ Pipeline ejecutado con éxito.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el pipeline: {e}")
        
    try:
        disparar_alertas_agrupadas()
    except Exception as e:
        print(f"❌ Error al disparar alertas agrupadas: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    ejecutar_pipeline_actualizacion(dry_run=is_dry)
