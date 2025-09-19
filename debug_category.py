# find_database.py
import os
import sqlite3
from pathlib import Path

def find_and_check_database():
    # Buscar archivos .db en el proyecto
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    
    print("=== ARCHIVOS DE BASE DE DATOS ENCONTRADOS ===")
    for db_file in db_files:
        print(f"📁 {db_file}")
        
        # Verificar si tiene la tabla product
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"  Tablas en {db_file}: {[table[0] for table in tables]}")
            
            # Verificar si existe la tabla product
            if any('product' in table[0].lower() for table in tables):
                print(f"  ✅ Contiene tabla de productos")
                # Mostrar estructura
                cursor.execute("PRAGMA table_info(product)")
                columns = cursor.fetchall()
                print(f"  Estructura: {[col[1] for col in columns]}")
            else:
                print(f"  ❌ No contiene tabla de productos")
                
            conn.close()
            print()
            
        except sqlite3.Error as e:
            print(f"  Error al conectar: {e}")
            print()

if __name__ == '__main__':
    find_and_check_database()