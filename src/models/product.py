from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    rating = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(300))
    product_url = db.Column(db.String(300), nullable=False)
    store = db.Column(db.String(50), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    size = db.Column(db.String(50))
    flavor = db.Column(db.String(50))
    
    # Precios históricos (almacenados como JSON)
    price_history = db.Column(db.Text, default='[]')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'price': self.price,
            'original_price': self.original_price,
            'rating': self.rating,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'store': self.store,
            'last_updated': self.last_updated.isoformat(),
            'size': self.size,
            'flavor': self.flavor
        }
    
    def update_price(self, new_price):
        # Guardar historial de precios
        history = json.loads(self.price_history)
        history.append({
            'price': new_price,
            'date': datetime.utcnow().isoformat()
        })
        # Mantener solo los últimos 30 días
        if len(history) > 30:
            history = history[-30:]
        
        self.original_price = self.original_price or new_price
        self.price = new_price
        self.price_history = json.dumps(history)
        self.last_updated = datetime.utcnow()