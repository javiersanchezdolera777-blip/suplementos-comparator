import sys
import os

# Agregar la carpeta src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app
from models.product import db

def init_database():
    """Inicializar la base de datos y crear tablas"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas de la base de datos creadas correctamente")
        print("📍 Base de datos: suplementos.db")
        
        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Tablas existentes: {tables}")

if __name__ == '__main__':
    init_database()