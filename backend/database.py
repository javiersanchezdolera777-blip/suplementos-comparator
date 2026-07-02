from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Definimos dónde se guardará la base de datos (en un archivo local llamado suplementos.db)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Creamos una "fábrica de sesiones" (las sesiones son como carritos de la compra para sacar/meter datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base es la clase principal de la que heredarán nuestros modelos (nuestras tablas)
Base = declarative_base()