from sqlalchemy import create_engine
# Cambio: importar Base de sqlalchemy.orm directamente si no usas legacy
# from sqlalchemy.ext.declarative import declarative_base # Comentado como en la instrucción
from sqlalchemy.orm import sessionmaker, declarative_base
# Corregir la importación para que sea absoluta desde la nueva estructura
from app.core.config import settings 

# Crear la URL de conexión usando la configuración
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Crear el motor de SQLAlchemy
# 'connect_args' puede ser necesario para SQLite, pero usualmente no para PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # Si usaras SQLite: , connect_args={"check_same_thread": False}
)

# Crear una fábrica de sesiones (SessionLocal)
# autocommit=False y autoflush=False son configuraciones estándar para APIs web
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase Base para nuestros modelos ORM
Base = declarative_base()

# --- Dependencia de FastAPI para obtener la sesión de BD ---
def get_db():
    """
    Dependencia de FastAPI que crea y gestiona una sesión de base de datos
    para cada solicitud.
    """
    db = SessionLocal()
    try:
        yield db # Proporciona la sesión a la ruta
    finally:
        db.close() # Cierra la sesión después de que la solicitud termine

# Enmascarar contraseña antes de imprimir
try:
    masked_url_parts = SQLALCHEMY_DATABASE_URL.split('@')
    if len(masked_url_parts) > 1:
        user_part = masked_url_parts[0].split('//')[-1].split(':')[0]
        host_part = masked_url_parts[1]
        masked_url = f"postgresql://{user_part}:***@{host_part}"
    else:
        masked_url = SQLALCHEMY_DATABASE_URL # No parece tener formato user:pass@host
except Exception:
    masked_url = "[Error al enmascarar URL]"

print(f"DEBUG: SQLAlchemy Engine creado para URL: {masked_url}") # Imprime URL enmascarada al iniciar