from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date # Usar date para fechas sin hora

# Esquema para la respuesta del link_token
class PlaidLinkTokenResponse(BaseModel):
    link_token: str

# Esquema para recibir el public_token del frontend
class PlaidSetAccessTokenRequest(BaseModel):
    public_token: str

# Esquema para la respuesta al establecer el access_token (simple)
class PlaidSetAccessTokenResponse(BaseModel):
    message: str = "Access token set successfully"
    item_id: Optional[str] = None # Opcional: devolver el item_id

# Esquema para representar una transacción individual de Plaid (simplificado)
class PlaidTransaction(BaseModel):
    transaction_id: str
    account_id: str
    date: date # Usar date para la fecha de la transacción
    name: str
    amount: float # El monto de la transacción
    # La categoría de Plaid es una jerarquía, la simplificamos a una lista opcional
    category: Optional[List[str]] = None
    pending: bool

    class Config:
        from_attributes = True # Para crear desde objetos de la librería Plaid

# Esquema para la respuesta del endpoint de transacciones
class PlaidTransactionResponse(BaseModel):
    transactions: List[PlaidTransaction]
    # Podríamos añadir más info si fuera necesario, como detalles de cuenta
    account_name: Optional[str] = None # Ejemplo 