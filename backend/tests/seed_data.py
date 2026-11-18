"""Generador determinista de datos sintéticos para pruebas y benchmark de /api/productos.

Cubre a propósito los casos delicados del endpoint:
  - Productos sin ofertas, con una o con varias ofertas (activas e inactivas).
  - Empates de precio y de clics_count (incluidos NULL) para probar desempates.
  - precio_anterior NULL, menor, igual, mayor y 0 (afecta a 'descuento' y 'solo_ofertas').
  - sabor/objetivo como lista, lista vacía, string (coincidencia parcial),
    string doblemente codificado, SQL NULL, JSON null, número, booleano,
    objeto y listas con elementos no-string.
  - Productos sin categoría y/o sin marca, marcas con distinta capitalización.

Nunca se conecta a nada por sí mismo: recibe un engine ya validado como local.
"""
import random
from datetime import datetime, timedelta

from sqlalchemy import text

import models

CATEGORIAS = [
    "Proteínas",
    "Creatinas",
    "Aminoácidos",
    "Pre-Entrenos",
    "Vitaminas y Minerales",
    "Salud y Bienestar",
    "Otros",
]
MARCAS = ["HSN", "MyProtein", "Optimum Nutrition", "NOW Foods", "Desconocida", "Prozis"]
TIENDAS = ["HSN", "Farma2Go", "Sportlive", "Amazon"]
SABORES = [
    "Fresa", "Vainilla", "Chocolate", "Sin sabor", "Limón", "Frutas del bosque",
    "Cookies & Cream", "Plátano", "Café / Capuchino", "Coco", "Caramelo",
    "Avellana", "Cacahuete", "Almendra", "Menta",
]
OBJETIVOS = ["Volumen Muscular", "Pérdida de Peso", "Salud y Bienestar", "Rendimiento Deportivo"]
FORMATOS = ["Polvo", "Cápsulas", "Líquido / Gel", "Barrita", "Gominolas", None]
SELLOS = ["Creapure", "Lacprodan", "Kyowa", "Isolac", "Optipep", "Carnipure", None]
TIPOS_PROTEINA = ["Whey Concentrado", "Isolate (Aislado)", "Hidrolizado", "Caseína", "Vegetal", None]
TIPOS_CREATINA = ["Monohidrato", "HCL", "Kre-Alkalyn", "Micronizada", None]
PERFILES_AMINO = ["BCAA", "EAA", "Glutamina", "Citrulina", "Beta-Alanina", None]
TIPOS_VITAMINA = ["Multivitamínico", "Vitamina C", "Vitamina D", "Magnesio", "Omega-3", None]
NOMBRES_BASE = [
    "Whey Protein", "Proteína Isolate", "Creatina Monohidrato", "Creatine Creapure",
    "BCAA 2:1:1", "EAA Complex", "Pre-Workout Evo", "Omega 3", "Magnesio Bisglicinato",
    "Vitamina D3 K2", "Mantequilla de Cacahuete", "Harina de Avena", "Glutamina Pure",
    "Cafeína 200", "Quemador Termogénico",
]
SQL_NULL = "__SQL_NULL__"
PRECIOS = [4.99, 9.99, 14.99, 19.99, 19.99, 24.99, 29.99, 34.99, 39.99, 49.99, 59.99]


def _variar_mayusculas(rng, s):
    return rng.choice([s, s.lower(), s.upper(), s])


def _valor_json(rng, catalogo):
    """Devuelve un valor heterogéneo para columnas JSON sabor/objetivo."""
    r = rng.random()
    if r < 0.55:
        return [_variar_mayusculas(rng, v) for v in rng.sample(catalogo, rng.randint(1, 3))]
    if r < 0.62:
        return []
    if r < 0.72:
        a, b = rng.sample(catalogo, 2)
        return rng.choice([f"{a} y {b}", f"Sabor {a.lower()}", a.upper(), f"{a}/{b}"])
    if r < 0.76:
        return f'["{rng.choice(catalogo)}"]'  # string doblemente codificado
    if r < 0.82:
        return SQL_NULL  # se convierte en SQL NULL tras el insert
    if r < 0.86:
        return None  # JSON 'null' (comportamiento por defecto de sqlalchemy.JSON)
    if r < 0.89:
        return rng.choice([5, 3.5, True, False])
    if r < 0.92:
        return {"valor": rng.choice(catalogo)}
    return [1, None, rng.choice(catalogo), True]


