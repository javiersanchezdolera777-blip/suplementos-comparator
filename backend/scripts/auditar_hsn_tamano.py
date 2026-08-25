import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Asegurar que el script puede importar desde el directorio raíz del backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ingestores.utils import extraer_presentacion
except ImportError:
    print("❌ Error: No se pudo importar 'extraer_presentacion'.")
    sys.exit(1)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada en el .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)


def auditar_hsn():
    print("🔍 Iniciando Auditoría Específica para HSN...\n")

    with engine.connect() as conn:
        # 1. Estadísticas generales de HSN
        query_stats = text(
            """
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN presentacion IS NOT NULL THEN 1 ELSE 0 END) as con_pres
            FROM productos 
            WHERE tienda = 'HSN';
        """
        )
        total, con_pres = conn.execute(query_stats).fetchone()
        con_pres = con_pres or 0
        porc = (con_pres / total) * 100 if total > 0 else 0

        print(f"📊 Estado actual en BBDD para HSN:")
        print(f"   ➤ Total de productos HSN: {total}")
        print(f"   ➤ Con presentación: {con_pres} ({porc:.2f}%)")
        print(f"   ➤ Sin presentación (NULL): {total - con_pres}\n")

        # 2. Muestreo de títulos reales de HSN que no tienen presentación
        print("🧪 Analizando títulos reales de HSN sin presentación con el Motor NLP:")
        query_fallos = text(
            """
            SELECT nombre FROM productos 
            WHERE tienda = 'HSN' AND presentacion IS NULL 
            LIMIT 15;
        """
        )
        fallos = conn.execute(query_fallos).fetchall()

        if not fallos:
            print(
                "🎉 ¡Increíble! No hay ningún producto de HSN sin presentación en la BBDD."
            )
            return

        for (nombre,) in fallos:
            res_nlp = extraer_presentacion(nombre)
            print("-" * 60)
            print(f"   ➤ Título HSN: {nombre}")
            if res_nlp:
                print(f"   ✅ El NLP SÍ detecta: '{res_nlp}'")
                print(
                    f"      -> Conclusión: El script 'hsn.py' no lo guardó o el Upsert lo ignoró."
                )
            else:
                print(f"   ⚠️ El NLP NO detecta nada.")
                print(
                    f"      -> Conclusión: El título no tiene el tamaño explícito o la Regex necesita ajustarse."
                )


if __name__ == "__main__":
    auditar_hsn()
