from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Importar la configuración desde la nueva ubicación
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

print(f"SQLAlchemy Engine creado para URL: {SQLALCHEMY_DATABASE_URL[:SQLALCHEMY_DATABASE_URL.find('@')] + '@...masked...'}") # Imprime URL enmascarada al iniciar