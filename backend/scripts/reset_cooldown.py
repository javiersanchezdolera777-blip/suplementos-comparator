import sys
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models


def resetear_ofertas_antiguas():
    print("🔄 Comprobando chollos antiguos en Telegram (Cooldown de 7 días)...")
    db = SessionLocal()
    try:
        hace_7_dias = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            days=7
        )

        # 🚨 CAMBIO: Ahora buscamos ofertas caducadas, no productos
        ofertas_caducadas = (
            db.query(models.Oferta)
            .filter(
                models.Oferta.publicado_telegram == True,
                models.Oferta.fecha_publicacion_telegram != None,
                models.Oferta.fecha_publicacion_telegram < hace_7_dias,
            )
            .all()
        )

        if not ofertas_caducadas:
            print("ℹ️ No hay ofertas que necesiten reseteo hoy.")
            return

        for oferta in ofertas_caducadas:
            oferta.publicado_telegram = False
            oferta.fecha_publicacion_telegram = None  # Limpiamos la fecha

        db.commit()
        print(
            f"✅ ¡Reseteo completado! {len(ofertas_caducadas)} ofertas han vuelto al circuito del bot."
        )

    except Exception as e:
        db.rollback()
        print(f"❌ Error al resetear el cooldown: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    resetear_ofertas_antiguas()
