import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def limpiar_categorias():
    db = SessionLocal()
    try:
        # 1. Buscar la categoría correcta
        cat_salud = db.query(models.Categoria).filter_by(nombre="Salud y Bienestar").first()
        cat_otros = db.query(models.Categoria).filter_by(nombre="Otros").first()
        
        if cat_otros and cat_salud:
            # 2. Mover todos los productos de 'Otros' a 'Salud'
            productos = db.query(models.Producto).filter_by(categoria_id=cat_otros.id).all()
            for p in productos:
                p.categoria_id = cat_salud.id
            db.commit()
            print(f"✅ Se han movido {len(productos)} productos de Drasanvi a 'Salud y Bienestar'.")
            
            # 3. Borrar la categoría 'Otros'
            db.delete(cat_otros)
            db.commit()
            print("✅ Categoría 'Otros' eliminada de la base de datos.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    limpiar_categorias()