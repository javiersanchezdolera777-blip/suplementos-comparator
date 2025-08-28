# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'suplementos.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Otras configuraciones
SECRET_KEY = 'tu-clave-secreta-aqui-cambiar-en-produccion'