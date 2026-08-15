import sys
from sqlalchemy.sql.expression import func

print("🔍 AUDITORÍA VISUAL DE DESCRIPCIONES SANEADAS\n" + "="*55)

try:
    from database import SessionLocal
    import models

    db = SessionLocal()
    
    # Traemos 5 productos aleatorios que tengan descripción
    productos = db.query(models.Producto).filter(
        models.Producto.descripcion.isnot(None)
    ).order_by(func.random()).limit(5).all()
    
    for p in productos:
        print(f"💊 PRODUCTO: {p.nombre}")
        print(f"📝 DESCRIPCIÓN: {p.descripcion}")
        print("-" * 55)
        
    db.close()
except Exception as e:
    print(f"❌ FALLO AL CONSULTAR DB: {e}")