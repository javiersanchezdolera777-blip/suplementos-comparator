import json
import models
from database import SessionLocal

def cargar_datos():
    # 1. Abrimos el "carrito" de la base de datos
    db = SessionLocal()
    
    print("Iniciando la inyección de datos...")

    # 2. Leemos el archivo JSON del frontend
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
        nombre_marca = item["brand"]["name"]
        marca = db.query(models.Marca).filter(models.Marca.nombre == nombre_marca).first()
        if not marca:
            marca = models.Marca(nombre=nombre_marca)
            db.add(marca)
            db.commit()
            db.refresh(marca)

        # --- GESTIÓN DE CATEGORÍAS ---
        nombre_categoria = item["category"]["name"]
        categoria = db.query(models.Categoria).filter(models.Categoria.nombre == nombre_categoria).first()
        if not categoria:
            categoria = models.Categoria(nombre=nombre_categoria)
            db.add(categoria)
            db.commit()
            db.refresh(categoria)

        # ========================================================
        # 🧠 EL CEREBRO: ASIGNACIÓN AUTOMÁTICA DE OBJETIVO 🧠
        # ========================================================
        nombre_min = item["name"].lower()
        cat_min = item["category"]["name"].lower()
        
        # ========================================================
        # 🧠 EL CEREBRO: ASIGNACIÓN AUTOMÁTICA DE OBJETIVO 🧠
        # ========================================================
        nombre_min = item["name"].lower()
        cat_min = item["category"]["name"].lower()
        
        # Ojo: Aquí ponemos exactamente las frases de tu nuevo schemas.py
        objetivo_calculado = "Salud y Bienestar" 

        if "whey" in nombre_min or "prote" in nombre_min or "gainer" in nombre_min or "masa" in nombre_min:
            objetivo_calculado = "Volumen Muscular"
        elif "creatina" in cat_min or "pre-entreno" in cat_min or "pump" in nombre_min or "energia" in nombre_min:
            objetivo_calculado = "Rendimiento Deportivo"
        elif "termogenico" in nombre_min or "quemador" in nombre_min or "carnitina" in nombre_min or "cut" in nombre_min:
            objetivo_calculado = "Pérdida de Peso"
        # ========================================================
        # ========================================================

        # --- CREACIÓN DEL PRODUCTO ---
        producto_existente = db.query(models.Producto).filter(models.Producto.nombre == item["name"]).first()
        
        if not producto_existente:
            nuevo_producto = models.Producto(
                nombre=item["name"],
                descripcion=item["description"],
                precio=item["price"],
                imagen_url=item["image_url"],
                afiliado_url=item["affiliate_url"],
                sabor=item.get("sabor"),
                formato=item.get("formato"),
                
                # ¡AQUÍ USAMOS LO QUE HA CALCULADO EL CEREBRO!
                objetivo=objetivo_calculado, 
                
                caracteristicas=item.get("caracteristicas"),
                marca_id=marca.id,
                categoria_id=categoria.id
            )
            db.add(nuevo_producto)

    # 4. Confirmamos todos los cambios finales y cerramos
    db.commit()
    db.close()
    print("✅ ¡Base de datos llenada con éxito! La despensa está lista.")

if __name__ == "__main__":
    cargar_datos()