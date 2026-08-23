import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# 1. Añadimos el directorio raíz del backend al path para poder importar models.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 2. Cargar las variables de entorno desde backend/.env
load_dotenv()

# 3. Validar de forma estricta que existe la URL de conexión
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("❌ CRÍTICO: No se ha encontrado la variable DATABASE_URL en el entorno.")
    print("Asegúrate de que el archivo .env existe en la carpeta backend y está bien configurado.")
    sys.exit(1)

# 4. Importar la Base de SQLAlchemy y los modelos para que Alembic los detecte
import models
from database import Base

target_metadata = Base.metadata

config = context.config

# 5. Sobrescribir dinámicamente la URL en el config de Alembic
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
