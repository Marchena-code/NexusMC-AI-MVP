import random
import asyncio # Para llamar a la función async de categorización
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

# Importaciones relativas
from .. import models
from .. import schemas
from ..db.database import get_db
from ..core.security import get_current_user
from ..services.ia_service import categorize_transaction
# Necesitamos una forma de obtener transacciones. Importamos la función de plaid.py
# y su esquema de respuesta para usarlo.
from .plaid import get_transactions, create_mock_transactions_response
from ..schemas.plaid import PlaidTransactionResponse, PlaidTransaction

router = APIRouter()

# Lista de Tips Financieros
FINANCIAL_TIPS = [
    "Automatiza tus ahorros transfiriendo un % a una cuenta separada cada mes.",
    "Revisa tus suscripciones mensuales. ¿Realmente usas todas?",
    "Prioriza pagar las deudas con interés más alto primero (método avalancha).",
    "El interés compuesto es tu mejor amigo. Empieza a invertir temprano.",
    "Crea un presupuesto realista y síguelo. Usa la regla 50/30/20 como guía.",
    "Ten un fondo de emergencia que cubra 3-6 meses de gastos esenciales.",
    "Evita compras impulsivas esperando 24 horas antes de decidir.",
    "Compara precios antes de hacer compras grandes.",
    "Aprovecha descuentos y programas de lealtad.",
    "Invierte en tu educación financiera continuamente.",
]

@router.get("/data", response_model=schemas.dashboard.DashboardData)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Obtiene los datos agregados para el dashboard principal, incluyendo categorización IA.
    """
    try:
        # 1. Obtener transacciones (usará mock si Plaid no está listo/conectado)
        transaction_response: Optional[PlaidTransactionResponse] = None
        try:
            # Asumimos que get_transactions puede necesitar un cliente Plaid válido
            # Si get_transactions maneja internamente la contingencia mock, esto funcionará.
            # Si no, podríamos necesitar pasar get_plaid_client como dependencia aquí también.
            transaction_response = await get_transactions(db=db, current_user=current_user)
        except Exception as plaid_error:
            print(f"ERROR: Falla al obtener transacciones de Plaid: {plaid_error}. Usando mock.")
            # Si falla la obtención real, usamos el mock directamente
            transaction_response = create_mock_transactions_response()

        transactions = transaction_response.transactions if transaction_response else []

        # 2. Procesar transacciones y categorizar gastos ASINCRÓNICAMENTE
        gasto_categorias: Dict[str, float] = {}
        categorization_tasks = []

        # Crear tareas para categorizar todas las transacciones de gasto en paralelo
        for t in transactions:
            if t.amount > 0: # Gasto
                categorization_tasks.append(categorize_transaction(t.name))
            # Nota: No estamos almacenando la categoría en la transacción aquí,
            # solo agregando para el dashboard. Considerar almacenar en BD en el futuro.

        # Ejecutar todas las tareas de categorización en paralelo
        if categorization_tasks:
            print(f"DEBUG: Iniciando categorización para {len(categorization_tasks)} transacciones...")
            results = await asyncio.gather(*categorization_tasks)
            print(f"DEBUG: Categorización completada.")

            # Procesar los resultados
            task_index = 0
            for t in transactions:
                if t.amount > 0:
                    category = results[task_index]
                    if category and category not in ["Income", "Transfers", "Other"]:
                        gasto_categorias[category] = gasto_categorias.get(category, 0) + t.amount
                    task_index += 1
        else:
            print("DEBUG: No hay transacciones de gasto para categorizar.")


        # 3. Generar Insight de Ahorro (simple)
        insight_ahorro = "Aún no hay suficientes datos de gastos para generar un insight."
        if gasto_categorias:
            try:
                categoria_mayor_gasto = max(gasto_categorias, key=gasto_categorias.get)
                monto_mayor_gasto = gasto_categorias[categoria_mayor_gasto]
                insight_ahorro = f"Tu mayor área de gasto parece ser {categoria_mayor_gasto} (${monto_mayor_gasto:.2f}). ¡Una oportunidad para revisar!"
            except ValueError:
                # Esto no debería pasar si gasto_categorias no está vacío, pero por si acaso
                insight_ahorro = "Error al calcular el insight de gastos."

        # 4. Seleccionar Tip del Día
        tip_dia = random.choice(FINANCIAL_TIPS)

        # 5. Balance Simulado (Placeholder)
        # Idealmente, obtener de Plaid Assets o calcular sumando transacciones
        balance_simulado = 1234.56

        # 6. Devolver Datos
        return schemas.dashboard.DashboardData(
            balance_simulado=balance_simulado,
            gasto_categorias=gasto_categorias,
            insight_ahorro=insight_ahorro,
            tip_dia=tip_dia
        )

    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP que ya vienen de llamadas internas (ej. get_transactions)
        raise http_exc
    except Exception as e:
        print(f"ERROR CRÍTICO generando datos del dashboard: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not generate dashboard data due to an internal error: {e}"
        ) 