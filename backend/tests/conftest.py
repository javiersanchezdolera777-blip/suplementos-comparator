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

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for ruta in (BACKEND_DIR, TESTS_DIR):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import pytest
from security_guards import validate_test_database_url, validate_engine_for_testing

# Declaramos explícitamente el entorno de testing y la autorización de base de test
os.environ["TESTING"] = "1"
os.environ["ALLOW_DESTRUCTIVE_TEST_DB"] = "true"

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "").strip()
try:
    validate_test_database_url(TEST_DATABASE_URL)
except Exception as exc:
    pytest.exit(f"Abortando ejecución de pruebas por seguridad: {exc}", returncode=2)

# Fijamos DATABASE_URL para garantizar coherencia en todo el proceso
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests")
os.environ["ENV"] = "local"

import main  # noqa: E402
import seed_data  # noqa: E402
import legacy_productos  # noqa: E402

# Doble comprobación: validar que el engine real es estrictamente local de test
validate_engine_for_testing(main.engine, check_destructive_flag=True)

main.app.include_router(legacy_productos.router)


@pytest.fixture(scope="session")
def dataset():
    return seed_data.seed(main.engine, n_productos=int(os.environ.get("TEST_N_PRODUCTOS", "400")))


@pytest.fixture(scope="session")
def client(dataset):
    from fastapi.testclient import TestClient

    with TestClient(main.app) as c:
        yield c
