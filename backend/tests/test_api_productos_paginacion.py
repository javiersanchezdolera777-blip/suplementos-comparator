"""Pruebas de paridad: implementación antigua (oráculo) vs nueva de GET /api/productos.

- /legacy/api/productos -> copia literal de la versión de main@a5cf0a9.
- /api/productos        -> nueva versión con filtrado/deduplicación/paginación en SQL.

Para órdenes totalmente deterministas (relevancia) se exige igualdad exacta del
JSON. Para órdenes por precio/descuento la versión antigua no tenía desempate,
así que dentro de un empate su orden era arbitrario: se exige igualdad de
total, de la secuencia de claves de orden posición a posición, del conjunto de
productos, y de cada producto común byte a byte; además la nueva versión debe
ordenar los empates por id ASC.
"""
import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session, selectinload

import main
import models
import schemas

MAX_LIMIT = 200

ORDENES_PRECIO = {
    "precio_asc": "asc", "price_asc": "asc", "asc": "asc",
    "precio_desc": "desc", "price_desc": "desc", "desc": "desc",
    "descuento": "descuento",
}

# Matriz de escenarios (cubre los 15 casos de aceptación y variantes).
ESCENARIOS = {
    "01_sin_filtros": {},
    "02_categoria": {"categoria": "Proteínas"},
    "02b_categorias_plural": {"categorias": "Creatinas"},
    "02c_categoria_todos": {"categoria": "todos"},
    "03_marca_singular": {"marca": "hsn"},
    "03b_marcas_plural_mayus": {"marcas": "MYPROTEIN"},
    "04_multi_cat_marca": {"categorias": "Proteínas,Creatinas, Aminoácidos", "marcas": "HSN,NOW Foods,Prozis"},
    "05_sabor": {"sabor": "Chocolate"},
    "05b_sabores_multi": {"sabores": "fresa,VAINILLA , menta"},
    "05c_sabor_parcial": {"sabor": "choc"},
    "05d_sabor_acentos": {"sabor": "limón,plátano,café / capuchino"},
    "06_objetivo": {"objetivo": "Volumen Muscular"},
    "06b_objetivos_multi": {"objetivos": "pérdida de peso,salud y bienestar"},
    "06c_objetivo_parcial": {"objetivo": "salud"},
    "07_sabor_y_objetivo": {"sabor": "Chocolate,Fresa", "objetivo": "Rendimiento Deportivo,Volumen Muscular"},
    "08_relevancia_explicita": {"orden": "relevancia"},
    "08b_relevancia_ordenar_por": {"ordenar_por": "relevancia"},
    "08c_relevancia_busqueda": {"busqueda": "proteina hsn"},
    "08d_relevancia_q": {"q": "creatina"},
    "09_precio_asc": {"orden": "precio_asc"},
    "09b_precio_asc_alias": {"orden_precio": "price_asc"},
    "09c_asc_sort": {"sort": "asc"},
    "10_precio_desc": {"orden": "precio_desc"},
    "10b_precio_desc_alias": {"orden_precio": "desc"},
    "11_descuento": {"orden": "descuento"},
    "11b_descuento_orden_precio": {"orden_precio": "descuento"},
    "12_solo_ofertas": {"solo_ofertas": "true"},
    "12b_solo_ofertas_precio_asc": {"solo_ofertas": "true", "orden": "precio_asc"},
    "12c_solo_ofertas_descuento": {"solo_ofertas": "true", "orden_precio": "descuento"},
    "12d_solo_ofertas_busqueda": {"solo_ofertas": "true", "busqueda": "whey"},
    "15a_combo_basicos": {"formato": "Polvo,Cápsulas", "es_vegano": "false", "sin_gluten": "true"},
    "15b_combo_subfiltros": {"categoria": "Proteínas", "tipo_proteina": "whey", "porcentaje_proteina": "80"},
    "15c_combo_sellos": {"sello_calidad": "crea", "sin_lactosa": "true", "orden": "precio_desc"},
    "15d_combo_total": {
        "categorias": "Proteínas,Creatinas,Otros", "sabores": "chocolate,fresa,vainilla",
        "objetivos": "volumen", "orden_precio": "precio_asc",
    },
    "15e_combo_busqueda_sabor": {"q": "bcaa", "sabor": "limón", "orden": "descuento"},
    "15f_combo_aminos_vitas": {"perfil_aminoacidos": "bcaa", "tipo_vitamina": "omega"},
    "15g_sin_resultados": {"categoria": "No Existe"},
}


