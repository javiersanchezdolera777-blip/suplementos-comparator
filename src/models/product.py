from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta  # ← AÑADE ESTA IMPORTACIÓN
import json

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    product_url = db.Column(db.String(300))
    rating = db.Column(db.Float)
    
    # NUEVOS CAMPOS para los filtros
    objetivo = db.Column(db.String(100))  # Aumento masa muscular, Perder grasa, etc.
    caracteristicas = db.Column(db.String(300))  # Vegano, Sin lactosa, Sin gluten, etc.
    sabor = db.Column(db.String(100))  # Chocolate, Vainilla, Frutos rojos, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prices = db.relationship('PriceHistory', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'current_price': self.current_price,
            'best_price': self.best_price,
            'image_url': self.image_url,
            'rating': self.rating,
            'objetivo': self.objetivo,
            'caracteristicas': self.caracteristicas,
            'sabor': self.sabor,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @property
    def current_price(self):
        # Último precio registrado
        latest_price = PriceHistory.query.filter_by(product_id=self.id)\
                                        .order_by(PriceHistory.timestamp.desc())\
                                        .first()
        return latest_price.price if latest_price else None
    
    @property
    def best_price(self):
        # Mejor precio histórico
        best_price = PriceHistory.query.filter_by(product_id=self.id)\
                                      .order_by(PriceHistory.price.asc())\
                                      .first()
        return best_price.price if best_price else None
    
    @property
    def last_updated(self):
        latest_price = PriceHistory.query.filter_by(product_id=self.id)\
                                        .order_by(PriceHistory.timestamp.desc())\
                                        .first()
        return latest_price.timestamp if latest_price else None


class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    store = db.Column(db.String(100), nullable=False)
    offer = db.Column(db.Boolean, default=False)
    discount_percentage = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'price': self.price,
            'store': self.store,
            'offer': self.offer,
            'discount_percentage': self.discount_percentage,
            'timestamp': self.timestamp.isoformat()
        }


class Store(db.Model):
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    scraping_interval = db.Column(db.Integer, default=24)  # horas
    last_scraped = db.Column(db.DateTime)