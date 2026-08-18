import sys
import os
from sqlalchemy import text

# Añadimos la ruta del backend para que reconozca database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal

def activar_extensiones():
    print("🔄 Conectando a la base de datos para activar extensiones de PostgreSQL...")
    db = SessionLocal()
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        db.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
        db.commit()
        print("✅ ¡Éxito! Las extensiones 'pg_trgm' y 'unaccent' han sido activadas correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al activar las extensiones: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    activar_extensiones()