from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError # Importar Field y ValidationError
from dotenv import load_dotenv
import os
from typing import Optional

# Carga las variables del archivo .env en el entorno
# La ruta asume que .env está en la carpeta 'backend'
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
# print(f"DEBUG: Intentando cargar .env desde: {dotenv_path}") # Línea de depuración opcional
# print(f"DEBUG: DATABASE_URL leída: {os.getenv('DATABASE_URL')}") # Línea de depuración opcional

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

    # Seguridad JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_super_secret_key_change_me")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Clave de Encriptación Fernet (Debe ser de 32 bytes URL-safe base64 encoded)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "generate_a_real_32_byte_key_please") # Placeholder - ¡Generar una real!

    # Plaid API
    PLAID_CLIENT_ID: Optional[str] = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET_SANDBOX: Optional[str] = os.getenv("PLAID_SECRET_SANDBOX")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")

    # Hugging Face API
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")

    # Pydantic-settings cargará automáticamente desde variables de entorno.
    # La configuración de Config es opcional si las variables ya están en el entorno (gracias a load_dotenv)
    # class Config:
    #    env_file = dotenv_path
    #    env_file_encoding = 'utf-8'
    #    extra = 'ignore' # Ignorar variables extra en .env

# Crear una instancia de la configuración para usarla en la aplicación
try:
    settings = Settings()
    # print("DEBUG: Configuración cargada exitosamente.") # Línea de depuración opcional
except ValidationError as e:
    print(f"ERROR: Error al validar la configuración: {e}")
    # Decide cómo manejar el error, p.ej., salir o usar valores por defecto más seguros
    raise e # Volver a lanzar la excepción para detener la ejecución si es crítico

# Validación y advertencias para claves placeholder
if settings.SECRET_KEY == "default_super_secret_key_change_me":
    print("
ADVERTENCIA: La SECRET_KEY de JWT es un placeholder inseguro.")
    print("             Genera una clave segura (ej. openssl rand -hex 32) y configúrala en .env.
")
    # Considera lanzar un error en producción:
    # raise ValueError("¡SECRET_KEY debe ser configurada con un valor seguro en .env!")

if settings.ENCRYPTION_KEY == "generate_a_real_32_byte_key_please":
    print("
ADVERTENCIA: La ENCRYPTION_KEY es un placeholder inseguro.")
    print("             Genera una clave Fernet (python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')")
    print("             y configúrala en .env.
")
    # Considera lanzar un error en producción:
    # raise ValueError("¡ENCRYPTION_KEY debe ser generada y configurada en .env!")

# Imprimir una versión segura de la configuración cargada (opcional)
# print(f"DEBUG: DATABASE_URL cargada: {settings.DATABASE_URL[:settings.DATABASE_URL.find('@') if '@' in settings.DATABASE_URL else None]}...")
# print(f"DEBUG: SECRET_KEY cargada: {settings.SECRET_KEY[:5]}...")
# print(f"DEBUG: ENCRYPTION_KEY cargada: {settings.ENCRYPTION_KEY[:5]}...")