import sys
import os
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def auditoria_integral():
    db = SessionLocal()
    try:
        productos = db.query(models.Producto).all()

        print("\n" + "=" * 50)
        print("📊 AUDITORÍA INTEGRAL DE CATÁLOGO")
        print("=" * 50)

        # 1. Análisis de Formatos
        formatos = Counter(p.formato for p in productos)
        print("\n📦 FORMATOS DETECTADOS:")
        for f, count in formatos.most_common():
            print(f"  - {f or 'Desconocido'}: {count}")

        # 2. Análisis de Sabores
        sabores_counter = Counter()
        sin_sabor_por_tienda = Counter()

        for p in productos:
            sabores = p.sabor if isinstance(p.sabor, list) else []
            for s in sabores:
                sabores_counter[s] += 1
                if s in ["Sin sabor", "Neutro"]:
                    sin_sabor_por_tienda[p.tienda] += 1

        print("\n👅 RANKING DE SABORES:")
        for s, count in sabores_counter.most_common():
            print(f"  - {s}: {count}")

        # 3. Foco en "Sin Sabor"
        print("\n⚠️ DESGLOSE DE 'SIN SABOR' POR TIENDA:")
        for tienda, count in sin_sabor_por_tienda.most_common():
            print(f"  - {tienda}: {count} productos")

        # 4. Muestra para depuración de HSN (vital para arreglar el JS)
        print("\n🕵️‍♂️ MUESTRA DE HSN 'SIN SABOR' (Para investigar el Regex):")
        hsn_sin_sabor = [
            p for p in productos if p.tienda == "HSN" and "Sin sabor" in (p.sabor or [])
        ]
        for p in hsn_sin_sabor[:5]:
            url_limpia = (
                p.afiliado_url.split("SUPARATOR||")[-1]
                if p.afiliado_url and "SUPARATOR||" in p.afiliado_url
                else "Sin URL"
            )
            print(f"  - {p.nombre}")
            print(f"    URL: {url_limpia}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditoria_integral()
