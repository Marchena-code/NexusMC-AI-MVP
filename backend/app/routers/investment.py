from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, List # Añadir List

# Importaciones relativas
from .. import models
from .. import schemas
# No necesitamos get_db aquí si no consultamos la BD directamente
# from ..db.database import get_db
from ..core.security import get_current_user

router = APIRouter()

# --- Datos Estáticos para la Demo ESG ---
# Define los datos aquí o cárgalos desde un archivo de configuración si prefieres
ESG_DEMO_DATA: Dict = {
    "fundName": "EcoFuture Leaders Fund (DEMO)",
    "tickerSymbol": "EFLFX",
    "description": "Invierte en empresas globales líderes en innovación sostenible y prácticas éticas. (Datos ilustrativos).",
    "keyMetricLabel": "Rentabilidad Anualizada (5 Años - Ejemplo)",
    "keyMetricValue": "11.5%",
    "esgFocus": ["Energía Limpia", "Gobierno Corporativo", "Impacto Social"],
    "disclaimer": "**DATOS SÓLO PARA FINES DEMOSTRATIVOS. NO ES UNA RECOMENDACIÓN DE INVERSIÓN.**"
}

@router.get("/demo_data", response_model=schemas.investment.InvestmentDemoData)
async def get_investment_demo_data(
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Obtiene datos demostrativos para la sección de inversión,
    incluyendo información ESG si el usuario está interesado.
    """

    # 1. Generar Insight de Inversión Genérico (Basado en Reglas Simples)
    insight_inversion = "Una cartera diversificada es clave para el crecimiento a largo plazo. Considera tu tolerancia al riesgo."
    # Usar el perfil del usuario (si existe) para personalizar el insight
    age = getattr(current_user, 'age', None) # Obtener edad de forma segura
    if age:
        if age < 35:
            insight_inversion = "Con un horizonte de tiempo largo, podrías considerar una mayor exposición a activos de crecimiento como acciones. (Ejemplo ilustrativo)."
        elif age < 55:
            insight_inversion = "Balancear crecimiento y preservación de capital es importante. Revisa tu asignación de activos periódicamente. (Ejemplo ilustrativo)."
        else:
            insight_inversion = "En esta etapa, priorizar la preservación del capital y considerar inversiones que generen ingresos puede ser prudente. (Ejemplo ilustrativo)."

    # 2. Preparar Datos ESG si aplica
    fondo_esg_info: Optional[schemas.investment.ESGInvestmentInfo] = None
    esg_active = getattr(current_user, 'esg_interest', False) # Obtener interés ESG
    if esg_active:
        # Crear el objeto Pydantic desde el diccionario estático
        try:
            fondo_esg_info = schemas.investment.ESGInvestmentInfo(**ESG_DEMO_DATA)
        except Exception as e:
            print(f"ERROR: Error creando objeto ESG Demo Data: {e}")
            # Continuar sin los datos ESG si hay un error inesperado

    # 3. Construir la Respuesta
    response_data = schemas.investment.InvestmentDemoData(
        esg_info_active=esg_active,
        fondo_esg_demo=fondo_esg_info,
        insight_inversion=insight_inversion
    )

    return response_data 