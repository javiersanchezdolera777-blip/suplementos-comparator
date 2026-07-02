import csv
import models
from database import SessionLocal, engine

# Nos aseguramos de que las tablas existen en la base de datos
models.Base.metadata.create_all(bind=engine)

def procesar_csv(ruta_archivo):
    db = SessionLocal()
    print(f"Iniciando la lectura del catálogo: {ruta_archivo}")

    try:
        # Abrimos el archivo CSV
        with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
            # DictReader usa la primera línea del CSV (brand, category...) como claves
            lector_csv = csv.DictReader(archivo)
            
            for fila in lector_csv:
                # --- 1. GESTIÓN DE LA MARCA ---
                nombre_marca = fila["brand"]
                marca = db.query(models.Marca).filter(models.Marca.nombre == nombre_marca).first()
                if not marca:
                    marca = models.Marca(nombre=nombre_marca)
                    db.add(marca)
                    db.commit()
                    db.refresh(marca)
                
                # --- 2. GESTIÓN DE LA CATEGORÍA ---
                nombre_cat = fila["category"]
                categoria = db.query(models.Categoria).filter(models.Categoria.nombre == nombre_cat).first()
                if not categoria:
                    categoria = models.Categoria(nombre=nombre_cat)
                    db.add(categoria)
                    db.commit()
                    db.refresh(categoria)

                # --- 3. CREACIÓN O ACTUALIZACIÓN DEL PRODUCTO ---
                nombre_prod = fila["name"]
                precio_prod = float(fila["price"]) # Convertimos el texto a número decimal
                
                producto = db.query(models.Producto).filter(models.Producto.nombre == nombre_prod).first()
                
                if not producto:
                    # Si no existe, lo insertamos nuevo
                    nuevo_producto = models.Producto(
                        nombre=nombre_prod,
                        descripcion=fila["description"],
                        precio=precio_prod,
                        imagen_url=fila["image_url"],
                        afiliado_url=fila["affiliate_url"],
                        marca_id=marca.id,
                        categoria_id=categoria.id
                    )
                    db.add(nuevo_producto)
                    print(f"✅ Nuevo producto añadido: {nombre_prod}")
                else:
                    # Si ya existe, comprobamos el precio para actualizarlo
                    if producto.precio != precio_prod:
                        producto.precio = precio_prod
                        print(f"🔄 Precio actualizado para: {nombre_prod}")
                    else:
                        print(f"➡️ Sin cambios en: {nombre_prod}")

            # Guardamos todos los cambios en la base de datos
            db.commit()
            print("\n🚀 ¡Sincronización del Data Feed completada con éxito!")
            
    except Exception as e:
        print(f"❌ Ocurrió un error al procesar el archivo: {e}")
    finally:
        db.close() # Siempre cerramos la conexión

if __name__ == "__main__":
    procesar_csv("catalogo_amazon.csv")
