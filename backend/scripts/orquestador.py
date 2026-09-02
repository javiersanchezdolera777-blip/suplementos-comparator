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
    # 1. Capturamos la hora EXACTA en el milisegundo que arranca el script (antes de que HSN consuma tiempo)
    hora_arranque_utc = datetime.now(timezone.utc).hour
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Iniciando Orquestador Maestro...")
    print(f"🕒 Hora de arranque UTC capturada: {hora_arranque_utc}")
    
    # 2. HSN se ejecuta SIEMPRE (4 veces al día)
    try:
        print("\n--- Ejecutando HSN ---")
        inyectar_hsn()
    except Exception as e:
        print(f"❌ Error crítico en ingestor HSN: {e}")

    # 3. Lógica de Bloques Horarios (Ventanas impenetrables de 6 horas)
    # Bloque 1: de 00:00 a 05:59 UTC | Bloque 3: de 12:00 a 17:59 UTC
    if (0 <= hora_arranque_utc < 6) or (12 <= hora_arranque_utc < 18):
        print("🎯 Ventana TradeDoubler activa (Bloque 00h-05h o 12h-17h). Ejecutando Farma2Go y Sportlive...")
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
        print("⏸️ Fuera de la ventana TradeDoubler (Bloque 06h-11h o 18h-23h). Saltando Farma2Go y Sportlive.")

    # 4. Generar alertas después de la ingesta
    db = SessionLocal()
    try:
        generar_alertas(db)
        disparar_alertas_agrupadas()
    finally:
        db.close()
    
    print("\n✅ Orquestador finalizado.")

if __name__ == "__main__":
    ejecutar_orquestador()
