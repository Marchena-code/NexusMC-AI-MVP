from pydantic import BaseModel
from typing import Dict, Optional, List

class DashboardData(BaseModel):
    balance_simulado: float # O usar Optional[float] = None
    gasto_categorias: Dict[str, float] # Ej: {"Comida": 150.20, "Transporte": 80.0}
    insight_ahorro: str
    tip_dia: str
    # Opcional: añadir lista de transacciones recientes si se quiere mostrar
    # transacciones_recientes: Optional[List[PlaidTransaction]] = None # Requeriría importar PlaidTransaction 