"""Módulo central de seguridad y blindaje de entornos para bases de datos.

Este módulo previene la ejecución accidental de pruebas, benchmarks y scripts destructivos
en bases de datos no autorizadas (como ramas de Neon de desarrollo, staging o producción).
"""
import os
import sys
from urllib.parse import urlparse

HOSTS_LOCALES_PERMITIDOS = {"localhost", "127.0.0.1", "::1", ""}


def is_local_host(host: str | None) -> bool:
    """Comprueba si un host corresponde a una interfaz de loopback local."""
    h = (host or "").strip().lower()
    return h in HOSTS_LOCALES_PERMITIDOS or h == "localhost"


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

    Reglas:
    1. No puede ser vacía.
    2. No puede ser remota ni contener referencias a Neon.
    3. El host debe ser estrictamente localhost, 127.0.0.1 o ::1.
    4. El nombre de la base de datos debe terminar en '_test'.
    """
    if not url or not url.strip():
        raise RuntimeError(
            "TEST_DATABASE_URL no está definido o está vacío. "
            "Las pruebas y benchmarks requieren un PostgreSQL local aislado "
            "(ej: postgresql://postgres@127.0.0.1:54329/tus_suplementos_test)."
        )

    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()

    if is_remote_url(url):
        raise RuntimeError(
            f"TEST_DATABASE_URL inseguro: se detectó un host remoto o no autorizado ({host!r}). "
            "Está estrictamente prohibido ejecutar pruebas o benchmarks contra bases remotas o Neon."
        )

    db_name = (parsed.path or "").strip("/")
    if not db_name.endswith("_test"):
        raise RuntimeError(
            f"TEST_DATABASE_URL inseguro: la base de datos {db_name!r} no termina en '_test'. "
            "Por seguridad, la base de datos de pruebas debe llamarse *_test."
        )


def is_test_environment() -> bool:
    """Detecta si el proceso actual se está ejecutando en contexto de testing o benchmark."""
    if os.environ.get("TESTING", "").lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("ENV", "").lower() == "test" or os.environ.get("ENVIRONMENT", "").lower() == "test":
        return True
    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return False


def get_active_database_url() -> str:
    """Determina la URL de base de datos activa según el entorno.

    - Si el entorno es de testing: EXIGE TEST_DATABASE_URL validado y lo devuelve.
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
    """Verifica que un SQLAlchemy Engine apunte exclusivamente a una base de datos local de test.

    Opcionalmente exige que una variable de entorno de autorización explícita esté presente.
    """
    if engine is None or not hasattr(engine, "url"):
        raise ValueError("Engine inválido o nulo proporcionado a validate_engine_for_testing.")

    url = engine.url
    host = (url.host or "").strip().lower()
    database = (url.database or "").strip()

    # Comprobar host
    if not is_local_host(host) or "neon" in str(url).lower():
        raise RuntimeError(
            f"OPERACIÓN ABORTADA POR SEGURIDAD: El engine apunta a un host remoto o no autorizado ({host!r}). "
            "Las operaciones de prueba/benchmark solo están permitidas en PostgreSQL local."
        )

    # Comprobar nombre de base de datos
    if not database.endswith("_test"):
        raise RuntimeError(
            f"OPERACIÓN ABORTADA POR SEGURIDAD: El engine apunta a la base de datos {database!r}, "
            "que no termina en '_test'. Operación cancelada para proteger datos de desarrollo/producción."
        )

    # Comprobar flag destructivo si se solicita
    if check_destructive_flag:
        flag_val = os.environ.get(flag_name, "").strip().lower()
        if flag_val not in ("1", "true", "yes"):
            raise RuntimeError(
                f"OPERACIÓN DESTRUCTIVA BLOQUEADA: Se requiere definir la variable de entorno {flag_name}=true "
                f"para autorizar el borrado/truncado en la base de datos de pruebas {database!r}."
            )


def validate_destructive_script_execution(
    engine,
    script_name: str,
    flag_name: str,
    allow_non_test: bool = False,
) -> None:
    """Guardia de seguridad para scripts de reseteo o mantenimiento destructivo.

    - Si allow_non_test es False: el script SOLO puede ejecutarse en base de datos local *_test
      y exige además la variable flag_name=true.
    - Si allow_non_test es True: el script puede ejecutarse en otros entornos solo si el usuario
      proporciona explícitamente flag_name=true.
    """
    if engine is None or not hasattr(engine, "url"):
        raise ValueError(f"Engine inválido en script '{script_name}'.")

    url = engine.url
    host = (url.host or "local").strip().lower()
    database = (url.database or "").strip()

    if not allow_non_test:
        validate_engine_for_testing(engine, check_destructive_flag=True, flag_name=flag_name)
    else:
        flag_val = os.environ.get(flag_name, "").strip().lower()
        if flag_val not in ("1", "true", "yes"):
            raise RuntimeError(
                f"EJECUCIÓN BLOQUEADA en script '{script_name}':\n"
                f"Este script realiza modificaciones en la base de datos '{database}' (host: '{host}').\n"
                f"Para autorizar su ejecución, debes definir la variable de entorno:\n"
                f"    {flag_name}=true\n"
            )
