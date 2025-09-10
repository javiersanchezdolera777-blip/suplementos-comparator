# src/utils/database.py
from src import db

def get_or_create(model, **kwargs):
    """
    Función utilitaria para obtener o crear un objeto en la base de datos
    """
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False  # Encontrado, no creado
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        return instance, True   # Creado nuevo