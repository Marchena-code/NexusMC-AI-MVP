import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

# Intentar importar Plaid y manejar si no está instalado (aunque lo instalamos)
try:
    import plaid
    from plaid.api import plaid_api
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.transactions_sync_request import TransactionsSyncRequest
    # Alternativa a Sync:
    # from plaid.model.transactions_get_request import TransactionsGetRequest
    # from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    from plaid.exceptions import ApiException
except ImportError:
    print("ERROR CRÍTICO: La librería 'plaid-python' no está instalada.")
    # Marcar Plaid como no disponible
    plaid = None
    ApiException = Exception # Usar excepción genérica para los catch
    plaid_api = None # Placeholder

# Importaciones relativas
from .. import models
from .. import schemas
from ..db.database import get_db
from ..core.config import settings
from ..core.security import get_current_user, encrypt_data, decrypt_data

router = APIRouter()

# --- Configuración del Cliente Plaid --- 
# Productos que usaremos (pueden variar según tu caso de uso)
PLAID_PRODUCTS = [Products(p) for p in os.getenv("PLAID_PRODUCTS", "transactions").split(',')]
# Países soportados (ej. solo US para empezar)
PLAID_COUNTRY_CODES = [CountryCode(c) for c in os.getenv("PLAID_COUNTRY_CODES", "US").split(',')]
# Ambiente Plaid (Sandbox, Development, Production)
PLAID_ENV = getattr(plaid.Environment, settings.PLAID_ENV.capitalize(), plaid.Environment.Sandbox)

# Función auxiliar o dependencia para obtener el cliente API
def get_plaid_client():
    # Verificar si la librería Plaid se importó correctamente
    if plaid is None or plaid_api is None:
        print("ADVERTENCIA: Librería Plaid no disponible.")
        return None

    # Verificar credenciales
    if not settings.PLAID_CLIENT_ID or not settings.PLAID_SECRET_SANDBOX:
        print("ADVERTENCIA: Credenciales de Plaid Sandbox no configuradas en .env")
        return None # Devolver None para indicar que no está configurado

    try:
        configuration = plaid.Configuration(
            host=PLAID_ENV,
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET_SANDBOX, # Usar sandbox para MVP
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        # print(f"DEBUG: Cliente Plaid inicializado para el entorno: {PLAID_ENV}") # Debug
        return client
    except Exception as e:
        print(f"ERROR: No se pudo inicializar el cliente Plaid: {e}")
        return None

# --- Endpoints ---

@router.post("/create_link_token", response_model=schemas.plaid.PlaidLinkTokenResponse)
async def create_link_token(
    current_user: models.user.User = Depends(get_current_user),
    client: Optional[plaid_api.PlaidApi] = Depends(get_plaid_client) # Hacer opcional
):
    """
    Crea un link_token para inicializar Plaid Link en el frontend.
    """
    if client is None:
        print("DEBUG: create_link_token - Cliente Plaid no disponible.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plaid service is not configured or available."
        )

    try:
        request = LinkTokenCreateRequest(
            client_name="NexusMC AI",
            language='en', # o 'es'
            country_codes=PLAID_COUNTRY_CODES,
            user=LinkTokenCreateRequestUser(
                client_user_id=str(current_user.id) # ID único y estable
            ),
            products=PLAID_PRODUCTS,
            # webhook='https://YOUR_BACKEND_WEBHOOK_URL/plaid-webhook' # Añadir si usas webhooks
        )
        response = client.link_token_create(request)
        return schemas.plaid.PlaidLinkTokenResponse(link_token=response['link_token'])

    except ApiException as e:
        print(f"Error de Plaid API al crear link_token: {e.body}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create Plaid link token.")
    except Exception as e:
        print(f"Error inesperado al crear link_token: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error creating Plaid link token.")

@router.post("/set_access_token", response_model=schemas.plaid.PlaidSetAccessTokenResponse)
async def set_access_token(
    request_body: schemas.plaid.PlaidSetAccessTokenRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user),
    client: Optional[plaid_api.PlaidApi] = Depends(get_plaid_client)
):
    """
    Intercambia un public_token por un access_token y lo guarda encriptado.
    """
    if client is None:
        print("DEBUG: set_access_token - Cliente Plaid no disponible.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Plaid service not configured or available.")

    public_token = request_body.public_token
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        encrypted_access_token = encrypt_data(access_token)
        if not encrypted_access_token:
            print(f"ERROR CRÍTICO: Falla al encriptar access_token para usuario {current_user.id}")
            raise HTTPException(status_code=500, detail="Failed to secure access token due to encryption error.")

        current_user.plaid_access_token_encrypted = encrypted_access_token
        current_user.plaid_item_id = item_id
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return schemas.plaid.PlaidSetAccessTokenResponse(item_id=item_id)

    except ApiException as e:
        # Imprimir más detalles del error de API
        body_detail = e.body if hasattr(e, 'body') else str(e)
        print(f"Error de Plaid API al intercambiar token: status={e.status}, body={body_detail}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not exchange public token: {body_detail}")
    except Exception as e:
        db.rollback() # Asegurar rollback si la encriptación o commit fallan
        print(f"Error inesperado al guardar access token para usuario {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process access token.")


