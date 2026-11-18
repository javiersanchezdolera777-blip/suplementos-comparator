import sys
import os

# Rutas para que reconozca la carpeta backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BLINDAJE DE SEGURIDAD PRE-IMPORTACIÓN:
# Exige entorno local de test y flag antes de cargar database.py o inicializar SQLAlchemy.
from security_guards import enforce_local_test_environment, validate_destructive_script_execution

enforce_local_test_environment("limpiar_suscriptor.py", "ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR")

from database import SessionLocal, engine
from sqlalchemy import text


def limpiar_correo_automatico(email_a_borrar: str):
    validate_destructive_script_execution(
        engine=engine,
        script_name="limpiar_suscriptor.py",
        flag_name="ALLOW_MAINTENANCE_DELETE_SUSCRIPTOR",
    )
    db = SessionLocal()
    try:
        print("🔌 Conectando a la base de datos local de test para escanear las tablas...")

        # 1. Consultamos todas las tablas de la base de datos
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result]
        print(f"📋 Tablas encontradas en la BD: {tables}")

        borrado_con_exito = False

        # 2. Buscamos en qué tabla existe una columna 'email' para hacer el DELETE seguro
        for table in tables:
            try:
                res = db.execute(text(f"SELECT * FROM {table} LIMIT 0"))
                columns = list(res.keys())

                if 'email' in columns:
                    print(f"🎯 ¡Encontrada tabla candidata con columna 'email': '{table}'!")

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
    correo = sys.argv[1] if len(sys.argv) > 1 else "test_usuario@example.com"
    limpiar_correo_automatico(correo)
