"""Herramienta de diagnóstico de conectividad a la base de datos (100% Solo Lectura).

Realiza comprobaciones exclusivamente de lectura (SELECT 1 y conteos de tablas).
NO importa database.py para evitar cualquier ejecución de DDL o ajuste de secuencias
(ensure_schema_compatibility). Totalmente inocuo para cualquier entorno.

Uso unívoco:
    python backend/scripts/ping_bd.py --test   (Diagnostica la base local TEST_DATABASE_URL)
    python backend/scripts/ping_bd.py --dev    (Diagnostica la base DATABASE_URL de backend/.env)
"""
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

from security_guards import validate_test_database_url, is_test_environment

load_dotenv(os.path.join(BACKEND_DIR, ".env"), override=False)


def select_target_url() -> tuple[str, str]:
    """Determina unívocamente la URL a diagnosticar según flags o variables explícitas."""
    args = sys.argv[1:]

    if "--test" in args:
        test_url = os.environ.get("TEST_DATABASE_URL", "").strip()
        if not test_url:
            print("❌ Error: Se solicitó modo testing (--test), pero TEST_DATABASE_URL no está definido.")
            sys.exit(1)
        validate_test_database_url(test_url)
        return test_url, "TESTING LOCAL (PostgreSQL _test)"

    if "--dev" in args:
        dev_url = os.environ.get("DATABASE_URL", "").strip()
        if not dev_url:
            print("❌ Error: Se solicitó modo desarrollo (--dev), pero DATABASE_URL no está configurado.")
            sys.exit(1)
        return dev_url, "DESARROLLO / PRODUCCIÓN"

    # Si se ejecuta dentro de un contexto declarado de testing
    if is_test_environment() or ("TEST_DATABASE_URL" in os.environ and "DATABASE_URL" not in os.environ):
        test_url = os.environ.get("TEST_DATABASE_URL", "").strip()
        if not test_url:
            print("❌ Error: Entorno de testing detectado pero TEST_DATABASE_URL no está definido.")
            sys.exit(1)
        validate_test_database_url(test_url)
        return test_url, "TESTING LOCAL (PostgreSQL _test)"

    if "DATABASE_URL" in os.environ:
        return os.environ["DATABASE_URL"].strip(), "DESARROLLO / PRODUCCIÓN (default)"

    print("⚠️  Selección de destino requerida:")
    print("Debes especificar unívocamente qué entorno deseas diagnosticar:")
    print("    python backend/scripts/ping_bd.py --test   (Diagnostica TEST_DATABASE_URL)")
    print("    python backend/scripts/ping_bd.py --dev    (Diagnostica DATABASE_URL)")
    sys.exit(1)


def ping():
    db_url, modo_str = select_target_url()

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
