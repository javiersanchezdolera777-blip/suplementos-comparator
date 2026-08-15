import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import models

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("❌ CRÍTICO: No se ha encontrado la variable DATABASE_URL.")
    exit(1)

# Iniciar conexión
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def sanitize_text(text: str) -> str:
    if not text:
        return text
    
    # 1. Eliminar CTAs intrusivos (Ignorando mayúsculas/minúsculas)
    cta_patterns = [
        r"¡?cómpralo en hsn!?\s*",
        r"¡?haz tu pedido hoy!?\s*",
        r"¡?compra ahora!?\s*",
        r"encuentra esto en hsn\s*",
        r"garantía hsn\s*",
        r"¡?compra( aquí)?!?\s*",
        r"visita nuestra tienda\s*",
        r"haz click aquí\s*"
    ]
    for pattern in cta_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # 2. Corregir formato: asegurar mayúscula después de punto, interrogación, exclamación (cierre y apertura)
    # Busca . ! ? ¡ ¿ seguido de espacios y una minúscula
    def capitalize_match(match):
        symbol = match.group(1)
        letter = match.group(2).upper()
        if symbol in ['¡', '¿']:
            return f"{symbol}{letter}"
        else:
            return f"{symbol} {letter}"
        
    text = re.sub(r"([.!?¡¿])\s*([a-zA-ZñÑáéíóúÁÉÍÓÚ])", capitalize_match, text)
    
    # 3. Limpiar espacios extra creados por las eliminaciones
    text = re.sub(r"\s{2,}", " ", text).strip()

    # 4. Capitalizar la primera letra del string completo (si es minúscula o símbolo)
    if text:
        # Encontrar el primer caracter alfanumérico
        match = re.search(r"[a-zñáéíóú]", text, re.IGNORECASE)
        if match and match.group(0).islower():
            idx = match.start()
            text = text[:idx] + text[idx].upper() + text[idx+1:]
        
    return text

def run_scrubber():
    db = SessionLocal()
    print("🧹 Iniciando Saneamiento de Descripciones (Scrubber)...")
    try:
        productos = db.query(models.Producto).all()
        modificados = 0
        
        for p in productos:
            if not p.descripcion:
                continue
            
            cleaned = sanitize_text(p.descripcion)
            if cleaned != p.descripcion:
                p.descripcion = cleaned
                modificados += 1
                
        if modificados > 0:
            db.commit()
            print(f"✅ Éxito: Se han saneado las descripciones de {modificados} productos en la BD.")
        else:
            print("ℹ️ Todo limpio. No se encontraron descripciones con formato erróneo o CTAs.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el saneamiento: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_scrubber()
