import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def comprobar_datos():
    db = SessionLocal()
    try:
        total = db.query(models.Producto).count()
        print("\n" + "=" * 50)
        print(f"📦 TOTAL DE PRODUCTOS EN TU NEON (DEV): {total}")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"❌ Error al conectar o leer: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    comprobar_datos()