@router.get("/transactions", response_model=schemas.plaid.PlaidTransactionResponse)
async def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user),
    client: Optional[plaid_api.PlaidApi] = Depends(get_plaid_client)
):
    """
    Obtiene las transacciones recientes del usuario usando el access_token guardado.
    Usa datos mock si no hay token o si hay errores.
    """
    if client is None:
        print("ADVERTENCIA: get_transactions - Cliente Plaid no disponible. Devolviendo datos MOCK.")
        return create_mock_transactions_response()

    encrypted_token = current_user.plaid_access_token_encrypted
    if not encrypted_token:
        print(f"ADVERTENCIA: Usuario {current_user.id} no tiene token Plaid. Devolviendo datos MOCK.")
        return create_mock_transactions_response()

    access_token = decrypt_data(encrypted_token)
    if not access_token:
        print(f"ERROR: Falla al desencriptar token para usuario {current_user.id}. Devolviendo datos MOCK.")
        # Podríamos lanzar un error 500, pero devolver mocks puede ser mejor para MVP
        return create_mock_transactions_response()

    try:
        # Usar Transactions Sync para obtener cambios desde la última sincronización
        # o todas las transacciones si es la primera vez (cursor=None)
        # Para simplicidad en MVP, pediremos siempre las últimas transacciones
        # (requiere más lógica de cursor para ser eficiente en producción)
        request = TransactionsSyncRequest(access_token=access_token)
        response = client.transactions_sync(request)

        # La respuesta contiene 'added', 'modified', 'removed'. Procesamos 'added'.
        transactions_data = response.get('added', [])

        # --- Alternativa: Transactions Get (rango de fechas) ---
        # start_date = (datetime.date.today() - datetime.timedelta(days=30))
        # end_date = datetime.date.today()
        # request = TransactionsGetRequest(
        #     access_token=access_token,
        #     start_date=start_date,
        #     end_date=end_date,
        # )
        # response = client.transactions_get(request)
        # transactions_data = response.get('transactions', [])
        # --- Fin Alternativa ---

        transactions_list: List[schemas.plaid.PlaidTransaction] = []
        for t_dict in transactions_data:
            try:
                # Asegurarse de que los nombres de campo coincidan
                # Plaid puede devolver campos adicionales, Pydantic los ignora por defecto
                transactions_list.append(schemas.plaid.PlaidTransaction.model_validate(t_dict))
            except Exception as validation_error:
                print(f"Error validando transacción de Plaid: {validation_error}, Datos: {t_dict}")
                continue # Omitir transacción inválida

        # Obtener nombre de cuenta (simplificado)
        account_name = "Linked Account (Plaid)" # Placeholder
        # En una app real: client.accounts_get(AccountsGetRequest(access_token=access_token))

        return schemas.plaid.PlaidTransactionResponse(
            transactions=transactions_list,
            account_name=account_name
        )

    except ApiException as e:
        body_detail = e.body if hasattr(e, 'body') else str(e)
        print(f"Error de Plaid API al obtener transacciones para user {current_user.id}: status={e.status}, body={body_detail}")
        # Manejar errores comunes como ITEM_LOGIN_REQUIRED, etc.
        if e.status == 400: # Podría ser un token inválido
             print("ADVERTENCIA: Error 400 de Plaid (posible token inválido). Devolviendo datos MOCK.")
             return create_mock_transactions_response()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not retrieve transactions: {body_detail}")
    except Exception as e:
        print(f"Error inesperado al obtener transacciones para user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve transaction data.")

# Función auxiliar para datos mock
def create_mock_transactions_response():
    """Genera una respuesta mock para /transactions."""
    mock_transactions = [
         schemas.plaid.PlaidTransaction(transaction_id="mock_1", account_id="mock_acc", date=datetime.date.today() - datetime.timedelta(days=1), name="Mock Cafe Visit", amount=12.50, category=["Food and Drink", "Restaurants"], pending=False),
         schemas.plaid.PlaidTransaction(transaction_id="mock_2", account_id="mock_acc", date=datetime.date.today() - datetime.timedelta(days=2), name="Mock Subway Card", amount=35.00, category=["Travel", "Public Transportation"], pending=False),
         schemas.plaid.PlaidTransaction(transaction_id="mock_3", account_id="mock_acc", date=datetime.date.today() - datetime.timedelta(days=3), name="Mock Salary Deposit", amount=-500.00, category=["Transfer", "Payroll"], pending=False), # Ingreso
    ]
    return schemas.plaid.PlaidTransactionResponse(transactions=mock_transactions, account_name="Mock Linked Account") 