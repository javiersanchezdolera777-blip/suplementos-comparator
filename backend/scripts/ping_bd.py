"""Herramienta de diagnóstico de conectividad a la base de datos (Solo Lectura).

Realiza comprobaciones exclusivamente de lectura (SELECT 1 y conteos de tablas).
NO importa database.py para evitar cualquier ejecución de DDL o ajuste de secuencias
(ensure_schema_compatibility). Totalmente inocuo para cualquier entorno.
"""
import os
import sys
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno del backend si están presentes
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BACKEND_DIR, ".env"), override=False)


def ping():
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("TEST_DATABASE_URL")
    if not db_url:
        print("❌ Error: No se ha encontrado DATABASE_URL ni TEST_DATABASE_URL en el entorno.")
        sys.exit(1)

    # Enmascarar contraseña para mostrar en pantalla
    parsed = urlparse(db_url)
    host_display = parsed.hostname or "local"
    db_name = (parsed.path or "").strip("/")
    user = parsed.username or ""
    safe_target = f"{user}@{host_display}:{parsed.port or 5432}/{db_name}"

    print("\n" + "=" * 60)
    print("📡 PING DE BASE DE DATOS (100% SOLO LECTURA)")
    print("=" * 60)
    print(f"Destino: {safe_target}")
    print("Garantía: Sin DDL, sin alteración de secuencias, sin escrituras.")

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

            # 2. Conteo seguro de tablas públicas
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
