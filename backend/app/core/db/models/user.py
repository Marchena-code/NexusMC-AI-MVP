from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para valores por defecto como now()
from app.core.db.database import Base # Importar la Base de database.py (Usando import absoluto)
import uuid # Para generar IDs únicos si usamos UUID
from sqlalchemy.dialects.postgresql import UUID # Específico para PostgreSQL UUID

class User(Base):
    __tablename__ = "users"

    # Cambiar a UUID si se prefiere sobre Integer
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True, index=True) # Opción con Integer

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Campos de Perfil (Añadidos aquí para la migración inicial completa)
    age = Column(Integer, nullable=True)
    primary_goal = Column(String, nullable=True)
    esg_interest = Column(Boolean, default=False, nullable=False)

    # Campos Plaid (Añadidos aquí)
    # Usar LargeBinary para almacenar el token encriptado (bytes)
    # O String si prefieres guardar la versión base64 del token encriptado
    plaid_access_token_encrypted = Column(LargeBinary, nullable=True)
    plaid_item_id = Column(String, nullable=True, index=True) # El ID del item de Plaid

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Usar onupdate=func.now() si quieres que se actualice automáticamente
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Si tuviéramos relaciones, se definirían aquí. Ejemplo:
    # items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"