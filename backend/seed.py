import json
import models
from database import SessionLocal

def cargar_datos():
    # 1. Abrimos el "carrito" de la base de datos
    db = SessionLocal()
    
    print("Iniciando la inyección de datos...")

    # 2. Leemos el archivo JSON del frontend
    # Asegúrate de que la ruta coincide con donde está tu archivo
    ruta_json = "../frontend/src/data/mock_products.json"
    
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            productos_mock = json.load(archivo)
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo en {ruta_json}")
        return

    # 3. Recorremos cada producto del JSON
    for item in productos_mock:
        
        # --- GESTIÓN DE MARCAS ---
        # Miramos si la marca ya existe en la base de datos para no repetirla
        nombre_marca = item["brand"]["name"]
        marca = db.query(models.Marca).filter(models.Marca.nombre == nombre_marca).first()
        
        if not marca:
            marca = models.Marca(nombre=nombre_marca)
            db.add(marca)
            db.commit() # Guardamos para que se genere su ID
            db.refresh(marca)

        # --- GESTIÓN DE CATEGORÍAS ---
        # Hacemos lo mismo con la categoría
        nombre_categoria = item["category"]["name"]
        categoria = db.query(models.Categoria).filter(models.Categoria.nombre == nombre_categoria).first()
        
        if not categoria:
            categoria = models.Categoria(nombre=nombre_categoria)
            db.add(categoria)
            db.commit()
            db.refresh(categoria)

        # --- CREACIÓN DEL PRODUCTO ---
        # Comprobamos que el producto no esté ya guardado
        producto_existente = db.query(models.Producto).filter(models.Producto.nombre == item["name"]).first()
        
        if not producto_existente:
            nuevo_producto = models.Producto(
                nombre=item["name"],
                descripcion=item["description"],
                precio=item["price"],
                imagen_url=item["image_url"],
                afiliado_url=item["affiliate_url"],
                marca_id=marca.id,           # Conectamos con el ID de la marca
                categoria_id=categoria.id    # Conectamos con el ID de la categoría
            )
            db.add(nuevo_producto)

    # 4. Confirmamos todos los cambios finales y cerramos
    db.commit()
    db.close()
    print("✅ ¡Base de datos llenada con éxito! La despensa está lista.")

# Esta línea hace que la función se ejecute al arrancar el archivo
if __name__ == "__main__":
    cargar_datos()