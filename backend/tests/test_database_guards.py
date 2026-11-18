"""Pruebas unitarias de seguridad para el blindaje de entornos y bases de datos.

Verifica que:
1. Las URLs locales terminadas en _test sean aceptadas.
2. Las URLs remotas, de Neon o no terminadas en _test sean estrictamente rechazadas.
3. El modo de testing exija TEST_DATABASE_URL y nunca use la base de desarrollo por accidente.
4. seed_data.seed() rechace engines remotos y exija ALLOW_DESTRUCTIVE_TEST_DB=true.
5. Los guardias de scripts destructivos impidan operaciones sin los flags de autorización requeridos.
"""
import os
from unittest.mock import MagicMock
import pytest

from security_guards import (
    validate_test_database_url,
    validate_engine_for_testing,
    validate_destructive_script_execution,
    get_active_database_url,
    is_test_environment,
    is_remote_url,
    is_local_host,
)
import seed_data


def test_is_local_host():
    assert is_local_host("localhost") is True
    assert is_local_host("127.0.0.1") is True
    assert is_local_host("::1") is True
    assert is_local_host("") is True
    assert is_local_host("remote.server.com") is False
    assert is_local_host("ep-twilight-base.neon.tech") is False


def test_is_remote_url():
    assert is_remote_url("postgresql://postgres@127.0.0.1:54329/tus_suplementos_test") is False
    assert is_remote_url("postgresql://postgres@localhost:5432/test_db_test") is False
    assert is_remote_url("postgresql://user:pass@ep-fancy-glitter.c-4.neon.tech/neondb") is True
    assert is_remote_url("postgresql://user:pass@db.mycompany.com:5432/app_test") is True


def test_validate_test_database_url_valid():
    # Local y terminado en _test debe pasar sin excepciones
    validate_test_database_url("postgresql://postgres@127.0.0.1:54329/tus_suplementos_test")
    validate_test_database_url("postgresql://postgres@localhost:5432/catalog_test")
    validate_test_database_url("postgresql://user:pass@[::1]:5432/my_app_test")


@pytest.mark.parametrize("invalid_url,reason", [
    ("", "vacío"),
    ("   ", "espacios"),
    ("postgresql://user:pass@ep-fancy-glitter.c-4.eu-central-1.aws.neon.tech/neondb", "Neon remoto"),
    ("postgresql://user:pass@ep-fancy-glitter.c-4.eu-central-1.aws.neon.tech/neondb_test", "Neon con sufijo _test"),
    ("postgresql://user:pass@db.produccion.com:5432/prod_test", "Host remoto"),
    ("postgresql://postgres@127.0.0.1:54329/tus_suplementos_dev", "No termina en _test"),
    ("postgresql://postgres@localhost:5432/neondb", "No termina en _test"),
])
def test_validate_test_database_url_invalid(invalid_url, reason):
    with pytest.raises(RuntimeError):
        validate_test_database_url(invalid_url)


def test_get_active_database_url_requires_test_url_in_test_mode(monkeypatch):
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@remote-neon.tech/neondb")

    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL no está configurado"):
        get_active_database_url()


def test_get_active_database_url_rejects_insecure_test_url_in_test_mode(monkeypatch):
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://user:pass@remote-neon.tech/neondb")

    with pytest.raises(RuntimeError, match="inseguro"):
        get_active_database_url()


def test_get_active_database_url_accepts_valid_test_url(monkeypatch):
    monkeypatch.setenv("TESTING", "1")
    valid_test_url = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    monkeypatch.setenv("TEST_DATABASE_URL", valid_test_url)

    active_url = get_active_database_url()
    assert active_url == valid_test_url


def test_validate_engine_for_testing():
    mock_engine = MagicMock()
    mock_url = MagicMock()
    mock_url.host = "127.0.0.1"
    mock_url.database = "tus_suplementos_test"
    mock_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    mock_engine.url = mock_url

    # Sin chequeo de flag destructivo
    validate_engine_for_testing(mock_engine, check_destructive_flag=False)

    # Con chequeo de flag destructivo sin setear
    os.environ.pop("ALLOW_DESTRUCTIVE_TEST_DB", None)
    with pytest.raises(RuntimeError, match="OPERACIÓN DESTRUCTIVA BLOQUEADA"):
        validate_engine_for_testing(mock_engine, check_destructive_flag=True, flag_name="ALLOW_DESTRUCTIVE_TEST_DB")

    # Con flag seteado a true
    os.environ["ALLOW_DESTRUCTIVE_TEST_DB"] = "true"
    validate_engine_for_testing(mock_engine, check_destructive_flag=True, flag_name="ALLOW_DESTRUCTIVE_TEST_DB")


