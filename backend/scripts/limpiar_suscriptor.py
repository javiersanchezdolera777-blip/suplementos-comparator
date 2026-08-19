import sys
import os
from sqlalchemy import text

# Rutas para que reconozca la carpeta backend y cargue el .env
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal

def limpiar_correo_automatico(email_a_borrar: str):
    db = SessionLocal()
    try:
        print("🔌 Conectando a la base de datos para escanear las tablas...")
        
        # 1. Consultamos todas las tablas de la base de datos
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result]
        print(f"📋 Tablas encontradas en la BD: {tables}")
        
        borrado_con_exito = False
        
        # 2. Buscamos en qué tabla existe una columna 'email' para hacer el DELETE seguro
        for table in tables:
            try:
                # Comprobamos las columnas de cada tabla de forma segura
                res = db.execute(text(f"SELECT * FROM {table} LIMIT 0"))
                columns = list(res.keys())
                
                if 'email' in columns:
                    print(f"🎯 ¡Encontrada tabla candidata con columna 'email': '{table}'!")
                    
                    # Intentamos borrar el correo en esta tabla
                    query = text(f"DELETE FROM {table} WHERE email = :email")
                    resultado = db.execute(query, {"email": email_a_borrar})
                    db.commit()
                    
                    if resultado.rowcount > 0:
                        print(f"✅ ¡Éxito! Se ha eliminado el correo '{email_a_borrar}' de la tabla '{table}' ({resultado.rowcount} fila(s) afectada(s)).")
                        borrado_con_exito = True
                    else:
                        print(f"   (El correo no estaba registrado en la tabla '{table}')")
            except Exception as ex:
                db.rollback()
                # Ignoramos tablas del sistema o con restricciones particulares de lectura
                continue
                
        if not borrado_con_exito:
            print("⚠️ No se encontró ningún registro con ese correo en ninguna tabla de la base de datos.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error general en el proceso: {e}")
    finally:
        db.close()
        print("🚪 Conexión cerrada.")

if __name__ == "__main__":
    correo_prueba = "javiersanchezdolera9@gmail.com"
    limpiar_correo_automatico(correo_prueba)