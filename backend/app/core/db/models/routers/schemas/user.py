from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid # Si usas UUID como ID
from datetime import datetime

# --- Esquemas Base ---
class UserBase(BaseModel):
    email: EmailStr # Pydantic valida que sea un email válido

# --- Esquemas para Creación ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=8) # Requiere contraseña con mínimo 8 caracteres

# --- Esquemas para Lectura (Respuesta de API) ---
# Esquema básico solo con ID y Email
class UserReadBasic(UserBase):
    # id: uuid.UUID # Si usas UUID
    id: int # Si usas Integer

    class Config:
        # DeprecationWarning: orm_mode está deprecado, usar from_attributes=True
        # orm_mode = True
        from_attributes = True # Permite crear el esquema desde un objeto ORM (SQLAlchemy)

# Esquema completo con datos de perfil para devolver desde /users/me
class UserReadProfile(UserReadBasic):
    age: Optional[int] = None
    primary_goal: Optional[str] = None
    esg_interest: bool
    created_at: datetime
    updated_at: datetime

    # Config ya heredada de UserReadBasic

# --- Esquemas para Actualización ---
class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    primary_goal: Optional[str] = None
    esg_interest: Optional[bool] = None

    # Añadir validaciones si es necesario, ej. para age > 0

# --- Esquema Interno (si es necesario para dependencias) ---
# No es estrictamente necesario ahora mismo, pero podría ser útil más adelante
class UserInDBBase(UserBase):
    # id: uuid.UUID # Si usas UUID
    id: int # Si usas Integer
    hashed_password: str

    class Config:
        # orm_mode = True
        from_attributes = True