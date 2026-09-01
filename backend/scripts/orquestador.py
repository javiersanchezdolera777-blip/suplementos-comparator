import sys
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Asegurar path de importación
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
from ingestores.hsn import inyectar_en_bd as inyectar_hsn
from ingestores.pharma2go import inyectar_en_bd as inyectar_pharma2go
from ingestores.sportlive import inyectar_en_bd as inyectar_sportlive

alertas_pendientes = {}

def disparar_alertas_agrupadas():
    if not alertas_pendientes:
        print("📭 No hay alertas de bajada de precio para enviar.")
        return

    print(f"✉️ Disparando resumen de alertas para {len(alertas_pendientes)} usuarios...")
    try:
        from services.email_service import enviar_resumen_alertas_favoritos

        for email, productos in alertas_pendientes.items():
            try:
                enviar_resumen_alertas_favoritos(email, productos)
            except Exception as e:
                print(f"❌ Error al disparar resumen para {email}: {e}")
    except Exception as e:
        print(f"⚠️ Error importando o usando email_service: {e}")

    alertas_pendientes.clear()


def generar_alertas(db):
    print("🔍 Buscando ofertas con bajada de precio para notificar...")
    try:
        # Buscamos ofertas que se hayan modificado en la última hora y que representen una bajada de precio
        hace_una_hora = datetime.utcnow() - timedelta(hours=1)
        ofertas_rebajadas = db.query(models.Oferta).filter(
            models.Oferta.precio_anterior != None,
            models.Oferta.precio < models.Oferta.precio_anterior,
            models.Oferta.ultima_actualizacion >= hace_una_hora
        ).all()

        for oferta in ofertas_rebajadas:
            prod = oferta.producto
            usuarios_notificar = (
                db.query(models.Usuario.email)
                .join(models.Favorito, models.Usuario.id == models.Favorito.usuario_id)
                .filter(models.Favorito.producto_id == prod.id)
                .all()
            )
            for (email_usuario,) in usuarios_notificar:
                if email_usuario not in alertas_pendientes:
                    alertas_pendientes[email_usuario] = []
                alertas_pendientes[email_usuario].append(
                    {
                        "nombre": prod.nombre,
                        "tienda": oferta.tienda,
                        "precio_viejo": oferta.precio_anterior,
                        "precio_nuevo": oferta.precio,
                        "slug": prod.slug,
                        "imagen_url": prod.imagen_url,
                    }
                )
            
            # Marcamos como no publicado en Telegram para que el bot de Telegram lo recoja luego
            oferta.publicado_telegram = False
        
        db.commit()

    except Exception as e:
        print(f"⚠️ Error al buscar alertas: {e}")


def ejecutar_orquestador():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Iniciando Orquestador Maestro...")
    
    # HSN se ejecuta SIEMPRE
    try:
        print("\n--- Ejecutando HSN ---")
        inyectar_hsn()
    except Exception as e:
        print(f"❌ Error crítico en ingestor HSN: {e}")

    # Evaluar hora UTC para TradeDoubler (Farma2Go y Sportlive)
    hora_actual_utc = datetime.now(timezone.utc).hour
    print(f"\n🕒 Hora actual UTC: {hora_actual_utc}")
    
    if hora_actual_utc in [0, 12]:
        print("🎯 Ventana TradeDoubler activa. Ejecutando Farma2Go y Sportlive...")
        try:
            print("\n--- Ejecutando Farma2Go ---")
            inyectar_pharma2go()
        except Exception as e:
            print(f"❌ Error crítico en ingestor Farma2Go: {e}")

        try:
            print("\n--- Ejecutando Sportlive ---")
            inyectar_sportlive()
        except Exception as e:
            print(f"❌ Error crítico en ingestor Sportlive: {e}")
    else:
        print("⏸️ Fuera de la ventana TradeDoubler (Solo a las 00:xx y 12:xx UTC). Saltando Farma2Go y Sportlive.")

    # Generar alertas después de la ingesta
    db = SessionLocal()
    try:
        generar_alertas(db)
        disparar_alertas_agrupadas()
    finally:
        db.close()
    
    print("\n✅ Orquestador finalizado.")

if __name__ == "__main__":
    ejecutar_orquestador()
