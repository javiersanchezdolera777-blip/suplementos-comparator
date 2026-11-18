"""Pruebas unitarias de seguridad para el blindaje de entornos y bases de datos.

Verifica que:
1. Las URLs locales terminadas en _test sean aceptadas.
2. Las URLs remotas, de Neon o no terminadas en _test sean estrictamente rechazadas.
3. Se rechacen esquemas no PostgreSQL (como SQLite).
4. Se rechacen URLs PostgreSQL sin hostname explícito.
5. Se rechacen parámetros de query que alteren el host (host, hostaddr, service).
6. Se rechace cualquier engine cuyo dialecto no sea PostgreSQL o tenga parámetros de query sospechosos.
7. El modo de testing exija TEST_DATABASE_URL y nunca use la base de desarrollo por accidente.
8. seed_data.seed() rechace engines remotos y exija ALLOW_DESTRUCTIVE_TEST_DB=true.
9. enforce_local_test_environment() bloquee Neon dev, Neon prod o hosts remotos antes de cualquier importación.
10. ping_bd.py seleccione destinos de forma unívoca y no ejecute DDL.
11. database.py no contenga CREATE EXTENSION en su inicialización.
"""
import os
import sys
from unittest.mock import MagicMock
import pytest

from security_guards import (
    validate_test_database_url,
    validate_engine_for_testing,
    validate_destructive_script_execution,
    enforce_local_test_environment,
    get_active_database_url,
    is_test_environment,
    is_remote_url,
    is_local_host,
)
import seed_data
from scripts.ping_bd import select_target_url, create_parser


def test_is_local_host():
    assert is_local_host("localhost") is True
    assert is_local_host("127.0.0.1") is True
    assert is_local_host("::1") is True
    assert is_local_host("") is False
    assert is_local_host(None) is False
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
    validate_test_database_url("postgresql+psycopg2://postgres@localhost:5432/catalog_test")
    validate_test_database_url("postgresql://user:pass@[::1]:5432/my_app_test")


