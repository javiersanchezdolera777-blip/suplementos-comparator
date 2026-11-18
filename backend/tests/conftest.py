"""Configuración de pruebas aisladas para /api/productos.

SEGURIDAD: estas pruebas NUNCA usan backend/.env ni la base de datos de
producción. Requieren TEST_DATABASE_URL apuntando a un PostgreSQL local
(localhost / 127.0.0.1 / socket). Si no se define, o apunta a un host remoto,
las pruebas se abortan antes de importar la aplicación.

Ejemplo:
    set TEST_DATABASE_URL=postgresql://postgres@127.0.0.1:54329/tus_suplementos_test
    python -m pytest backend/tests -q
"""
import os
import sys
from urllib.parse import urlparse

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for ruta in (BACKEND_DIR, TESTS_DIR):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

HOSTS_PERMITIDOS = {"localhost", "127.0.0.1", "::1", ""}


def _validar_url_local(url):
    if not url:
        pytest.exit(
            "TEST_DATABASE_URL no definido: las pruebas requieren un PostgreSQL local aislado.",
            returncode=2,
        )
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in HOSTS_PERMITIDOS or "neon" in url.lower():
        pytest.exit(f"TEST_DATABASE_URL debe ser local; host recibido: {host!r}", returncode=2)
    if not parsed.path.strip("/").endswith("_test"):
        pytest.exit("El nombre de la base de datos de pruebas debe terminar en '_test'.", returncode=2)


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")
_validar_url_local(TEST_DATABASE_URL)

# Estas variables se fijan ANTES de importar la app. database.py/security.py usan
# load_dotenv() sin override, así que los valores de backend/.env no las pisan.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests")
os.environ["ENV"] = "local"

import main  # noqa: E402
import seed_data  # noqa: E402
import legacy_productos  # noqa: E402

# Doble comprobación: el engine real de la app apunta al host local.
assert (main.engine.url.host or "") in HOSTS_PERMITIDOS, main.engine.url
assert main.engine.url.database.endswith("_test"), main.engine.url

main.app.include_router(legacy_productos.router)


@pytest.fixture(scope="session")
def dataset():
    return seed_data.seed(main.engine, n_productos=int(os.environ.get("TEST_N_PRODUCTOS", "400")))


@pytest.fixture(scope="session")
def client(dataset):
    from fastapi.testclient import TestClient

    with TestClient(main.app) as c:
        yield c
