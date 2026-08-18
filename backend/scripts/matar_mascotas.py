import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from sqlalchemy import or_

def purgar_animales():
    db = SessionLocal()
    try:
        terminos = ["%perro%", "%gato%", "%mascota%", "%cachorro%", "%veterinari%", "%felino%"]
        condiciones = [models.Producto.descripcion.ilike(t) for t in terminos] + [models.Producto.nombre.ilike(t) for t in terminos]
        
        productos_animales = db.query(models.Producto).filter(or_(*condiciones)).all()
        
        for p in productos_animales:
            db.delete(p)
            
        db.commit()
        print(f"✅ ¡Purga completada! Se han eliminado {len(productos_animales)} productos veterinarios.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    purgar_animales()
