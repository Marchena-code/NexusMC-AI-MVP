import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError, BaseModel # Añadir BaseModel para TokenData placeholder
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

# Importaciones relativas desde el mismo nivel 'core' o niveles superiores
from .config import settings
from ..db.database import get_db
from ..models.user import User
# Importar TokenData desde su nueva ubicación
from ..schemas.token import TokenData

# Esquema OAuth2 para obtener el token de las cabeceras
# El tokenUrl debe coincidir con la ruta del endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Configuración de Passlib para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Contraseña ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

# --- Funciones de Token JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un nuevo token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Usa el tiempo de expiración de la configuración si no se provee delta
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Dependencia para Obtener Usuario Actual ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependencia para obtener el usuario actual basado en el token JWT.
    Decodifica el token, valida los datos y obtiene el usuario de la BD.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: Optional[str] = payload.get("sub") # Hacer email opcional temporalmente
        if email is None:
            print("DEBUG: JWT payload no contiene 'sub' (email)")
            raise credentials_exception
        # Validar con el esquema TokenData
        try:
            token_data = TokenData(email=email)
        except ValidationError as e:
             print(f"DEBUG: Error de validación de TokenData: {e}")
             raise credentials_exception

    except JWTError as e:
        print(f"DEBUG: Error al decodificar JWT: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"DEBUG: Usuario no encontrado en BD para email: {email}")
        raise credentials_exception
    # print(f"DEBUG: Usuario autenticado: {user.email}") # Línea de depuración opcional
    return user

# --- Funciones de Encriptación (para Plaid Token) ---
# Asegúrate de que ENCRYPTION_KEY sea una clave válida generada por Fernet.generate_key()
# y codificada en base64 url-safe.

fernet = None # Inicializar a None
try:
    # Inicializar Fernet. Lanzará error si la clave no es válida.
    # La clave debe ser bytes
    fernet_key_bytes = settings.ENCRYPTION_KEY.encode()
    fernet = Fernet(fernet_key_bytes)
    print("DEBUG: Instancia de Fernet creada exitosamente.") # Debug
except (ValueError, TypeError) as e:
    print(f"ERROR CRÍTICO: La ENCRYPTION_KEY ({settings.ENCRYPTION_KEY[:5]}...) no es válida para Fernet: {e}")
    # En un caso real, probablemente deberías lanzar un error fatal aquí
    # raise ValueError(f"La ENCRYPTION_KEY configurada no es válida: {e}")
    pass # Permitir que continúe por ahora, pero las funciones fallarán

def encrypt_data(data: str) -> Optional[bytes]:
    """Encripta datos de tipo string usando la clave Fernet."""
    if fernet and isinstance(data, str):
        try:
            return fernet.encrypt(data.encode('utf-8'))
        except Exception as e:
            print(f"Error al encriptar datos: {e}")
            return None
    elif not fernet:
        print("ERROR: Intento de encriptar sin instancia válida de Fernet.")
    return None

def decrypt_data(encrypted_data: bytes) -> Optional[str]:
    """Desencripta datos usando la clave Fernet y devuelve un string."""
    if fernet and isinstance(encrypted_data, bytes):
        try:
            return fernet.decrypt(encrypted_data).decode('utf-8')
        except Exception as e: # Captura errores de desencriptación (ej. token inválido, padding incorrecto)
            print(f"Error al desencriptar datos: {e}")
            return None
    elif not fernet:
        print("ERROR: Intento de desencriptar sin instancia válida de Fernet.")
    return None 