# src/routes/main_routes.py
from flask import Blueprint, render_template, jsonify, request
from ..models.product import Product, db
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_products = Product.query.order_by(Product.rating.desc()).limit(6).all()
    return render_template('index.html', products=featured_products)

@main_bp.route('/productos')
def productos():
    # Esta vista ahora solo muestra todos los productos inicialmente
    # El filtrado se hará via JavaScript
    products = Product.query.all()
    return render_template('productos.html', products=products)

@main_bp.route('/api/productos/filtrar', methods=['POST'])
def api_filtrar_productos():
    try:
        filters = request.get_json()
        
        query = Product.query
        
        # Filtros de categoría
        if filters.get('categorias'):
            query = query.filter(Product.category.in_(filters['categorias']))
        
        # Filtros de subcategoría
        if filters.get('subcategorias'):
            query = query.filter(Product.subcategory.in_(filters['subcategorias']))
        
        # Filtros de objetivo
        if filters.get('objetivos'):
            query = query.filter(Product.objetivo.in_(filters['objetivos']))
        
        # Filtros de características
        if filters.get('caracteristicas'):
            # Buscar productos que tengan al menos una de las características
            conditions = []
            for caracteristica in filters['caracteristicas']:
                conditions.append(Product.caracteristicas.ilike(f'%{caracteristica}%'))
            query = query.filter(or_(*conditions))
        
        # Filtro de ofertas
        if filters.get('ofertas'):
            query = query.filter(Product.original_price > Product.price)
        
        # Ordenamiento
        sort = filters.get('sort', 'rating-desc')
        if sort == 'price-asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price-desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'name-asc':
            query = query.order_by(Product.name.asc())
        elif sort == 'name-desc':
            query = query.order_by(Product.name.desc())
        else:  # rating-desc por defecto
            query = query.order_by(Product.rating.desc())
        
        products = query.all()
        
        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products],
            'count': len(products)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/productos')
def api_productos():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])