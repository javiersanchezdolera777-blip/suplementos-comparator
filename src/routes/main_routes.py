from flask import Blueprint, render_template, jsonify, request
from models.product import Product, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Obtener productos destacados (mejor valoración)
    featured_products = Product.query.order_by(Product.rating.desc()).limit(6).all()
    return render_template('index.html', products=featured_products)

@main_bp.route('/productos')
def productos():
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 1000, type=float)
    brand = request.args.get('brand', '')
    
    query = Product.query
    
    if category:
        query = query.filter_by(category=category)
    if brand:
        query = query.filter_by(brand=brand)
    
    query = query.filter(Product.price.between(min_price, max_price))
    
    # Ordenar por mejor valoración o precio
    sort = request.args.get('sort', 'rating')
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.rating.desc())
    
    products = query.all()
    return render_template('productos.html', products=products)

@main_bp.route('/api/productos')
def api_productos():
    # API para filtros avanzados
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])