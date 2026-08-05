import os
from dotenv import load_dotenv # <-- NUEVO
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargamos las variables de entorno desde el archivo .env del backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, ".env"))

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definido. Revisa el archivo .env del backend.")

print("🗄️ Conectando a la base de datos configurada en el backend/.env")
engine = create_engine(SQLALCHEMY_DATABASE_URL)


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

            if conn.dialect.name == "postgresql":
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

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,       # <--- Esto es la clave: comprueba si la BD está viva antes de usarla
    pool_recycle=3600,        # <--- Recicla la conexión cada hora para que no caduque
    pool_size=10,             # Mantener un pequeño pool de conexiones
    max_overflow=20
)

# 3. Creamos una "fábrica de sesiones" (las sesiones son como carritos de la compra para sacar/meter datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base es la clase principal de la que heredarán nuestros modelos (nuestras tablas)
Base = declarative_base()