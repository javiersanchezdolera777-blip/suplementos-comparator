import os
from dotenv import load_dotenv # <-- NUEVO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# 1. Definimos dónde se guardará la base de datos (en un archivo local llamado suplementos.db)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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