 # src/__init__.py
from flask_sqlalchemy import SQLAlchemy

# ✅ Una sola instancia de SQLAlchemy para toda la aplicación
db = SQLAlchemy()

# Importar modelos después de crear db (para evitar importaciones circulares)
from .models.product import Product