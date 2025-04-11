from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para valores por defecto como now()
from app.db.database import Base
# import uuid # Descomentar si usas UUID
# from sqlalchemy.dialects.postgresql import UUID # Específico para PostgreSQL UUID

class User(Base):
    __tablename__ = "users"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Opción con UUID
    id = Column(Integer, primary_key=True, index=True) # Opción con Integer

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Campos de Perfil
    age = Column(Integer, nullable=True)
    primary_goal = Column(String, nullable=True)
    esg_interest = Column(Boolean, default=False, nullable=False)

    # Campos Plaid
    plaid_access_token_encrypted = Column(LargeBinary, nullable=True) # Almacena bytes encriptados
    plaid_item_id = Column(String, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Ejemplo relación (si hubiera una tabla 'items'):
    # items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"