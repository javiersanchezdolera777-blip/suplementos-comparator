from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Importamos a nuestros "trabajadores"
import models
from database import engine, SessionLocal

# 1. LA ORDEN DE CONSTRUCCIÓN: Le decimos al motor que lea los modelos y cree las tablas
models.Base.metadata.create_all(bind=engine)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API de Suplementos",
    description="Backend para el comparador de suplementos",
    version="1.0.0"
)

# 2. LAS REGLAS DEL "CARRITO" (Dependencia de la Base de Datos)
def get_db():
    db = SessionLocal() # Abrimos la despensa
    try:
        yield db        # Entregamos los ingredientes mientras la petición esté viva
    finally:
        db.close()      # SIEMPRE cerramos la despensa al terminar, pase lo que pase

# Nuestro endpoint de prueba (la ventanilla del recepcionista)
@app.get("/")
def leer_raiz():
    return {"mensaje": "¡Hola! El servidor de FastAPI y la Base de Datos están conectados 🚀"}