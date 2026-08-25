import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Asegurar que el script puede importar desde el directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ingestores.utils import extraer_presentacion
except ImportError:
    print("❌ Error: No se pudo importar 'extraer_presentacion'. Verifica la ruta.")
    sys.exit(1)

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada en el .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)


def auditar():
    print("🔍 Iniciando Auditoría Global de Tamaños/Presentaciones...\n")

    with engine.connect() as conn:
        # 1. Estadísticas de relleno para TODAS las tiendas dinámicamente
        query_stats = text(
            """
            SELECT tienda, 
                   COUNT(*) as total, 
                   SUM(CASE WHEN presentacion IS NOT NULL THEN 1 ELSE 0 END) as con_presentacion
            FROM productos 
            GROUP BY tienda
            ORDER BY tienda;
        """
        )

        resultados = conn.execute(query_stats).fetchall()

        total_general = 0
        total_con_presentacion = 0

        for tienda, total, con_pres in resultados:
            total_general += total
            total_con_presentacion += con_pres
            porc = (con_pres / total) * 100 if total > 0 else 0
            nombre_tienda = tienda if tienda else "Desconocida"
            print(
                f"🏪 {nombre_tienda}: {con_pres} de {total} con presentación ({porc:.2f}%)"
            )

        if total_general > 0:
            porc_global = (total_con_presentacion / total_general) * 100
        else:
            porc_global = 0

        print(
            f"\n📊 TOTAL GLOBAL: {total_con_presentacion} / {total_general} ({porc_global:.2f}%)\n"
        )

        # 2. Prueba en vivo de la Regex (Simulacro aleatorio multi-tienda)
        print("🧪 Pasando 15 productos fallidos (al azar) por el Motor NLP local...")

        query_fallos = text(
            """
            SELECT tienda, nombre FROM productos 
            WHERE presentacion IS NULL 
            ORDER BY RANDOM()
            LIMIT 15;
        """
        )
        fallos = conn.execute(query_fallos).fetchall()

        if not fallos:
            print(
                "🎉 ¡Increíble! NO hay ningún producto sin tamaño en toda la base de datos."
            )
            return

        for tienda, nombre in fallos:
            resultado_simulacro = extraer_presentacion(nombre)
            print("-" * 60)
            print(f"🏪 Tienda: {tienda}")
            print(f"   ➤ Título original: {nombre}")
            if resultado_simulacro:
                print(f"   ❌ FALLO DE GUARDADO (La Regex SÍ lo detecta):")
                print(f"      ➤ Extracción exitosa: '{resultado_simulacro}'")
                print(
                    f"      🛑 Conclusión: El scraper o el script de migración no lo guardó."
                )
            else:
                print(f"   ⚠️ FALLO DE REGEX (El NLP no detectó el tamaño):")
                print(
                    f"      🛑 Conclusión: No hay tamaño en el título o la Regex no lo entiende."
                )


if __name__ == "__main__":
    auditar()
