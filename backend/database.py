from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Definimos dónde se guardará la base de datos (en un archivo local llamado suplementos.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./suplementos.db"

# 2. Creamos el "motor" que se conecta a la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Esto es un requisito específico de SQLite
)

# 3. Creamos una "fábrica de sesiones" (las sesiones son como carritos de la compra para sacar/meter datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base es la clase principal de la que heredarán nuestros modelos (nuestras tablas)
Base = declarative_base()