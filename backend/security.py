from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

# 1. Configuración del encriptador (Bcrypt)
# Esto es lo que convertirá "mi_contraseña_123" en "$2b$12$indescifrable..."
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Configuración del JWT
# Nota: En un entorno real puro, el SECRET_KEY se guarda en el archivo .env
SECRET_KEY = "super_secreto_para_suplementos_comparator_api"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # La pulsera VIP dura 1 semana (en minutos)

def verificar_password(plain_password: str, hashed_password: str):
    """Comprueba si la contraseña que escribe el usuario coincide con la encriptada en BD."""
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password: str):
    """Cifra la contraseña antes de guardarla en la base de datos."""
    return pwd_context.hash(password)

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    """Fabrica la 'pulsera VIP' (JWT) metiendo dentro el email del usuario."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Sellamos el token con nuestra palabra secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt