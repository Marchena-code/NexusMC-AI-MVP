from pydantic_settings import BaseSettings
from pydantic import Field # Asegúrate de importar Field si usas default_factory o validaciones
from dotenv import load_dotenv
import os
from typing import Optional

# Carga las variables del archivo .env en el entorno
load_dotenv()

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

    # Seguridad JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_super_secret_key_change_me")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Clave de Encriptación Fernet (Debe ser de 32 bytes URL-safe base64 encoded)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "generate_a_real_32_byte_key_please") # Placeholder - ¡Generar una real!

    # Plaid API
    PLAID_CLIENT_ID: Optional[str] = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET_SANDBOX: Optional[str] = os.getenv("PLAID_SECRET_SANDBOX")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")

    # Hugging Face API
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")

    # Configuración para cargar desde .env si existe
    # class Config:
    #    env_file = ".env"
    #    env_file_encoding = 'utf-8'
    # No necesitamos la clase Config si usamos load_dotenv() al principio

# Crear una instancia de la configuración para usarla en la aplicación
settings = Settings()

# Validación simple para la clave de encriptación (ajustar según necesidad)
if settings.ENCRYPTION_KEY == "generate_a_real_32_byte_key_please":
   print("ADVERTENCIA: ¡La ENCRYPTION_KEY es un placeholder! Genera una clave real para producción.")
   # Podrías generar una aquí para desarrollo si quieres, o lanzar un error.
   # from cryptography.fernet import Fernet
   # key = Fernet.generate_key()
   # print(f"Clave Fernet generada (para .env): {key.decode()}")
   # Descomentar para detener si no hay clave real (más seguro)
   # raise ValueError("¡ENCRYPTION_KEY debe ser generada y configurada en .env!")

if settings.SECRET_KEY == "default_super_secret_key_change_me":
    print("ADVERTENCIA: ¡La SECRET_KEY de JWT es un placeholder! Genera una clave real para producción.")
    # Descomentar para detener si no hay clave real (más seguro)
    # raise ValueError("¡SECRET_KEY debe ser generada y configurada en .env!")