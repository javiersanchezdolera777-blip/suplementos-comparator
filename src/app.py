# app.py
from flask import Flask
from routes.main_routes import main_bp
from models.product import db




def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    
    # Inicializar base de datos
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)