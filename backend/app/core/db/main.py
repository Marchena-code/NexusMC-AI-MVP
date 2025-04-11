from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importar routers más adelante cuando los creemos
# from .routers import auth, users, plaid, dashboard, investment, ia

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title="NexusMC AI API",
    description="API para la plataforma NexusMC AI - MVP",
    version="0.1.0",
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Permite que el frontend (ej. ejecutándose en localhost:3000)
# se comunique con el backend (ej. ejecutándose en localhost:8000)
origins = [
    "http://localhost",       # Origen común para desarrollo local
    "http://localhost:8080",  # Otro puerto común de desarrollo frontend
    "http://localhost:3000",  # Puerto común para React
    # Añadir aquí la URL del frontend desplegado en el futuro
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de orígenes permitidos
    allow_credentials=True, # Permite cookies (si las usas)
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todas las cabeceras
)

# --- Incluir Routers ---
# Descomentar e incluir cada router a medida que los creemos
# app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(plaid.router, prefix="/plaid", tags=["Plaid"])
# app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
# app.include_router(investment.router, prefix="/investment", tags=["Investment"])
# app.include_router(ia.router, prefix="/ia", tags=["AI"])


# --- Endpoint Raíz (Prueba) ---
@app.get("/")
async def read_root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {"message": "NexusMC AI Backend is running!"}

# --- Ejecutar con Uvicorn (para desarrollo local) ---
# Puedes ejecutar desde la terminal con: uvicorn app.main:app --reload --port 8000
# El flag --reload hace que el servidor se reinicie automáticamente con los cambios.