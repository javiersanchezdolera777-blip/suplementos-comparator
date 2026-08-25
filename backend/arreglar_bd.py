from database import engine
from sqlalchemy import text

print("🔧 Conectando a PostgreSQL para añadir las columnas...")

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE perfiles ADD COLUMN descripcion VARCHAR;"))
        print("✅ Columna 'descripcion' añadida.")
    except Exception as e:
        print("⚠️ La columna 'descripcion' ya existía o hubo un error.")
        conn.rollback() # Limpiamos el error para intentar el siguiente

    try:
        conn.execute(text("ALTER TABLE perfiles ADD COLUMN foto_perfil VARCHAR;"))
        print("✅ Columna 'foto_perfil' añadida.")
    except Exception as e:
        print("⚠️ La columna 'foto_perfil' ya existía o hubo un error.")
        
    conn.commit()

print("🚀 ¡Base de datos actualizada! Ya puedes borrar este archivo.")