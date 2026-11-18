import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Añadimos el directorio backend al sys.path si es necesario para importar security_guards
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from security_guards import get_active_database_url, is_test_environment

# Solo cargamos backend/.env si no se ha prohibido explícitamente y no pisa variables existentes
load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, ".env"), override=False)

# Obtenemos la URL blindada según el entorno (testing vs dev/prod)
SQLALCHEMY_DATABASE_URL = get_active_database_url()

# Creamos el engine principal con opciones de pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20
)

# Indicador de conexión seguro (sin contraseñas)
entorno_str = "TESTING LOCAL" if is_test_environment() else "DESARROLLO / PRODUCCIÓN"
try:
    safe_target = engine.url.render_as_string(hide_password=True)
except Exception:
    safe_target = f"{engine.url.host or 'local'}/{engine.url.database}"
print(f"🔌 Conectando a la base de datos ({entorno_str}): {safe_target}")


def ensure_schema_compatibility():
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'productos'
                      AND column_name = 'precio_anterior'
                )
            """))
            exists = result.scalar()
            if not exists:
                conn.execute(text("ALTER TABLE productos ADD COLUMN precio_anterior DOUBLE PRECISION"))
                print("✅ Columna precio_anterior añadida a productos")
                
            result_presentacion = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'productos'
                      AND column_name = 'presentacion'
                )
            """))
            exists_presentacion = result_presentacion.scalar()
            if not exists_presentacion:
                conn.execute(text("ALTER TABLE productos ADD COLUMN presentacion VARCHAR"))
                print("✅ Columna presentacion añadida a productos")

            if conn.dialect.name == "postgresql":
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
                except Exception as ext_err:
                    print(f"⚠️ No se pudo verificar o crear la extensión pg_trgm: {ext_err}")

                for table, pk in [("marcas", "id"), ("categorias", "id"), ("productos", "id"), ("usuarios", "id"), ("favoritos", "id")]:
                    exists_table = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'public' AND table_name = :table_name
                        )
                    """), {"table_name": table}).scalar()
                    if not exists_table:
                        continue

                    seq_name = conn.execute(text("SELECT pg_get_serial_sequence(:table_name, :pk_column)"), {
                        "table_name": table,
                        "pk_column": pk,
                    }).scalar()
                    if seq_name:
                        conn.execute(text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX({pk}) FROM {table}), 0) + 1, false)"))
                        print(f"✅ Secuencia ajustada para {table}")
    except Exception as exc:
        print(f"⚠️ No se pudo validar o ajustar el esquema de la base de datos: {exc}")


ensure_schema_compatibility()

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para modelos
Base = declarative_base()