def _get(client, ruta, params):
    r = client.get(ruta, params=params)
    assert r.status_code == 200, (ruta, params, r.text[:500])
    return r.json()


def _todas_las_paginas(client, ruta, params, limit):
    """Recorre todas las páginas con ?page= y devuelve (total, lista de productos)."""
    primera = _get(client, ruta, {**params, "limit": limit, "page": 1})
    total = primera["total_resultados"]
    productos = list(primera["productos"])
    page = 2
    while len(productos) < total and page <= total + 2:
        datos = _get(client, ruta, {**params, "limit": limit, "page": page})
        assert datos["total_resultados"] == total
        if not datos["productos"]:
            break
        productos.extend(datos["productos"])
        page += 1
    return total, productos


def _sort_final(params):
    return (
        params.get("orden_precio") or params.get("ordenar_por") or params.get("sort")
        or params.get("orden") or "relevancia"
    )


def _cumple_solo_ofertas(oferta, categoria):
    pa, p = oferta.precio_anterior, oferta.precio
    if pa is None or not (pa > p) or not (pa > 0) or categoria is None:
        return False
    pct = ((pa - p) / pa) * 100
    if categoria in ("Proteínas", "Creatinas"):
        return pct >= 30
    if categoria in ("Aminoácidos", "Pre-Entrenos"):
        return pct >= 40
    return pct >= 50


@pytest.fixture(scope="session")
def claves_orden(dataset):
    """Oráculo independiente de la clave de orden por producto (en Python)."""
    with Session(main.engine) as s:
        productos = (
            s.query(models.Producto)
            .options(selectinload(models.Producto.ofertas), selectinload(models.Producto.categoria))
            .all()
        )
        datos = {}
        for p in productos:
            cat = p.categoria.nombre if p.categoria else None
            datos[p.id] = (cat, [(o.precio, o.precio_anterior, o) for o in p.ofertas])

    def clave(pid, modo, solo_ofertas):
        cat, ofertas = datos[pid]
        if solo_ofertas:
            filas = [(pr, pa) for pr, pa, o in ofertas if _cumple_solo_ofertas(o, cat)]
        else:
            filas = [(pr, pa) for pr, pa, _ in ofertas] or [(None, None)]
        precios = [pr for pr, _ in filas if pr is not None]
        if modo == "asc":
            return min(precios) if precios else None
        if modo == "desc":
            return max(precios) if precios else None
        difs = [None if (pa is None or pr is None) else pa - pr for pr, pa in filas]
        return None if any(d is None for d in difs) else max(difs)

    return clave


def _clave_ordenable(valor, modo):
    """Traduce la clave a una tupla comparable con la colocación de NULLs de PostgreSQL."""
    if modo == "asc":  # ASC NULLS LAST
        return (1, 0) if valor is None else (0, valor)
    return (0, 0) if valor is None else (1, -valor)  # DESC NULLS FIRST


