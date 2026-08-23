import sys
import os

# Añadimos la raíz del backend para poder importar la base de datos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Producto, Marca

def purgar_fantasmas():
    db = SessionLocal()
    try:
        print("🕵️‍♂️ Escaneando Neon DB en busca de productos corruptos o zombis...")
        
        # 1. Buscamos el ID de la marca "Desconocida"
        marca_desc = db.query(Marca).filter(Marca.nombre == "Desconocida").first()
        id_desc = marca_desc.id if marca_desc else -1
        
        # 2. Localizamos la basura: Productos sin imagen, sin enlace, o de marca Desconocida
        productos_basura = db.query(Producto).filter(
            (Producto.imagen_url == None) | 
            (Producto.imagen_url == "") | 
            (Producto.afiliado_url == "") |
            (Producto.marca_id == id_desc)
        ).all()
        
        if not productos_basura:
            print("✅ ¡Tu base de datos está impoluta! No hay productos fantasma.")
            return

        print(f"🗑️ Se han encontrado {len(productos_basura)} productos corruptos. Iniciando purga...")
        
        for p in productos_basura:
            print(f"   - 💥 Eliminando: {p.nombre} (ID: {p.id})")
            db.delete(p)
            
        db.commit()
        print("\n🎉 ¡Purga completada! La base de datos está limpia y optimizada.")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    purgar_fantasmas()