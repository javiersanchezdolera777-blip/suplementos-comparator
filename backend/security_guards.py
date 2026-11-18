"""Módulo central de seguridad y blindaje de entornos para bases de datos.

Este módulo previene la ejecución accidental de pruebas, benchmarks y scripts de mantenimiento
o reseteo en bases de datos no autorizadas (como ramas de Neon de desarrollo, staging o producción).
"""
import os
import sys
from urllib.parse import urlparse, parse_qs

HOSTS_LOCALES_PERMITIDOS = {"localhost", "127.0.0.1", "::1"}
PARAMETROS_QUERY_PROHIBIDOS = {"host", "hostaddr", "service"}


def is_valid_postgres_scheme(scheme: str) -> bool:
    """Verifica que el esquema sea exclusivamente 'postgresql' o 'postgresql+<driver>'.

    Rechaza esquemas como 'postgresql.evil', 'postgresql_fake', 'sqlite', 'mysql', etc.
    """
    if scheme == "postgresql":
        return True
    if scheme.startswith("postgresql+"):
        driver = scheme[len("postgresql+"):]
        return bool(driver) and driver.replace("_", "").isalnum()
    return False


def is_local_host(host: str | None) -> bool:
    """Comprueba si un host corresponde a una interfaz de loopback local explícita."""
    if not host:
        return False
    h = host.strip().lower()
    return h in HOSTS_LOCALES_PERMITIDOS


def is_remote_url(url: str) -> bool:
    """Detecta si una URL de conexión apunta a un host remoto o contiene referencias a Neon."""
    if not url:
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()
    if "neon.tech" in url.lower() or "neon" in host:
        return True
    return not is_local_host(host)


def validate_test_database_url(url: str) -> None:
    """Valida rigurosamente que una URL corresponda a un PostgreSQL local de pruebas.

    Reglas estrictas:
    1. No puede ser vacía.
    2. Debe usar exclusivamente el driver PostgreSQL (postgresql:// o postgresql+...).
    3. El host debe ser explícitamente localhost, 127.0.0.1 o ::1 (no vacío).
    4. No puede contener referencias a Neon en URL ni host.
    5. No puede contener parámetros en query que redirijan la conexión (host, hostaddr, service).
    6. El nombre de la base de datos debe terminar estrictamente en '_test'.
    """
    if not url or not url.strip():
        raise RuntimeError(
            "TEST_DATABASE_URL no está definido o está vacío. "
            "Las pruebas, benchmarks y scripts de mantenimiento requieren un PostgreSQL local aislado "
            "(ej: postgresql://postgres@127.0.0.1:54329/tus_suplementos_test)."
        )

    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()

    # 1. Driver PostgreSQL obligatorio (rechaza sqlite, mysql, postgresql.evil, etc.)
    if not is_valid_postgres_scheme(scheme):
        raise RuntimeError(
            f"TEST_DATABASE_URL inseguro: esquema o dialecto no autorizado ({scheme!r}). "
            "Solo se admiten URLs de conexión PostgreSQL ('postgresql' o 'postgresql+<driver>')."
        )

    # 2. Host explícito no vacío
    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise RuntimeError(
            "TEST_DATABASE_URL inseguro: no se especificó un host explícito. "
            "Se requiere un hostname explícito de loopback (127.0.0.1, localhost o ::1)."
        )

    if not is_local_host(host) or "neon" in url.lower():
        raise RuntimeError(
            f"TEST_DATABASE_URL inseguro: se detectó un host remoto o no autorizado ({host!r}). "
            "Está estrictamente prohibido ejecutar pruebas, benchmarks o scripts de mantenimiento contra bases remotas o Neon."
        )

    # 3. Parámetros de query prohibidos que podrían desviar la conexión física
    if parsed.query:
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        for param in PARAMETROS_QUERY_PROHIBIDOS:
            if param in query_params:
                raise RuntimeError(
                    f"TEST_DATABASE_URL inseguro: se detectó el parámetro de conexión '{param}' en la query URL, "
                    "lo cual podría desviar la conexión hacia un host remoto no autorizado."
                )

    # 4. Sufijo _test obligatorio
    db_name = (parsed.path or "").strip("/")
    if not db_name.endswith("_test"):
        raise RuntimeError(
            f"TEST_DATABASE_URL inseguro: la base de datos {db_name!r} no termina en '_test'. "
            "Por seguridad, la base de datos autorizada para pruebas y mantenimiento debe llamarse *_test."
        )


def is_test_environment() -> bool:
    """Detecta si el proceso actual se está ejecutando en contexto de testing, benchmark o mantenimiento local."""
    if os.environ.get("TESTING", "").lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("ENV", "").lower() == "test" or os.environ.get("ENVIRONMENT", "").lower() == "test":
        return True
    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return False


def get_active_database_url() -> str:
    """Determina la URL de base de datos activa según el entorno.

    - Si el entorno es de testing/mantenimiento: EXIGE TEST_DATABASE_URL validado y lo devuelve.
      Si no está definido o es inválido, aborta INMEDIATAMENTE para impedir que
      el backend cargue accidentalmente la base de datos de desarrollo de backend/.env.
    - Si el entorno es de desarrollo normal: devuelve DATABASE_URL.
    """
    if is_test_environment() or "TEST_DATABASE_URL" in os.environ:
        test_url = os.environ.get("TEST_DATABASE_URL", "").strip()
        if not test_url:
            raise RuntimeError(
                "Modo TESTING detectado, pero TEST_DATABASE_URL no está configurado. "
                "Para evitar sobrescribir la base de datos de desarrollo o producción, "
                "la ejecución se ha detenido inmediatamente."
            )
        validate_test_database_url(test_url)
        return test_url

    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL no está definido. Revisa las variables de entorno o el archivo .env del backend."
        )
    return db_url


