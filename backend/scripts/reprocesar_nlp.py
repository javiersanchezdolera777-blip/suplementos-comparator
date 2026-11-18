import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BLINDAJE DE SEGURIDAD PRE-IMPORTACIÓN:
# Exige entorno local de test y flag antes de cargar database.py o inicializar SQLAlchemy.
from security_guards import enforce_local_test_environment, validate_destructive_script_execution

enforce_local_test_environment("reprocesar_nlp.py", "ALLOW_MAINTENANCE_REPROCESAR_NLP")

from database import SessionLocal, engine
from models import Producto, Categoria
from ingestores.utils import clasificar_producto


def reprocesar_todo():
    validate_destructive_script_execution(
        engine=engine,
        script_name="reprocesar_nlp.py",
        flag_name="ALLOW_MAINTENANCE_REPROCESAR_NLP",
    )
    db = SessionLocal()
    print("🧠 Iniciando reprocesamiento masivo con NLP en base local de test...")

    productos = db.query(Producto).all()
    mapa_cats = {c.nombre: c.id for c in db.query(Categoria).all()}
    actualizados = 0

    for p in productos:
        if not p.nombre:
            continue

        desc = p.descripcion or ""
        etiquetas = clasificar_producto(p.nombre, desc)

        if etiquetas and etiquetas.get("categoria"):
            cat_nombre = etiquetas.get("categoria")
            if cat_nombre in mapa_cats:
                p.categoria_id = mapa_cats[cat_nombre]

            p.formato = etiquetas.get("formato")

            sabor_nuevo = etiquetas.get("sabor")
            p.sabor = (
                sabor_nuevo
                if isinstance(sabor_nuevo, list)
                else ([sabor_nuevo] if sabor_nuevo else [])
            )

            p.objetivo = etiquetas.get("objetivo")
            p.es_vegano = bool(etiquetas.get("es_vegano"))
            p.sin_gluten = bool(etiquetas.get("sin_gluten"))
            p.sin_lactosa = bool(etiquetas.get("sin_lactosa"))
            p.sello_calidad = etiquetas.get("sello_calidad")
            p.tipo_proteina = etiquetas.get("tipo_proteina")
            p.tipo_creatina = etiquetas.get("tipo_creatina")
            p.perfil_aminoacidos = etiquetas.get("perfil_aminoacidos")
            p.tipo_vitamina = etiquetas.get("tipo_vitamina")

            actualizados += 1

    db.commit()
    print(
        f"✅ ¡Completado! {actualizados} productos han sido re-etiquetados con éxito."
    )
    db.close()


if __name__ == "__main__":
    reprocesar_todo()