def test_validate_engine_rejects_remote_or_non_test(monkeypatch):
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_TEST_DB", "true")

    # Caso 1: Host remoto
    remote_engine = MagicMock()
    remote_url = MagicMock()
    remote_url.host = "ep-fancy-glitter.neon.tech"
    remote_url.database = "neondb_test"
    remote_url.__str__.return_value = "postgresql://user:pass@ep-fancy-glitter.neon.tech/neondb_test"
    remote_engine.url = remote_url

    with pytest.raises(RuntimeError, match="host remoto o no autorizado"):
        validate_engine_for_testing(remote_engine, check_destructive_flag=True)

    # Caso 2: Host local pero DB no _test
    prod_local_engine = MagicMock()
    prod_url = MagicMock()
    prod_url.host = "127.0.0.1"
    prod_url.database = "tus_suplementos_prod"
    prod_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_prod"
    prod_engine = MagicMock()
    prod_engine.url = prod_url

    with pytest.raises(RuntimeError, match="no termina en '_test'"):
        validate_engine_for_testing(prod_engine, check_destructive_flag=True)


def test_seed_data_guards(monkeypatch):
    # Si intentan llamar seed(remote_engine), debe explotar antes de ejecutar cualquier SQL
    remote_engine = MagicMock()
    remote_url = MagicMock()
    remote_url.host = "ep-prod.neon.tech"
    remote_url.database = "neondb"
    remote_url.__str__.return_value = "postgresql://user:pass@ep-prod.neon.tech/neondb"
    remote_engine.url = remote_url

    with pytest.raises(RuntimeError):
        seed_data.seed(remote_engine)

    # Si intentan llamar seed(local_test_engine) sin el flag de autorización
    local_engine = MagicMock()
    local_url = MagicMock()
    local_url.host = "127.0.0.1"
    local_url.database = "tus_suplementos_test"
    local_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    local_engine.url = local_url

    monkeypatch.delenv("ALLOW_DESTRUCTIVE_TEST_DB", raising=False)
    with pytest.raises(RuntimeError, match="OPERACIÓN DESTRUCTIVA BLOQUEADA"):
        seed_data.seed(local_engine)


def test_validate_destructive_script_execution(monkeypatch):
    # Script estricto de test (allow_non_test=False)
    local_engine = MagicMock()
    local_url = MagicMock()
    local_url.host = "127.0.0.1"
    local_url.database = "tus_suplementos_test"
    local_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    local_engine.url = local_url

    # Sin flag
    monkeypatch.delenv("ALLOW_DESTRUCTIVE_RESET", raising=False)
    with pytest.raises(RuntimeError, match="OPERACIÓN DESTRUCTIVA BLOQUEADA"):
        validate_destructive_script_execution(
            engine=local_engine,
            script_name="reset_db.py",
            flag_name="ALLOW_DESTRUCTIVE_RESET",
            allow_non_test=False,
        )

    # Con flag
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_RESET", "true")
    validate_destructive_script_execution(
        engine=local_engine,
        script_name="reset_db.py",
        flag_name="ALLOW_DESTRUCTIVE_RESET",
        allow_non_test=False,
    )

    # Script de mantenimiento en base que no es _test (allow_non_test=True)
    dev_engine = MagicMock()
    dev_url = MagicMock()
    dev_url.host = "ep-dev.neon.tech"
    dev_url.database = "neondb"
    dev_url.__str__.return_value = "postgresql://user:pass@ep-dev.neon.tech/neondb"
    dev_engine.url = dev_url

    # Sin flag específico de mantenimiento
    monkeypatch.delenv("ALLOW_MAINTENANCE_OP", raising=False)
    with pytest.raises(RuntimeError, match="EJECUCIÓN BLOQUEADA"):
        validate_destructive_script_execution(
            engine=dev_engine,
            script_name="reprocesar_nlp.py",
            flag_name="ALLOW_MAINTENANCE_OP",
            allow_non_test=True,
        )

    # Con flag específico de mantenimiento
    monkeypatch.setenv("ALLOW_MAINTENANCE_OP", "true")
    validate_destructive_script_execution(
        engine=dev_engine,
        script_name="reprocesar_nlp.py",
        flag_name="ALLOW_MAINTENANCE_OP",
        allow_non_test=True,
    )
