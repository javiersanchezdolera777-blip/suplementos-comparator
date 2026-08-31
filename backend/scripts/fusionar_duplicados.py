import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
from sqlalchemy import func, text


def fusionar_duplicados():
    db = SessionLocal()
    print("🔍 Buscando productos duplicados (mismo slug)...")

    try:
        # 1. Encontrar slugs repetidos
        slugs_duplicados = (
            db.query(models.Producto.slug)
            .group_by(models.Producto.slug)
            .having(func.count(models.Producto.id) > 1)
            .all()
        )

        if not slugs_duplicados:
            print("✅ No hay duplicados. La base de datos está limpia.")
        else:
            print(
                f"⚠️ Se encontraron {len(slugs_duplicados)} slugs duplicados. Iniciando fusión..."
            )

            # Mapeo de tabla -> columna padre (para evitar colisiones de claves únicas)
            tablas_padres = {
                "favoritos": "usuario_id",
                "historial_vistas": "usuario_id",
                "stack_producto": "stack_id",
                "resenas_sabores": "perfil_id",
            }

            for (slug,) in slugs_duplicados:
                productos = (
                    db.query(models.Producto).filter(models.Producto.slug == slug).all()
                )
                # Elegir el maestro (el que tenga imagen o el primero)
                maestro = next((p for p in productos if p.imagen_url), productos[0])
                clones = [p for p in productos if p.id != maestro.id]

                print(
                    f"  -> Fusionando '{slug}' ({len(clones)} clones) en el ID Maestro {maestro.id}"
                )

                for clone in clones:
                    # 1. Mover Ofertas al Maestro (no hay peligro de colisión aquí)
                    db.execute(
                        text(
                            "UPDATE ofertas SET producto_id = :master_id WHERE producto_id = :clone_id"
                        ),
                        {"master_id": maestro.id, "clone_id": clone.id},
                    )

                    # 2. Mover Relaciones Comunitarias de forma segura
                    for tabla, col_padre in tablas_padres.items():
                        # A. Borramos la relación del clon SI el maestro ya la tiene con el mismo usuario/stack
                        query_delete = f"""
                            DELETE FROM {tabla} WHERE producto_id = :clone_id 
                            AND {col_padre} IN (SELECT {col_padre} FROM {tabla} WHERE producto_id = :master_id)
                        """
                        db.execute(
                            text(query_delete),
                            {"master_id": maestro.id, "clone_id": clone.id},
                        )

                        # B. Actualizamos los clones que quedan sin miedo a chocar
                        query_update = f"UPDATE {tabla} SET producto_id = :master_id WHERE producto_id = :clone_id"
                        db.execute(
                            text(query_update),
                            {"master_id": maestro.id, "clone_id": clone.id},
                        )

                    # 3. Eliminar el clon
                    db.delete(clone)

            db.commit()
            print("✅ Fusión de duplicados completada con éxito.")

        # 2. Restaurar el candado UNIQUE
        print("🔒 Restaurando candado de seguridad UNIQUE en la columna slug...")
        db.execute(text("DROP INDEX IF EXISTS ix_productos_slug;"))
        db.execute(text("CREATE UNIQUE INDEX ix_productos_slug ON productos (slug);"))
        db.commit()
        print("✅ Candado UNIQUE restaurado correctamente.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la fusión: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    fusionar_duplicados()