# ---------------------------------------------------------------------------
# 1) Paridad antigua vs nueva en todos los escenarios
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("nombre", sorted(ESCENARIOS))
def test_paridad_con_implementacion_antigua(client, claves_orden, nombre):
    params = ESCENARIOS[nombre]
    total_old, old = _todas_las_paginas(client, "/legacy/api/productos", params, MAX_LIMIT)
    total_new, new = _todas_las_paginas(client, "/api/productos", params, MAX_LIMIT)

    ids_new = [p["id"] for p in new]
    ids_old = [p["id"] for p in old]
    assert total_new == total_old
    assert len(ids_new) == len(set(ids_new)) == total_new, "duplicados o pérdidas en la versión nueva"
    assert set(ids_new) == set(ids_old)

    modo = ORDENES_PRECIO.get(_sort_final(params))
    if modo is None:
        # Orden determinista en ambas versiones: igualdad exacta del JSON completo.
        assert new == old
        return

    solo = str(params.get("solo_ofertas", "")).lower() == "true"
    claves_new = [claves_orden(i, modo, solo) for i in ids_new]
    claves_old = [claves_orden(i, modo, solo) for i in ids_old]
    assert claves_new == claves_old, "la secuencia de claves de orden difiere"
    # La nueva versión ordena exactamente por (clave, id) => desempate estable.
    esperado = sorted(ids_new, key=lambda i: (_clave_ordenable(claves_orden(i, modo, solo), modo), i))
    assert ids_new == esperado
    por_id_old = {p["id"]: p for p in old}
    for p in new:
        assert p == por_id_old[p["id"]]


# ---------------------------------------------------------------------------
# 2) Paginación: page / skip, sin duplicados ni huecos
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("nombre", ["01_sin_filtros", "09_precio_asc", "10_precio_desc", "11_descuento",
                                    "12_solo_ofertas", "15d_combo_total", "08c_relevancia_busqueda"])
@pytest.mark.parametrize("limit", [7, 36])
def test_paginacion_page_y_skip_consistentes(client, nombre, limit):
    params = ESCENARIOS[nombre]
    completo = _get(client, "/api/productos", {**params, "limit": MAX_LIMIT})
    total = completo["total_resultados"]
    referencia = [p["id"] for p in _todas_las_paginas(client, "/api/productos", params, MAX_LIMIT)[1]]

    por_page = [p["id"] for p in _todas_las_paginas(client, "/api/productos", params, limit)[1]]
    assert por_page == referencia
    assert len(por_page) == len(set(por_page)) == total

    por_skip = []
    skip = 0
    while True:
        if skip == 0:
            # skip=0 => se ignora y se usa page (comportamiento heredado)
            datos = _get(client, "/api/productos", {**params, "limit": limit, "skip": 0, "page": 1})
        else:
            # skip > 0 tiene prioridad sobre page (compatibilidad con el parámetro antiguo)
            datos = _get(client, "/api/productos", {**params, "limit": limit, "skip": skip, "page": 99})
        assert datos["total_resultados"] == total
        if not datos["productos"]:
            break
        por_skip.extend(p["id"] for p in datos["productos"])
        skip += limit
    assert por_skip == referencia


@pytest.mark.parametrize(
    "extra",
    [
        {"limit": 0},
        {"limit": -3},
        {"limit": -3, "page": 2},
        {"limit": 5, "page": 10_000},
        {"limit": 5, "skip": 10_000},
        {"limit": 5, "skip": -4, "page": 3},
        {"limit": 5, "skip": 3},
        {"limit": 1, "page": 2},
    ],
)
@pytest.mark.parametrize("nombre", ["01_sin_filtros", "09_precio_asc", "05_sabor"])
def test_paginacion_valores_limite_igual_que_antes(client, claves_orden, nombre, extra):
    params = {**ESCENARIOS[nombre], **extra}
    old = _get(client, "/legacy/api/productos", params)
    new = _get(client, "/api/productos", params)
    assert new["total_resultados"] == old["total_resultados"]
    assert len(new["productos"]) == len(old["productos"])
    modo = ORDENES_PRECIO.get(_sort_final(params))
    if modo is None:
        assert new == old
    else:
        assert [claves_orden(p["id"], modo, False) for p in new["productos"]] == [
            claves_orden(p["id"], modo, False) for p in old["productos"]
        ]


def test_limite_maximo_se_conserva(client):
    assert client.get("/api/productos", params={"limit": 201}).status_code == 422
    assert client.get("/api/productos", params={"page": 0}).status_code == 422
    assert client.get("/api/productos", params={"limit": 200}).status_code == 200


