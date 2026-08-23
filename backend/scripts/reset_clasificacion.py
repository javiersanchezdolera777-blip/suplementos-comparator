import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def resetear():
    db = SessionLocal()
    try:
        print("🧹 Borrando formatos y sabores antiguos...")
        db.query(models.Producto).update(
            {models.Producto.sabor: [], models.Producto.formato: None}
        )
        db.commit()
        print("✅ Base de datos reseteada. Lista para la nueva inyección.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    resetear()
