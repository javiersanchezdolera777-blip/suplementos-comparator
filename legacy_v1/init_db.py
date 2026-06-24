# init_db.py
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

print(f"📂 Directorio base: {BASE_DIR}")
print(f"📂 Directorio src: {SRC_DIR}")

from src.app import create_app
from src import db  # ← Importar la instancia centralizada

def init_database():
    print("🚀 Iniciando inicialización de la base de datos...")
    app = create_app()
    
    with app.app_context():
        # ❌ Elimina todas las tablas existentes
        db.drop_all()
        print("🗑️ Todas las tablas eliminadas")
        
        # ✅ Crea todas las tablas nuevas
        db.create_all()
        print("✅ Tablas de la base de datos creadas correctamente")
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Tablas existentes: {tables}")


if __name__ == '__main__':
    init_database()