# ---------------------------------------------------------------------------
# 3) Esquema de respuesta esperado por el frontend
# ---------------------------------------------------------------------------
def test_esquema_respuesta(client):
    datos = _get(client, "/api/productos", {"limit": 36, "page": 1})
    assert set(datos) == {"total_resultados", "productos"}
    assert isinstance(datos["total_resultados"], int)
    assert len(datos["productos"]) == 36
    campos = set(schemas.ProductResponse.model_fields)
    for p in datos["productos"]:
        assert set(p) == campos
        schemas.ProductResponse.model_validate(p)


# ---------------------------------------------------------------------------
# 4) Filtros JSON: comprobación directa contra la regla Python original
# ---------------------------------------------------------------------------
def _regla_python(valor, lista):
    if isinstance(valor, list):
        return any(str(item).lower() in lista for item in valor)
    if isinstance(valor, str):
        return any(s in valor.lower() for s in lista)
    return False


@pytest.mark.parametrize(
    "campo,param,valores",
    [
        ("sabor", "sabores", ["chocolate"]),
        ("sabor", "sabores", ["fresa", "menta", "coco"]),
        ("sabor", "sabores", ["choc", "ran"]),
        ("sabor", "sabores", ["café / capuchino", "limón"]),
        ("sabor", "sabores", ["5", "true", "none"]),
        ("objetivo", "objetivos", ["volumen muscular"]),
        ("objetivo", "objetivos", ["salud", "peso"]),
        ("objetivo", "objetivos", ["rendimiento deportivo", "pérdida de peso"]),
    ],
)
def test_filtro_json_equivale_a_regla_python(client, dataset, campo, param, valores):
    with Session(main.engine) as s:
        filas = s.query(models.Producto.id, getattr(models.Producto, campo)).all()
    esperados = {pid for pid, v in filas if _regla_python(v, valores)}
    _, productos = _todas_las_paginas(client, "/api/productos", {param: ",".join(valores)}, MAX_LIMIT)
    assert {p["id"] for p in productos} == esperados


def test_dataset_cubre_tipos_json(dataset):
    """Garantiza que el seed contiene todos los formatos JSON delicados."""
    from sqlalchemy import text

    with main.engine.connect() as conn:
        tipos = {
            r[0] for r in conn.execute(text("SELECT DISTINCT COALESCE(json_typeof(sabor), 'SQL NULL') FROM productos"))
        }
    assert {"array", "string", "null", "number", "boolean", "object", "SQL NULL"} <= tipos


# ---------------------------------------------------------------------------
# 5) Carga en memoria: la nueva versión no trae filas intermedias masivas
# ---------------------------------------------------------------------------
class _ContadorSQL:
    def __init__(self, engine):
        self.engine = engine
        self.sentencias = []

    def _after(self, conn, cursor, statement, parameters, context, executemany):
        self.sentencias.append((statement, cursor.rowcount))

    def __enter__(self):
        event.listen(self.engine, "after_cursor_execute", self._after)
        return self

    def __exit__(self, *exc):
        event.remove(self.engine, "after_cursor_execute", self._after)


@pytest.mark.parametrize("params", [{}, {"orden": "precio_asc"}, {"sabor": "chocolate", "orden": "descuento"}])
def test_no_materializa_resultados_intermedios(client, params):
    limit = 10
    with _ContadorSQL(main.engine) as nuevo:
        datos = _get(client, "/api/productos", {**params, "limit": limit, "page": 3})
    total = datos["total_resultados"]
    assert total > 3 * limit
    principales = [
        (sql, n) for sql, n in nuevo.sentencias
        if "FROM ofertas" not in sql and "FROM precios_historicos" not in sql
        and "FROM marcas" not in sql and "FROM categorias" not in sql
    ]
    # count(*) devuelve 1 fila; la query de IDs y la de objetos, como mucho `limit`.
    assert all(n <= limit for _, n in principales), principales

    with _ContadorSQL(main.engine) as antiguo:
        _get(client, "/legacy/api/productos", {**params, "limit": limit, "page": 3})
    assert max(n for _, n in antiguo.sentencias) >= total  # la versión antigua sí materializaba
