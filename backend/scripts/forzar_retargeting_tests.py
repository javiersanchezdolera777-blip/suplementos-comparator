import os
import sys
from dotenv import load_dotenv
import psycopg2

# Cargar entorno local
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("❌ ERROR: DATABASE_URL no encontrada en el .env")
    sys.exit(1)


def resetear_y_crear_vistas_prueba():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        # 1. Obtener tu ID de usuario (o el primero que encuentre)
        cursor.execute("SELECT id, email FROM usuarios LIMIT 1;")
        user = cursor.fetchone()
        if not user:
            print("❌ No se encontraron usuarios en la base de datos.")
            return

        user_id, email = user
        print(f"👤 Usuario de pruebas detectado: {email} (ID: {user_id})")

        # 2. Resetear la fecha de retargeting para saltarse el filtro de 7 días
        cursor.execute(
            "UPDATE usuarios SET fecha_ultimo_retargeting = NULL WHERE id = %s;",
            (user_id,),
        )

        # 3. Asegurar que tienes al menos una vista reciente en 'historial_vistas'
        cursor.execute("SELECT id FROM productos LIMIT 2;")
        productos = cursor.fetchall()

        if productos:
            for p in productos:
                prod_id = p[0]
                # Insertar o actualizar vista reciente
                cursor.execute(
                    """
                    INSERT INTO historial_vistas (usuario_id, producto_id, ultima_vista)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT DO NOTHING;
                """,
                    (user_id, prod_id),
                )

        conn.commit()
        cursor.close()
        conn.close()
        print(
            "✅ ¡Listo! Tu usuario ya es elegible para el retargeting. Ya puedes lanzar el script o la Action."
        )

    except Exception as e:
        print(f"❌ Error al preparar el test de retargeting: {e}")


if __name__ == "__main__":
    resetear_y_crear_vistas_prueba()