def validate_engine_for_testing(
    engine,
    check_destructive_flag: bool = False,
    flag_name: str = "ALLOW_DESTRUCTIVE_TEST_DB",
) -> None:
    """Verifica que un SQLAlchemy Engine apunte exclusivamente a una base de datos PostgreSQL local de test.

    Opcionalmente exige que una variable de entorno de autorización explícita esté presente.
    """
    if engine is None or not hasattr(engine, "url"):
        raise ValueError("Engine inválido o nulo proporcionado a validate_engine_for_testing.")

    # 1. Comprobar dialecto
    dialect_name = getattr(getattr(engine, "dialect", None), "name", "")
    if dialect_name != "postgresql":
        raise RuntimeError(
            f"OPERACIÓN ABORTADA POR SEGURIDAD: Dialecto del motor no autorizado ({dialect_name!r}). "
            "Solo se permite dialecto 'postgresql'."
        )

    url = engine.url
    host = (url.host or "").strip().lower()
    database = (url.database or "").strip()

    # 2. Comprobar host
    if not host or not is_local_host(host) or "neon" in str(url).lower():
        raise RuntimeError(
            f"OPERACIÓN ABORTADA POR SEGURIDAD: El engine apunta a un host remoto, vacío o no autorizado ({host!r}). "
            "Las operaciones de prueba, benchmark o mantenimiento solo están permitidas en PostgreSQL local."
        )

    # 3. Comprobar query parameters en url del engine
    url_query = getattr(url, "query", {})
    if isinstance(url_query, dict):
        for param in PARAMETROS_QUERY_PROHIBIDOS:
            if param in url_query:
                raise RuntimeError(
                    f"OPERACIÓN ABORTADA POR SEGURIDAD: El engine contiene el parámetro de conexión '{param}', "
                    "lo cual podría desviar la conexión hacia un host remoto no autorizado."
                )

    # 4. Comprobar nombre de base de datos
    if not database.endswith("_test"):
        raise RuntimeError(
            f"OPERACIÓN ABORTADA POR SEGURIDAD: El engine apunta a la base de datos {database!r}, "
            "que no termina en '_test'. Operación cancelada para proteger datos de desarrollo/producción."
        )

    # 5. Comprobar flag destructivo si se solicita
    if check_destructive_flag:
        flag_val = os.environ.get(flag_name, "").strip().lower()
        if flag_val not in ("1", "true", "yes"):
            raise RuntimeError(
                f"OPERACIÓN BLOQUEADA: Se requiere definir la variable de entorno {flag_name}=true "
                f"para autorizar esta operación en la base de datos local de pruebas {database!r}."
            )


def enforce_local_test_environment(script_name: str, flag_name: str | None = None) -> str:
    """Guardia PREVIO a la importación de SQLAlchemy para scripts de mantenimiento y reseteo.

    Garantiza que:
    1. Se declare el entorno como testing (TESTING=1).
    2. TEST_DATABASE_URL esté definido y apunte estrictamente a un PostgreSQL local *_test.
    3. Ningún flag permita ejecutar operaciones contra Neon dev o producción.
    4. Se verifique la variable flag_name (si se proporciona) antes de importar database.py,
       impidiendo cualquier efecto secundario DDL o de setval() sobre bases no autorizadas.
    5. Fija DATABASE_URL=TEST_DATABASE_URL en el proceso.
    """
    os.environ["TESTING"] = "1"

    test_url = os.environ.get("TEST_DATABASE_URL", "").strip()
    if not test_url:
        raise RuntimeError(
            f"EJECUCIÓN BLOQUEADA en script '{script_name}':\n"
            f"Por directriz estricta de seguridad, todos los scripts de mantenimiento y reseteo\n"
            f"deben ejecutarse exclusivamente contra un PostgreSQL local de pruebas (*_test).\n"
            f"Debes configurar la variable de entorno antes de ejecutar:\n"
            f"    $env:TEST_DATABASE_URL = 'postgresql://postgres@127.0.0.1:54329/tus_suplementos_test'"
        )

    validate_test_database_url(test_url)

    if flag_name:
        flag_val = os.environ.get(flag_name, "").strip().lower()
        if flag_val not in ("1", "true", "yes"):
            raise RuntimeError(
                f"OPERACIÓN BLOQUEADA en script '{script_name}':\n"
                f"Se requiere autorizar explícitamente la operación mediante el flag:\n"
                f"    {flag_name}=true"
            )

    os.environ["DATABASE_URL"] = test_url
    return test_url


def validate_destructive_script_execution(
    engine,
    script_name: str,
    flag_name: str,
    allow_non_test: bool = False,
) -> None:
    """Guardia de motor SQLAlchemy para scripts de reseteo o mantenimiento.

    En esta fase, todas las herramientas de mantenimiento y reseteo están restringidas
    exclusivamente a bases de datos locales *_test. El parámetro allow_non_test queda
    estrictamente inhabilitado por seguridad para impedir cualquier acceso remoto.
    """
    if engine is None or not hasattr(engine, "url"):
        raise ValueError(f"Engine inválido en script '{script_name}'.")

    # Validación estricta: siempre exige que el engine sea local, termine en _test y tenga el flag activo
    validate_engine_for_testing(engine, check_destructive_flag=True, flag_name=flag_name)
