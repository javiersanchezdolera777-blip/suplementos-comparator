from flask import Blueprint, render_template, jsonify, request
from models.product import Product, db

main_bp = Blueprint('main', __name__)

# Datos de ejemplo para desarrollo CON LOS NUEVOS FILTROS
sample_products = [
    {
        'id': 1,
        'name': 'Whey Gold Standard',
        'category': 'Proteína',
        'category_color': 'proteina',
        'brand': 'Optimum Nutrition',
        'size': '2.27kg',
        'price': 54.99,
        'image_url': 'https://via.placeholder.com/200x150?text=Proteína+Whey',
        'objetivo': 'Aumento masa muscular, Recuperación muscular',
        'caracteristicas': 'Sin gluten, Sin lactosa',
        'sabor': 'Chocolate, Vainilla, Fresa'
    },
    {
        'id': 2,
        'name': 'Creatina Monohidrato',
        'category': 'Creatina',
        'category_color': 'creatina',
        'brand': 'MyProtein',
        'size': '500g',
        'price': 19.99,
        'image_url': 'https://via.placeholder.com/200x150?text=Creatina+Monohidrato',
        'objetivo': 'Aumento fuerza, Mejora rendimiento',
        'caracteristicas': 'Vegano, Sin aditivos',
        'sabor': 'Sin sabor'
    },
    {
        'id': 3,
        'name': 'Proteína Vegana',
        'category': 'Proteína',
        'category_color': 'proteina',
        'brand': 'Vegetarian',
        'size': '1kg',
        'price': 39.99,
        'image_url': 'https://via.placeholder.com/200x150?text=Proteína+Vegana',
        'objetivo': 'Aumento masa muscular, Definición',
        'caracteristicas': 'Vegano, Sin lactosa, Sin gluten, Orgánico',
        'sabor': 'Chocolate, Vainilla'
    },
    {
        'id': 4,
        'name': 'Quemador Termogénico',
        'category': 'Quemadores',
        'category_color': 'quemadores',
        'brand': 'Muscletech',
        'size': '120 cápsulas',
        'price': 29.99,
        'image_url': 'https://via.placeholder.com/200x150?text=Quemador+Termogénico',
        'objetivo': 'Perder grasa, Definición, Energía',
        'caracteristicas': 'Sin azúcar, Vegano',
        'sabor': 'Naranja, Limón'
    },
    {
        'id': 5,
        'name': 'BCAA Aminoácidos',
        'category': 'Aminoácidos',
        'category_color': 'aminoacidos',
        'brand': 'Scivation',
        'size': '30 serv',
        'price': 24.99,
        'image_url': 'https://via.placeholder.com/200x150?text=BCAA+Aminoácidos',
        'objetivo': 'Recuperación muscular, Prevenir catabolismo',
        'caracteristicas': 'Sin azúcar, Sin gluten',
        'sabor': 'Sandía, Limón'
    },
    {
        'id': 6,
        'name': 'Pre-entreno Explosivo',
        'category': 'Pre-entreno',
        'category_color': 'pre-entreno',
        'brand': 'C4',
        'size': '30 serv',
        'price': 34.99,
        'image_url': 'https://via.placeholder.com/200x150?text=Pre-entreno+Explosivo',
        'objetivo': 'Energía, Foco mental, Rendimiento',
        'caracteristicas': 'Sin azúcar, Vegano',
        'sabor': 'Frutos rojos, Naranja'
    }
]

@main_bp.route('/')
def index():
    # Mostrar solo 4 productos destacados en la homepage
    featured_products = sample_products[:4]
    return render_template('index.html', products=featured_products)

@main_bp.route('/productos')
def productos():
    category = request.args.get('category', '')
    objetivo = request.args.get('objetivo', '')
    caracteristicas = request.args.get('caracteristicas', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 1000, type=float)
    
    # Filtrar productos
    filtered_products = sample_products
    
    # Filtro por categoría
    if category:
        filtered_products = [p for p in filtered_products if p['category'].lower() == category.lower()]
    
    # NUEVO: Filtro por objetivo
    if objetivo:
        filtered_products = [p for p in filtered_products 
                           if p.get('objetivo') and objetivo.lower() in p['objetivo'].lower()]
    
    # NUEVO: Filtro por características
    if caracteristicas:
        filtered_products = [p for p in filtered_products 
                           if p.get('caracteristicas') and caracteristicas.lower() in p['caracteristicas'].lower()]
    
    # Filtro por precio
    filtered_products = [p for p in filtered_products if min_price <= p['price'] <= max_price]
    
    return render_template('productos.html', products=filtered_products)

@main_bp.route('/api/productos')
def api_productos():
    # Para API JSON, ahora incluye los nuevos campos
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'brand': p.brand,
        'price': p.current_price,
        'image_url': p.image_url,
        'objetivo': p.objetivo,
        'caracteristicas': p.caracteristicas,
        'sabor': p.sabor
    } for p in products])

# NUEVA RUTA: Para obtener opciones de filtros
@main_bp.route('/api/filtros')
def api_filtros():
    # Esto sería dinámico con base de datos real
    categorias = ['Proteína', 'Creatina', 'Pre-entreno', 'Quemadores', 'Aminoácidos']
    objetivos = ['Aumento masa muscular', 'Perder grasa', 'Definición', 'Energía', 'Recuperación muscular']
    caracteristicas = ['Vegano', 'Sin lactosa', 'Sin gluten', 'Sin azúcar', 'Orgánico']
    
    return jsonify({
        'categorias': categorias,
        'objetivos': objetivos,
        'caracteristicas': caracteristicas
    })