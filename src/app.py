# src/app.py
from flask import Flask
from .routes.main_routes import main_bp
from . import db  # ← Importar desde el paquete centralizado
import os

def create_app():
    app = Flask(__name__)
    
    # Configuración
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.py')
    
    if os.path.exists(config_path):
        app.config.from_pyfile(config_path)
        print("✅ Configuración cargada correctamente")
    else:
        print("❌ Usando configuración temporal")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'suplementos.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'clave-secreta-temporal'
    
    # ✅ Inicializar la instancia centralizada
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("✅ Tablas de la base de datos verificadas")
    
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)