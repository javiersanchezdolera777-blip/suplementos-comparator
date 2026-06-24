# consulta1.py
import sys
import os
from sqlalchemy import text  # ← Importa text

# Agrega el directorio src al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

from src.app import create_app
from src import db

def ejecutar_consulta():
    print("🚀 Ejecutando consulta...")
    app = create_app()
    
    with app.app_context():
        # Envuelve la consulta en text() ←
        resultados = db.session.execute(text("SELECT DISTINCT category FROM product;"))
        
        # Imprime los resultados
        print("📋 Categorías encontradas:")
        for categoria in resultados:
            print(f"• {categoria[0]}")  # categoria[0] porque es una tupla

if __name__ == '__main__':
    ejecutar_consulta()