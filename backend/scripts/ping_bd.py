"""Herramienta de diagnóstico de conectividad a la base de datos (100% Solo Lectura).

Realiza comprobaciones exclusivamente de lectura (SELECT 1 y conteos de tablas).
NO importa database.py para evitar cualquier ejecución de DDL o ajuste de secuencias
(ensure_schema_compatibility). Totalmente inocuo para cualquier entorno.

Uso unívoco:
    python backend/scripts/ping_bd.py --test   (Diagnostica la base local TEST_DATABASE_URL)
    python backend/scripts/ping_bd.py --dev    (Diagnostica la base DATABASE_URL de backend/.env)
"""
import argparse
import os
import sys
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Añadir ruta del backend para importar security_guards
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from security_guards import validate_test_database_url

load_dotenv(os.path.join(BACKEND_DIR, ".env"), override=False)


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser con grupo mutuamente excluyente y obligatorio (--test o --dev)."""
    parser = argparse.ArgumentParser(
        prog="ping_bd.py",
        description="Diagnóstico de conectividad a base de datos (100% Solo Lectura).",
        allow_abbrev=False,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--test",
        action="store_true",
        help="Diagnostica la base de datos local de pruebas configurada en TEST_DATABASE_URL.",
    )
    group.add_argument(
        "--dev",
        action="store_true",
        help="Diagnostica la base de desarrollo configurada en DATABASE_URL (backend/.env).",
    )
    return parser


def select_target_url(argv: list[str] | None = None) -> tuple[str, str]:
    """Determina unívocamente la URL a diagnosticar usando argparse.

    Requisitos estrictos:
    - --test y --dev son mutuamente excluyentes y obligatorios.
    - Se rechazan argumentos desconocidos.
    - Se rechaza la ausencia de ambos.
    - No existe fallback automático.
    - --test exige y valida TEST_DATABASE_URL estrictamente contra PostgreSQL local *_test.
    - --dev exige DATABASE_URL.
    """
    parser = create_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.test:
        test_url = os.environ.get("TEST_DATABASE_URL", "").strip()
        if not test_url:
            raise RuntimeError(
                "Se solicitó modo testing (--test), pero la variable de entorno "
                "TEST_DATABASE_URL no está configurada o está vacía."
            )
        validate_test_database_url(test_url)
        return test_url, "TESTING LOCAL (PostgreSQL _test)"

    if args.dev:
        dev_url = os.environ.get("DATABASE_URL", "").strip()
        if not dev_url:
            raise RuntimeError(
                "Se solicitó modo desarrollo (--dev), pero la variable de entorno "
                "DATABASE_URL no está configurada o está vacía."
            )
        return dev_url, "DESARROLLO / PRODUCCIÓN"

    raise RuntimeError("Selección de entorno no especificada.")


def ping(argv: list[str] | None = None):
    try:
        db_url, modo_str = select_target_url(argv)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"❌ Error de configuración: {exc}")
        sys.exit(1)

    # Enmascarar credenciales para reporte seguro
    parsed = urlparse(db_url)
    host_display = parsed.hostname or "local"
    db_name = (parsed.path or "").strip("/")
    user = parsed.username or ""
    safe_target = f"{user}@{host_display}:{parsed.port or 5432}/{db_name}"

    print("\n" + "=" * 60)
    print(f"📡 PING DE BASE DE DATOS [{modo_str}]")
    print("=" * 60)
    print(f"Destino:  {safe_target}")
    print("Garantía: 100% Solo Lectura (sin DDL, sin alteración de secuencias).")

    # Conexión aislada de solo lectura (sin importar database.py)
    engine = create_engine(
        db_url,
        execution_options={"isolation_level": "AUTOCOMMIT"},
        pool_pre_ping=False,
    )

    try:
        t0 = time.perf_counter()
        with engine.connect() as conn:
            # 1. Ping básico
            conn.execute(text("SELECT 1"))
            latency_ms = (time.perf_counter() - t0) * 1000

            # 2. Conteo de tablas públicas
            res_tables = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )).fetchall()
            table_names = {row[0] for row in res_tables}

            # 3. Conteo de filas si existen las tablas
            n_productos = None
            if "productos" in table_names:
                n_productos = conn.execute(text("SELECT COUNT(*) FROM productos")).scalar()

            n_ofertas = None
            if "ofertas" in table_names:
                n_ofertas = conn.execute(text("SELECT COUNT(*) FROM ofertas")).scalar()

        print(f"✅ Conexión establecida con éxito en {latency_ms:.2f} ms")
        print(f"📋 Tablas en esquema público: {len(table_names)}")
        if n_productos is not None:
            print(f"📦 Total productos: {n_productos}")
        if n_ofertas is not None:
            print(f"🏷️  Total ofertas:   {n_ofertas}")
        print("=" * 60 + "\n")

    except Exception as exc:
        print(f"❌ Error al conectar o consultar: {exc}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    ping()
