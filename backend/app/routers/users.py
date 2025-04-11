from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any # Para el diccionario en PUT

# Importaciones relativas
# Usaremos __init__.py para simplificar si existen
from .. import models
from .. import schemas
# O importa directamente:
# from ..models.user import User
# from ..schemas.user import UserReadProfile, UserProfileUpdate
from ..db.database import get_db
from ..core.security import get_current_user

router = APIRouter()

# --- Endpoint para obtener el perfil del usuario actual ---
@router.get("/me", response_model=schemas.user.UserReadProfile)
async def read_users_me(current_user: models.user.User = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario actualmente autenticado.
    """
    # Pydantic se encarga de convertir el objeto User de SQLAlchemy
    # al esquema UserReadProfile gracias a 'from_attributes=True' en el esquema.
    return current_user

# --- Endpoint para actualizar el perfil del usuario actual ---
@router.put("/me", response_model=schemas.user.UserReadProfile)
async def update_user_me(
    user_update: schemas.user.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Actualiza el perfil del usuario actualmente autenticado.
    Solo actualiza los campos proporcionados en el request body.
    """
    # Obtiene los datos del request que el usuario realmente envió (no los defaults)
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        # Si no se envió ningún dato para actualizar, podemos devolver un 304 o el usuario actual
        # Opcionalmente, lanzar un error 400 si se espera algún dato.
        # Devolver el usuario actual es seguro.
        # print("DEBUG: No update data provided for /users/me PUT")
        return current_user

    # Itera sobre los datos proporcionados y actualiza el objeto usuario
    updated_fields = False
    for key, value in update_data.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value) # Actualiza el atributo en el objeto SQLAlchemy
            updated_fields = True
        # else: # Opcional: Log si se envía un campo no existente en el modelo
            # print(f"Advertencia: Campo '{key}' no encontrado en el modelo User.")

    if not updated_fields:
        # Esto podría pasar si todos los campos enviados no existen en el modelo
        # Considera devolver un error 400 o simplemente el usuario sin cambios.
        return current_user

    # Guarda los cambios en la base de datos
    db.add(current_user) # Añade el objeto modificado a la sesión
    try:
        db.commit()      # Confirma la transacción
        db.refresh(current_user) # Refresca el objeto con datos de la BD (ej. updated_at)
    except Exception as e:
        db.rollback()
        print(f"Error al actualizar perfil de usuario {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update user profile."
        )

    return current_user 