def seed(engine, n_productos=400, seed_value=1234, max_ofertas=4, historial=True):
    rng = random.Random(seed_value)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.execute(
            text(
                "TRUNCATE precios_historicos, ofertas, productos, categorias, marcas "
                "RESTART IDENTITY CASCADE"
            )
        )

        cat_ids = []
        for nombre in CATEGORIAS:
            cat_ids.append(
                conn.execute(models.Categoria.__table__.insert().values(nombre=nombre).returning(models.Categoria.id)).scalar()
            )
        marca_ids = []
        for nombre in MARCAS:
            marca_ids.append(
                conn.execute(models.Marca.__table__.insert().values(nombre=nombre).returning(models.Marca.id)).scalar()
            )

        productos = []
        for i in range(1, n_productos + 1):
            productos.append(
                {
                    "id": i,
                    "nombre": f"{rng.choice(NOMBRES_BASE)} {rng.choice(MARCAS)} {i}",
                    "descripcion": f"Descripción del producto {i}",
                    "imagen_url": f"https://img.example/{i}.jpg",
                    "slug": f"producto-{i}",
                    "peso_gramos": rng.choice([None, 500, 1000, 2000]),
                    "clics_count": rng.choice([None, 0, 0, 1, 2, 3, 5, 5, 10, 50]),
                    "categoria_id": rng.choice(cat_ids + [None]),
                    "marca_id": rng.choice(marca_ids + [None]),
                    "objetivo": _valor_json(rng, OBJETIVOS),
                    "sabor": _valor_json(rng, SABORES),
                    "formato": rng.choice(FORMATOS),
                    "presentacion": None,
                    "es_vegano": rng.random() < 0.3,
                    "sin_gluten": rng.choice([True, False]),
                    "sin_lactosa": rng.choice([True, False]),
                    "sello_calidad": rng.choice(SELLOS),
                    "tipo_proteina": rng.choice(TIPOS_PROTEINA),
                    "porcentaje_proteina": rng.choice([None, 70, 80, 90]),
                    "tipo_creatina": rng.choice(TIPOS_CREATINA),
                    "perfil_aminoacidos": rng.choice(PERFILES_AMINO),
                    "tipo_vitamina": rng.choice(TIPOS_VITAMINA),
                }
            )
        for lote in range(0, len(productos), 2000):
            conn.execute(models.Producto.__table__.insert(), productos[lote:lote + 2000])
        for col in ("sabor", "objetivo"):
            conn.execute(text(f"UPDATE productos SET {col} = NULL WHERE {col}::text = :s"), {"s": f'"{SQL_NULL}"'})
        conn.execute(text("SELECT setval(pg_get_serial_sequence('productos','id'), :m)"), {"m": n_productos})

        ofertas = []
        oferta_id = 0
        for p in productos:
            for tienda in rng.sample(TIENDAS, rng.randint(0, max_ofertas)):
                oferta_id += 1
                precio = rng.choice(PRECIOS)
                r = rng.random()
                if r < 0.35:
                    anterior = None
                elif r < 0.45:
                    anterior = 0.0
                elif r < 0.55:
                    anterior = precio
                elif r < 0.62:
                    anterior = round(precio * 0.8, 2)
                else:
                    anterior = round(precio / rng.choice([0.9, 0.7, 0.6, 0.5, 0.4]), 2)
                ofertas.append(
                    {
                        "id": oferta_id,
                        "producto_id": p["id"],
                        "tienda": tienda,
                        "precio": precio,
                        "precio_anterior": anterior,
                        "precio_por_kg": rng.choice([None, 15.0, 25.0, 150.0]),
                        "afiliado_url": f"https://shop.example/{tienda}/{p['id']}",
                        "activo": rng.random() < 0.8,
                        "publicado_telegram": False,
                    }
                )
        for lote in range(0, len(ofertas), 5000):
            conn.execute(models.Oferta.__table__.insert(), ofertas[lote:lote + 5000])

        if historial and ofertas:
            base = datetime(2026, 10, 1)
            hist = []
            for o in ofertas:
                for k in range(rng.randint(0, 2)):
                    hist.append(
                        {
                            "oferta_id": o["id"],
                            "precio": o["precio"] + k,
                            "fecha": base - timedelta(days=rng.randint(0, 60)),
                        }
                    )
            for lote in range(0, len(hist), 5000):
                conn.execute(models.HistorialPrecio.__table__.insert(), hist[lote:lote + 5000])
        conn.execute(text("ANALYZE"))
    return {"productos": len(productos), "ofertas": len(ofertas)}
