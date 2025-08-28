from flask import Blueprint, render_template, jsonify, request
from models.product import Product, db

main_bp = Blueprint('main', __name__)

# Datos de ejemplo para desarrollo
sample_products = [
    {
        'id': 1,
        'name': 'Whey Gold Standard',
        'category': 'Proteína',
        'category_color': 'proteina',
        'brand': 'Optimum Nutrition',
        'size': '2.27kg',
        'price': 54.99,
        'rating': 4.7,
        'image_url': 'https://via.placeholder.com/200x150?text=Proteína+Whey'
    },
    {
        'id': 2,
        'name': 'Creatina Monohidrato',
        'category': 'Creatina',
        'category_color': 'creatina',
        'brand': 'MyProtein',
        'size': '500g',
        'price': 19.99,
        'rating': 4.5,
        'image_url': 'https://via.placeholder.com/200x150?text=Creatina+Monohidrato'
    },
    # Añadir más productos de ejemplo...
]

@main_bp.route('/')
def index():
    return render_template('index.html', products=sample_products)

@main_bp.route('/productos')
def productos():
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 1000, type=float)
    
    # En una versión real, esto consultaría la base de datos
    filtered_products = sample_products
    
    if category:
        filtered_products = [p for p in filtered_products if p['category'].lower() == category.lower()]
    
    filtered_products = [p for p in filtered_products if min_price <= p['price'] <= max_price]
    
    return render_template('productos.html', products=filtered_products)

@main_bp.route('/api/productos')
def api_productos():
    # Lógica similar para API JSON
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])