@pytest.mark.parametrize("invalid_url,reason", [
    ("", "vacío"),
    ("   ", "espacios"),
    ("postgresql://user:pass@ep-fancy-glitter.c-4.eu-central-1.aws.neon.tech/neondb", "Neon remoto"),
    ("postgresql://user:pass@ep-fancy-glitter.c-4.eu-central-1.aws.neon.tech/neondb_test", "Neon con sufijo _test"),
    ("postgresql://user:pass@ep-twilight-base-ass5vshw-pooler.c-4.eu-central-1.aws.neon.tech/neondb", "Neon dev"),
    ("postgresql://user:pass@db.produccion.com:5432/prod_test", "Host remoto"),
    ("postgresql://postgres@127.0.0.1:54329/tus_suplementos_dev", "No termina en _test"),
    ("postgresql://postgres@localhost:5432/neondb", "No termina en _test"),
    ("sqlite:///tus_suplementos_test.db", "SQLite no permitido"),
    ("sqlite:///:memory:_test", "SQLite en memoria no permitido"),
    ("mysql://root@127.0.0.1:3306/db_test", "MySQL no permitido"),
    ("postgresql.evil://127.0.0.1:54329/tus_suplementos_test", "Esquema postgresql.evil no permitido"),
    ("postgresql_fake://127.0.0.1:54329/tus_suplementos_test", "Esquema postgresql_fake no permitido"),
    ("postgresql+://127.0.0.1:54329/tus_suplementos_test", "Esquema postgresql+ sin driver no permitido"),
    ("postgresql:///tus_suplementos_test", "Sin hostname explícito"),
    ("postgresql://@localhost:5432/my_test?host=remote.com", "Host remoto en query"),
    ("postgresql://postgres@127.0.0.1:5432/my_test?hostaddr=10.0.0.1", "Hostaddr en query"),
    ("postgresql://postgres@127.0.0.1:5432/my_test?service=remotesvc", "Service en query"),
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
    mock_engine.dialect.name = "postgresql"
    mock_url = MagicMock()
    mock_url.host = "127.0.0.1"
    mock_url.database = "tus_suplementos_test"
    mock_url.query = {}
    mock_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    mock_engine.url = mock_url

    # Sin chequeo de flag destructivo
    validate_engine_for_testing(mock_engine, check_destructive_flag=False)

    # Con chequeo de flag destructivo sin setear
    os.environ.pop("ALLOW_DESTRUCTIVE_TEST_DB", None)
    with pytest.raises(RuntimeError, match="OPERACIÓN BLOQUEADA"):
        validate_engine_for_testing(mock_engine, check_destructive_flag=True, flag_name="ALLOW_DESTRUCTIVE_TEST_DB")

    # Con flag seteado a true
    os.environ["ALLOW_DESTRUCTIVE_TEST_DB"] = "true"
    validate_engine_for_testing(mock_engine, check_destructive_flag=True, flag_name="ALLOW_DESTRUCTIVE_TEST_DB")


def test_validate_engine_rejects_non_postgresql_dialect():
    mock_engine = MagicMock()
    mock_engine.dialect.name = "sqlite"
    mock_url = MagicMock()
    mock_url.host = "127.0.0.1"
    mock_url.database = "my_test"
    mock_url.query = {}
    mock_engine.url = mock_url

    with pytest.raises(RuntimeError, match="Dialecto del motor no autorizado"):
        validate_engine_for_testing(mock_engine, check_destructive_flag=False)


def test_validate_engine_rejects_query_redirect_parameters():
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_url = MagicMock()
    mock_url.host = "127.0.0.1"
    mock_url.database = "my_test"
    mock_url.query = {"host": "remote.com"}
    mock_engine.url = mock_url

    with pytest.raises(RuntimeError, match="parámetro de conexión 'host'"):
        validate_engine_for_testing(mock_engine, check_destructive_flag=False)

    mock_url.query = {"hostaddr": "1.2.3.4"}
    with pytest.raises(RuntimeError, match="parámetro de conexión 'hostaddr'"):
        validate_engine_for_testing(mock_engine, check_destructive_flag=False)

    mock_url.query = {"service": "remote_service"}
    with pytest.raises(RuntimeError, match="parámetro de conexión 'service'"):
        validate_engine_for_testing(mock_engine, check_destructive_flag=False)


def test_validate_engine_rejects_remote_or_non_test(monkeypatch):
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_TEST_DB", "true")

    # Caso 1: Host remoto
    remote_engine = MagicMock()
    remote_engine.dialect.name = "postgresql"
    remote_url = MagicMock()
    remote_url.host = "ep-fancy-glitter.neon.tech"
    remote_url.database = "neondb_test"
    remote_url.query = {}
    remote_url.__str__.return_value = "postgresql://user:pass@ep-fancy-glitter.neon.tech/neondb_test"
    remote_engine.url = remote_url

    with pytest.raises(RuntimeError, match="host remoto, vacío o no autorizado"):
        validate_engine_for_testing(remote_engine, check_destructive_flag=True)

    # Caso 2: Host local pero DB no _test
    prod_local_engine = MagicMock()
    prod_local_engine.dialect.name = "postgresql"
    prod_url = MagicMock()
    prod_url.host = "127.0.0.1"
    prod_url.database = "tus_suplementos_prod"
    prod_url.query = {}
    prod_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_prod"
    prod_local_engine.url = prod_url

    with pytest.raises(RuntimeError, match="no termina en '_test'"):
        validate_engine_for_testing(prod_local_engine, check_destructive_flag=True)

    # Caso 3: Host vacío
    empty_host_engine = MagicMock()
    empty_host_engine.dialect.name = "postgresql"
    empty_url = MagicMock()
    empty_url.host = ""
    empty_url.database = "my_test"
    empty_url.query = {}
    empty_host_engine.url = empty_url

    with pytest.raises(RuntimeError, match="host remoto, vacío o no autorizado"):
        validate_engine_for_testing(empty_host_engine, check_destructive_flag=True)


def test_seed_data_guards(monkeypatch):
    # Si intentan llamar seed(remote_engine), debe explotar antes de ejecutar cualquier SQL
    remote_engine = MagicMock()
    remote_engine.dialect.name = "postgresql"
    remote_url = MagicMock()
    remote_url.host = "ep-prod.neon.tech"
    remote_url.database = "neondb"
    remote_url.query = {}
    remote_url.__str__.return_value = "postgresql://user:pass@ep-prod.neon.tech/neondb"
    remote_engine.url = remote_url

    with pytest.raises(RuntimeError):
        seed_data.seed(remote_engine)

    # Si intentan llamar seed(local_test_engine) sin el flag de autorización
    local_engine = MagicMock()
    local_engine.dialect.name = "postgresql"
    local_url = MagicMock()
    local_url.host = "127.0.0.1"
    local_url.database = "tus_suplementos_test"
    local_url.query = {}
    local_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    local_engine.url = local_url

    monkeypatch.delenv("ALLOW_DESTRUCTIVE_TEST_DB", raising=False)
    with pytest.raises(RuntimeError, match="OPERACIÓN BLOQUEADA"):
        seed_data.seed(local_engine)


def test_enforce_local_test_environment_missing_url(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="EJECUCIÓN BLOQUEADA"):
        enforce_local_test_environment("fusionar_duplicados.py", "ALLOW_MAINTENANCE_FUSION")


def test_enforce_local_test_environment_rejects_neon_dev(monkeypatch):
    neon_dev = "postgresql://neondb_owner:pass@ep-twilight-base-ass5vshw-pooler.c-4.eu-central-1.aws.neon.tech/neondb"
    monkeypatch.setenv("TEST_DATABASE_URL", neon_dev)
    with pytest.raises(RuntimeError, match="inseguro"):
        enforce_local_test_environment("reprocesar_nlp.py", "ALLOW_MAINTENANCE_REPROCESAR_NLP")


def test_enforce_local_test_environment_rejects_neon_prod(monkeypatch):
    neon_prod = "postgresql://user:pass@ep-fancy-glitter-ascs2vpv-pooler.c-4.eu-central-1.aws.neon.tech/neondb"
    monkeypatch.setenv("TEST_DATABASE_URL", neon_prod)
    with pytest.raises(RuntimeError, match="inseguro"):
        enforce_local_test_environment("fusionar_duplicados.py", "ALLOW_MAINTENANCE_FUSION")


def test_enforce_local_test_environment_rejects_remote_even_with_flag(monkeypatch):
    monkeypatch.setenv("ALLOW_MAINTENANCE_FUSION", "true")
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://user:pass@db.example.com:5432/remote_test")
    with pytest.raises(RuntimeError, match="inseguro"):
        enforce_local_test_environment("fusionar_duplicados.py", "ALLOW_MAINTENANCE_FUSION")


def test_enforce_local_test_environment_requires_flag(monkeypatch):
    valid_test_url = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    monkeypatch.setenv("TEST_DATABASE_URL", valid_test_url)
    monkeypatch.delenv("ALLOW_MAINTENANCE_PURGE_HISTORICOS", raising=False)
    with pytest.raises(RuntimeError, match="OPERACIÓN BLOQUEADA"):
        enforce_local_test_environment("limpiar_historicos_duplicados.py", "ALLOW_MAINTENANCE_PURGE_HISTORICOS")


def test_enforce_local_test_environment_success(monkeypatch):
    valid_test_url = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    monkeypatch.setenv("TEST_DATABASE_URL", valid_test_url)
    monkeypatch.setenv("ALLOW_MAINTENANCE_FUSION", "true")

    url_ret = enforce_local_test_environment("fusionar_duplicados.py", "ALLOW_MAINTENANCE_FUSION")
    assert url_ret == valid_test_url
    assert os.environ["TESTING"] == "1"
    assert os.environ["DATABASE_URL"] == valid_test_url


def test_validate_destructive_script_execution_strictly_local(monkeypatch):
    local_engine = MagicMock()
    local_engine.dialect.name = "postgresql"
    local_url = MagicMock()
    local_url.host = "127.0.0.1"
    local_url.database = "tus_suplementos_test"
    local_url.query = {}
    local_url.__str__.return_value = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    local_engine.url = local_url

    # Sin flag
    monkeypatch.delenv("ALLOW_DESTRUCTIVE_RESET", raising=False)
    with pytest.raises(RuntimeError, match="OPERACIÓN BLOQUEADA"):
        validate_destructive_script_execution(
            engine=local_engine,
            script_name="reset_db.py",
            flag_name="ALLOW_DESTRUCTIVE_RESET",
        )

    # Con flag
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_RESET", "true")
    validate_destructive_script_execution(
        engine=local_engine,
        script_name="reset_db.py",
        flag_name="ALLOW_DESTRUCTIVE_RESET",
    )

    # Intento contra Neon remoto, incluso si alguien pasa un flag
    remote_engine = MagicMock()
    remote_engine.dialect.name = "postgresql"
    remote_url = MagicMock()
    remote_url.host = "ep-fancy-glitter.neon.tech"
    remote_url.database = "neondb"
    remote_url.query = {}
    remote_url.__str__.return_value = "postgresql://user:pass@ep-fancy-glitter.neon.tech/neondb"
    remote_engine.url = remote_url

    monkeypatch.setenv("ALLOW_MAINTENANCE_FUSION", "true")
    with pytest.raises(RuntimeError, match="host remoto, vacío o no autorizado"):
        validate_destructive_script_execution(
            engine=remote_engine,
            script_name="fusionar_duplicados.py",
            flag_name="ALLOW_MAINTENANCE_FUSION",
        )


def test_validate_test_database_url_rejects_evil_scheme():
    with pytest.raises(RuntimeError, match="esquema o dialecto no autorizado"):
        validate_test_database_url("postgresql.evil://127.0.0.1:54329/tus_suplementos_test")

    with pytest.raises(RuntimeError, match="esquema o dialecto no autorizado"):
        validate_test_database_url("postgresql_fake://127.0.0.1:54329/tus_suplementos_test")

    with pytest.raises(RuntimeError, match="esquema o dialecto no autorizado"):
        validate_test_database_url("postgresql+://127.0.0.1:54329/tus_suplementos_test")

    # Confirmar esquemas válidos
    validate_test_database_url("postgresql://127.0.0.1:54329/tus_suplementos_test")
    validate_test_database_url("postgresql+psycopg2://127.0.0.1:54329/tus_suplementos_test")
    validate_test_database_url("postgresql+asyncpg://127.0.0.1:54329/tus_suplementos_test")


def test_ping_bd_argparse_parser():
    parser = create_parser()

    # 1. --test solo
    args_test = parser.parse_args(["--test"])
    assert args_test.test is True
    assert args_test.dev is False

    # 2. --dev solo
    args_dev = parser.parse_args(["--dev"])
    assert args_dev.test is False
    assert args_dev.dev is True

    # 3. Sin argumentos -> error
    with pytest.raises(SystemExit):
        parser.parse_args([])

    # 4. Con ambos: --test --dev -> error
    with pytest.raises(SystemExit):
        parser.parse_args(["--test", "--dev"])

    # 5. Con ambos: --dev --test -> error
    with pytest.raises(SystemExit):
        parser.parse_args(["--dev", "--test"])

    # 6. Argumentos desconocidos -> error
    with pytest.raises(SystemExit):
        parser.parse_args(["--foo"])

    with pytest.raises(SystemExit):
        parser.parse_args(["--test", "--extra"])


def test_ping_bd_select_target_url_execution(monkeypatch):
    test_url = "postgresql://postgres@127.0.0.1:54329/tus_suplementos_test"
    dev_url = "postgresql://neondb_owner:pass@ep-twilight-base.neon.tech/neondb"

    monkeypatch.setenv("TEST_DATABASE_URL", test_url)
    monkeypatch.setenv("DATABASE_URL", dev_url)

    # 1. --test funciona correctamente
    url, modo = select_target_url(["--test"])
    assert url == test_url
    assert "TESTING LOCAL" in modo

    # 2. --dev funciona correctamente
    url, modo = select_target_url(["--dev"])
    assert url == dev_url
    assert "DESARROLLO" in modo

    # 3. Sin argumentos se produce error
    with pytest.raises(SystemExit):
        select_target_url([])

    # 4. Con --test --dev se produce error
    with pytest.raises(SystemExit):
        select_target_url(["--test", "--dev"])

    # 5. Con --dev --test se produce error
    with pytest.raises(SystemExit):
        select_target_url(["--dev", "--test"])

    # 6. Con argumentos desconocidos se produce error
    with pytest.raises(SystemExit):
        select_target_url(["--unknown"])

    # 7. Con --test y URL ausente se aborta la ejecución
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL no está configurada"):
        select_target_url(["--test"])

    # 8. Con --test y URL insegura se aborta la ejecución
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://user:pass@ep-fancy.neon.tech/neondb")
    with pytest.raises(RuntimeError, match="inseguro"):
        select_target_url(["--test"])

    # 9. Con --dev y DATABASE_URL ausente se aborta la ejecución
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL no está configurada"):
        select_target_url(["--dev"])


def test_database_py_does_not_execute_create_extension():
    # Asegurar que database.py NO contiene 'CREATE EXTENSION' en su código
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_file = os.path.join(backend_dir, "database.py")
    with open(db_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "CREATE EXTENSION" not in content, "database.py no debe contener CREATE EXTENSION en tiempo de importación"
