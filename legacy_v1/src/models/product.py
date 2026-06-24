# src/models/product.py
from datetime import datetime
import json
from src import db  # ← Importar la instancia centralizada
import unicodedata

# Intentamos usar ftfy para arreglar mojibake; si no está, usamos fallback
try:
    import ftfy
    def fix_mojibake(s):
        if not s:
            return s
        return ftfy.fix_text(s)
except Exception:
    def fix_mojibake(s):
        if not s:
            return s
        if isinstance(s, bytes):
            try:
                return s.decode('utf-8')
            except Exception:
                try:
                    return s.decode('latin-1')
                except Exception:
                    return s.decode('utf-8', errors='ignore')
        # Intento simple de revertir mojibake típico
        try:
            return s.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
        except Exception:
            return s

def normalize_search_text(s):
    """
    Resultado: ascii simple, minúsculas, sin acentos, solo letras/números y espacios.
    Ideal para filtros/índices.
    """
    if not s:
        return None
    s = fix_mojibake(s)
    s = s.strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    # dejar solo letras/números y espacios
    s = re.sub(r'[^0-9A-Za-z]+', ' ', s)
    s = s.lower().strip()
    return s if s else None

def normalize_display_text(s):
    """
    Arregla mojibake para mostrar (preserva acentos si es posible).
    """
    if not s:
        return s
    s = fix_mojibake(s)
    return s.strip()

class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Normalizamos los campos clave
        if self.category:
            self.category = normalizar_texto(self.category)
        if self.subcategory:
            self.subcategory = normalizar_texto(self.subcategory)
        if self.brand:
            self.brand = normalizar_texto(self.brand)

class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = {'extend_existing': True}  # 👈 evita redefiniciones


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  
    subcategory = db.Column(db.String(100))
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
    
    # NUEVOS CAMPOS PARA LOS FILTROS
    objetivo = db.Column(db.String(100))  # Objetivo del suplemento
    caracteristicas = db.Column(db.String(200))  # Características especiales
    protein_per_serving = db.Column(db.Float)  # Proteína por porción
    servings_per_container = db.Column(db.Integer)  # Porciones por envase
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,  # Cambiado de 'category'
            'subcategory': self.subcategory,
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
            'price_history': json.loads(self.price_history) if self.price_history else [],
            # Nuevos campos
            'objetivo': self.objetivo,
            'caracteristicas': self.caracteristicas,
            'protein_per_serving': self.protein_per_serving,
            'servings_per_container': self.servings_per_container
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