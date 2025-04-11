from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # Usamos email como 'subject' (sub) en nuestro token JWT
    email: Optional[EmailStr] = None 