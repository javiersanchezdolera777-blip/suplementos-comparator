# from src import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy() 

db.Model.metadata.clear()

class Product(db.Model):
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # Categoría principal
    subcategory = db.Column(db.String(100))  # ← NUEVO CAMPO: Subcategoría
    brand = db.Column(db.String(100))
    price = db.Column(db.Float)
    original_price = db.Column(db.Float)
    rating = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500))
    product_url = db.Column(db.String(500))
    store = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    size = db.Column(db.String(50))
    flavor = db.Column(db.String(50))
    price_history = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,  # ← NUEVO CAMPO
            'brand': self.brand,
            'price': self.price,
            'original_price': self.original_price,
            'rating': self.rating,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'store': self.store,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'size': self.size,
            'flavor': self.flavor,
            'price_history': json.loads(self.price_history) if self.price_history else []
        }
    
    def update_price(self, new_price):
        history = json.loads(self.price_history) if self.price_history else []
        history.append({
            'price': new_price,
            'date': datetime.utcnow().isoformat()
        })
        self.price_history = json.dumps(history)
        self.price = new_price
        self.last_updated = datetime.utcnow()