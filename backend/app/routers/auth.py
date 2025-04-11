from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importaciones relativas
# Necesitamos importar explícitamente los módulos o usar __init__.py
from .. import models
from .. import schemas
from ..db.database import get_db
from ..core import security # Importa el módulo de seguridad

router = APIRouter()

# --- Endpoint de Registro ---
@router.post("/register", response_model=schemas.user.UserReadBasic, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la base de datos.
    """
    # Verificar si el usuario ya existe
    db_user = db.query(models.user.User).filter(models.user.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hashear la contraseña
    hashed_password = security.get_password_hash(user.password)

    # Crear el nuevo usuario en la base de datos
    # Asegúrate de que el modelo User acepte estos campos directamente
    # o ajusta según tu inicializador si tienes uno
    new_user_data = user.model_dump(exclude={"password"}) # Excluir password plana
    new_user = models.user.User(**new_user_data, hashed_password=hashed_password)

    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user) # Refrescar para obtener el ID asignado por la BD
    except Exception as e:
        db.rollback() # Deshacer en caso de error
        print(f"Error al guardar usuario: {e}") # Log del error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user."
        )

    return new_user

# --- Endpoint de Login (Generación de Token) ---
@router.post("/token", response_model=schemas.token.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica al usuario y devuelve un token JWT.
    FastAPI espera que el cliente envíe 'username' y 'password' en un form-data.
    Usaremos el 'username' como el email.
    """
    user = db.query(models.user.User).filter(models.user.User.email == form_data.username).first()

    # Verificar si el usuario existe y la contraseña es correcta
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        # Log detallado opcional (sin exponer info sensible)
        # print(f"Intento de login fallido para email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token de acceso
    access_token = security.create_access_token(
        data={"sub": user.email} # Usar email como 'subject' del token
        # expires_delta puede ser omitido para usar el default de settings
    )

    return {"access_token": access_token, "token_type": "bearer"} 