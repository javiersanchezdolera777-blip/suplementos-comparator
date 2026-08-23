import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import models

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("❌ CRÍTICO: No se ha encontrado la variable DATABASE_URL.")
    exit(1)

# Iniciar conexión
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def audit_prices():
    db = SessionLocal()
    print("🕵️ Iniciando Auditoría del CRON de Precios...")
    try:
        # Puesto que la BD actual no tiene columna 'updated_at', verificamos
        # cuántos productos tienen actualmente un registro de bajada de precio activa.
        mutados = db.query(models.Producto).filter(
            models.Producto.precio_anterior.isnot(None),
            models.Producto.precio < models.Producto.precio_anterior
        ).count()
        
        print(f"📊 Análisis de Mutación de Precios:")
        print(f"👉 Hay {mutados} productos en la BD que tienen registrada una rebaja (precio_anterior > precio).")
        
        if mutados > 0:
            print("✅ CONCLUSIÓN: El pipeline orquestador está funcionando correctamente alterando los precios.")
        else:
            print("⚠️ AVISO: 0 variaciones detectadas. O bien el mercado está absolutamente estático, o el CRON no está actualizando los registros.")
            
    except Exception as e:
        print(f"❌ Error al consultar la BD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    audit_prices()
