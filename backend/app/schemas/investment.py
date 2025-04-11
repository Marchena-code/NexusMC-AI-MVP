from pydantic import BaseModel
from typing import Optional, List

class ESGInvestmentInfo(BaseModel):
    fundName: str
    tickerSymbol: str # Ficticio para demo
    description: str
    keyMetricLabel: str # Ej: "Rentabilidad Anualizada (5 Años - Ejemplo)"
    keyMetricValue: str # Ej: "11.5%"
    esgFocus: List[str] # Ej: ["Energía Limpia", "Gobierno Corporativo"]
    disclaimer: str # **IMPORTANTE** Aclarar que es demo

class InvestmentDemoData(BaseModel):
    esg_info_active: bool # Indica si el usuario marcó interés ESG
    fondo_esg_demo: Optional[ESGInvestmentInfo] = None # Datos del fondo si esg_info_active es True
    insight_inversion: str # El insight genérico generado 