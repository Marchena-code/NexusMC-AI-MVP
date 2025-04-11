import httpx
from typing import Optional, List
import os # Para getenv si no usas settings directamente

# Importar settings
# Asumiendo que este archivo está en app/services/
try:
    from ..core.config import settings
except ImportError:
    # Fallback si la estructura es diferente o para pruebas unitarias aisladas
    print("ADVERTENCIA: No se pudo importar settings desde ..core.config. Usando os.getenv directamente.")
    # Crear un objeto mock de settings si es necesario para que el código no falle
    class MockSettings:
        HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    settings = MockSettings()

# Categorías financieras objetivo para la clasificación
FINANCIAL_CATEGORIES: List[str] = [
    "Food and Drink",
    "Transportation",
    "Shopping",
    "Bills & Utilities",
    "Entertainment",
    "Housing",
    "Health & Wellness",
    "Education",
    "Income",
    "Transfers",
    "Fees & Charges",
    "Travel",
    "Personal Care",
    "Gifts & Donations",
    "Other"
]

# URL del modelo Zero-Shot recomendado en Hugging Face
HF_ZERO_SHOT_MODEL_URL = os.getenv("HF_MODEL_URL", "https://api-inference.huggingface.co/models/facebook/bart-large-mnli")
# Alternativa (más pequeño/rápido, potencialmente menos preciso):
# HF_ZERO_SHOT_MODEL_URL = "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"

# Límite de reintentos o timeout
REQUEST_TIMEOUT = 15.0 # Segundos

async def categorize_transaction(description: str) -> str:
    """
    Categoriza una descripción de transacción usando un modelo Zero-Shot de Hugging Face.

    Args:
        description: El texto de la descripción de la transacción.

    Returns:
        La categoría predicha (str). Devuelve "Other" si falla la categorización/configuración.
    """
    api_key = settings.HUGGINGFACE_API_KEY

    if not api_key:
        print("ADVERTENCIA: HUGGINGFACE_API_KEY no configurada. Devolviendo categoría 'Other'.")
        return "Other"
    
    if not description or not isinstance(description, str) or len(description.strip()) == 0:
        print("ADVERTENCIA: Descripción de transacción inválida o vacía. Devolviendo categoría 'Other'.")
        return "Other"

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": description,
        "parameters": {
            "candidate_labels": FINANCIAL_CATEGORIES,
            "multi_label": False # Asumimos una sola categoría por transacción
            },
        "options": {"wait_for_model": True} # Esperar a que el modelo esté listo
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(HF_ZERO_SHOT_MODEL_URL, headers=headers, json=payload)
            
            # Debugging de la respuesta
            # print(f"DEBUG HF Status: {response.status_code}")
            # print(f"DEBUG HF Response: {response.text}")
            
            response.raise_for_status() # Lanza excepción para errores HTTP 4xx/5xx

            result = response.json()
            if result and isinstance(result, dict) and 'labels' in result and 'scores' in result and result['labels']:
                # El modelo devuelve las etiquetas ordenadas por puntuación descendente
                best_category = result['labels'][0]
                best_score = result['scores'][0]
                # print(f"DEBUG: Categoría predicha para '{description}': {best_category} (Score: {best_score:.2f})")
                
                # Asegurarse de que la categoría devuelta esté en nuestra lista (por si acaso)
                if best_category in FINANCIAL_CATEGORIES:
                    return best_category
                else:
                    print(f"ADVERTENCIA: Categoría predicha '{best_category}' no está en FINANCIAL_CATEGORIES. Devolviendo 'Other'.")
                    return "Other"
            else:
                print(f"ADVERTENCIA: Respuesta inesperada o vacía de HF API para '{description}'. Respuesta: {result}")
                return "Other"

    except httpx.HTTPStatusError as e:
        # Manejar errores específicos como 401 (Unauthorized), 503 (Model loading), etc.
        print(f"ERROR: HTTP {e.response.status_code} de Hugging Face API para '{description}'. Respuesta: {e.response.text}")
        return "Other"
    except httpx.RequestError as e:
        # Errores de red, timeout, etc.
        print(f"ERROR: Error de red al contactar Hugging Face API para '{description}': {e}")
        return "Other"
    except Exception as e:
        # Otros errores inesperados (ej. JSONDecodeError)
        import traceback
        print(f"ERROR: Error inesperado durante la categorización IA para '{description}': {e}")
        traceback.print_exc() # Imprimir traceback completo para depuración
        return "Other" 