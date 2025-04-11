from pydantic import BaseModel, EmailStr, Field
from typing import Optional
# import uuid # Si usas UUID como ID
from datetime import datetime

# --- Esquemas Base ---
class UserBase(BaseModel):
    email: EmailStr # Valida formato email

# --- Esquemas para Creación ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=8) # Campo requerido, min 8 chars

# --- Esquemas para Lectura (Respuesta de API) ---
class UserReadBasic(UserBase):
    # id: uuid.UUID # Si usas UUID
    id: int # Si usas Integer

    class Config:
        from_attributes = True # Permite crear desde objeto SQLAlchemy

class UserReadProfile(UserReadBasic):
    age: Optional[int] = None
    primary_goal: Optional[str] = None
    esg_interest: bool
    created_at: datetime
    updated_at: datetime

    # Config ya heredada de UserReadBasic

# --- Esquemas para Actualización ---
class UserProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, gt=0) # Opcional, mayor que 0 si se provee
    primary_goal: Optional[str] = None
    esg_interest: Optional[bool] = None

# --- Esquema Interno (No estrictamente necesario ahora) ---
# class UserInDBBase(UserBase):
#     id: int
#     hashed_password: str
#     class Config:
#         from_attributes = True