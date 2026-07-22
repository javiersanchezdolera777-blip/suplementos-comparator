from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Por si acaso la columna ya existía mal tipada, la borramos y la creamos bien
    try:
        conn.execute(text("ALTER TABLE productos DROP COLUMN IF EXISTS precio_por_kg;"))
        conn.execute(text("ALTER TABLE productos ADD COLUMN precio_por_kg FLOAT;"))
        conn.commit()
        print("✅ Columna precio_por_kg recreada correctamente en Neon.")
    except Exception as e:
        print(f"Error: {e}")