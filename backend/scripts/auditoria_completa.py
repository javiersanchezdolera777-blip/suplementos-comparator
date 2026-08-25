import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada en el .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)


def auditoria_completa():
    print("==================================================")
    print(
        f"🚀 AUDITORÍA DE BBDD: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'LOCAL'}"
    )
    print("==================================================\n")

    with engine.connect() as conn:
        # 1. Total por Tienda
        print("🏪 1. PRODUCTOS POR TIENDA")
        res_tiendas = conn.execute(
            text(
                "SELECT tienda, COUNT(*) FROM productos GROUP BY tienda ORDER BY count DESC;"
            )
        ).fetchall()
        total_general = sum(count for _, count in res_tiendas)
        for tienda, count in res_tiendas:
            print(f"   ➤ {tienda}: {count} productos")
        print(f"   👉 TOTAL GLOBAL: {total_general} productos\n")

        # 2. Categorías Principales
        print("🏷️ 2. CLASIFICACIÓN POR CATEGORÍAS")
        res_cat = conn.execute(
            text(
                """
            SELECT c.nombre, COUNT(p.id) 
            FROM categorias c 
            LEFT JOIN productos p ON c.id = p.categoria_id 
            GROUP BY c.nombre 
            ORDER BY COUNT(p.id) DESC;
        """
            )
        ).fetchall()
        for cat, count in res_cat:
            if count > 0:
                print(f"   ➤ {cat}: {count} productos")
        print()

        # 3. Filtros Dietéticos (Gluten, Lactosa, Vegano)
        print("🥗 3. FILTROS DIETÉTICOS")
        res_diet = conn.execute(
            text(
                """
            SELECT 
                SUM(CASE WHEN sin_gluten = true THEN 1 ELSE 0 END) as gluten,
                SUM(CASE WHEN sin_lactosa = true THEN 1 ELSE 0 END) as lactosa,
                SUM(CASE WHEN es_vegano = true THEN 1 ELSE 0 END) as vegano
            FROM productos;
        """
            )
        ).fetchone()
        print(f"   ➤ Sin Gluten: {res_diet[0]} productos")
        print(f"   ➤ Sin Lactosa: {res_diet[1]} productos")
        print(f"   ➤ 100% Vegano: {res_diet[2]} productos\n")

        # 4. Sellos de Calidad
        print("🏅 4. SELLOS DE CALIDAD")
        res_sellos = conn.execute(
            text(
                "SELECT sello_calidad, COUNT(*) FROM productos WHERE sello_calidad IS NOT NULL GROUP BY sello_calidad ORDER BY count DESC;"
            )
        ).fetchall()
        total_sellos = sum(count for _, count in res_sellos)
        print(f"   ➤ Total con sello: {total_sellos} productos")
        for sello, count in res_sellos:
            print(f"      - {sello}: {count}")
        print()

        # 5. Tamaños y Presentación (Nuevo)
        print("⚖️ 5. PRESENTACIÓN Y TAMAÑOS (Nuevo Feature)")
        try:
            res_pres = conn.execute(
                text(
                    """
                SELECT tienda, COUNT(*) as total, SUM(CASE WHEN presentacion IS NOT NULL THEN 1 ELSE 0 END) as con_pres 
                FROM productos GROUP BY tienda;
            """
                )
            ).fetchall()
            for tienda, total, con_pres in res_pres:
                porc = (con_pres / total) * 100 if total > 0 else 0
                print(f"   ➤ {tienda}: {con_pres}/{total} ({porc:.1f}%)")
        except Exception:
            print("   ⚠️ La columna 'presentacion' no existe en esta Base de Datos aún.")

        print("\n==================================================")
        print("✅ AUDITORÍA FINALIZADA")
        print("==================================================")


if __name__ == "__main__":
    auditoria_completa()
