import sys
import os
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models


def auditar_sabores():
    db = SessionLocal()
    try:
        print("🔍 Escaneando la base de datos en busca de sabores ocultos...\n")
        productos = db.query(models.Producto).all()

        stats = defaultdict(lambda: {"total": 0, "neutro": 0, "sospechosos": []})

        # Diccionario ampliado para pillar a los fugitivos
        palabras_sabor = [
            "chocolate",
            "cacao",
            "brownie",
            "vainilla",
            "fresa",
            "limon",
            "limón",
            "citric",
            "cookie",
            "cream",
            "platano",
            "plátano",
            "banana",
            "cafe",
            "café",
            "capuchino",
            "frutas",
            "berry",
            "frambuesa",
            "cereza",
            "sandía",
            "sandia",
            "manzana",
            "naranja",
            "mango",
            "piña",
            "melocotón",
            "caramelo",
            "caramel",
            "lollipop",
            "piruleta",
            "avellana",
            "almendra",
            "cacahuete",
            "peanut",
            "pistacho",
            "menta",
            "cola",
        ]

        for p in productos:
            tienda = p.tienda or "Desconocida"
            stats[tienda]["total"] += 1

            # Manejar la columna sabor (asumimos que es una lista o string)
            sabores_guardados = p.sabor if p.sabor else []
            es_neutro = False

            # Comprobación segura según cómo lo devuelva SQLAlchemy (lista o string)
            if isinstance(sabores_guardados, list):
                if (
                    "Neutro" in sabores_guardados
                    or "Sin sabor" in sabores_guardados
                    or len(sabores_guardados) == 0
                ):
                    es_neutro = True
            elif isinstance(sabores_guardados, str):
                if (
                    "Neutro" in sabores_guardados
                    or "Sin sabor" in sabores_guardados
                    or sabores_guardados in ["[]", ""]
                ):
                    es_neutro = True

            if es_neutro:
                stats[tienda]["neutro"] += 1

                # Investigar si realmente es "Sin sabor" cruzándolo con nombre y descripción
                texto_completo = f"{p.nombre} {p.descripcion}".lower()
                sabores_ocultos = [s for s in palabras_sabor if s in texto_completo]

                # Excluimos cápsulas y pastillas porque suelen no tener sabor por naturaleza
                formato = (p.formato or "").lower()
                es_pastilla = any(
                    x in formato
                    for x in ["cápsula", "capsula", "comprimido", "perla", "pastilla"]
                )

                if sabores_ocultos and not es_pastilla:
                    # Guardamos hasta 10 ejemplos por tienda para ver el desastre
                    if len(stats[tienda]["sospechosos"]) < 10:
                        stats[tienda]["sospechosos"].append(
                            {"nombre": p.nombre, "ocultos": sabores_ocultos}
                        )

        print("📊 AUDITORÍA DE SABORES POR TIENDA")
        print("-" * 60)
        for tienda, data in stats.items():
            porcentaje = (
                (data["neutro"] / data["total"]) * 100 if data["total"] > 0 else 0
            )
            print(
                f"🏪 {tienda:<10} | {data['neutro']:>4} 'Sin sabor' de {data['total']:>4} productos ({porcentaje:.1f}%)"
            )

            if data["sospechosos"]:
                print(f"   ⚠️ FALSOS 'SIN SABOR' DETECTADOS (Tienen palabras clave):")
                for s in data["sospechosos"]:
                    claves = ", ".join(s["ocultos"])
                    print(f"      - {s['nombre']} [Menciona: {claves}]")
            print("-" * 60)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    auditar_sabores()
