from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importar routers
from .routers import auth, users # <<<--- IMPORTAR ROUTER USERS
# from .routers import plaid, dashboard, investment, ia # Rutas relativas a 'app'

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title="NexusMC AI API",
    description="API para la plataforma NexusMC AI - MVP",
    version="0.1.0", # Versión inicial
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Permite que el frontend (ej. ejecutándose en localhost:3000)
# se comunique con el backend (ej. ejecutándose en localhost:8000)
origins = [
    "http://localhost",       # Base localhost
    "http://localhost:8080",  # Puerto común dev frontend
    "http://localhost:3000",  # Puerto común React
    "http://localhost:19006", # Puerto común Expo Web
    # Añadir aquí la URL del frontend desplegado en el futuro si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de orígenes permitidos
    allow_credentials=True, # Permite cookies/auth headers
    allow_methods=["*"],    # Permite todos los métodos HTTP
    allow_headers=["*"],    # Permite todas las cabeceras HTTP
)

# --- Incluir Routers --- 
# Asegúrate de que los archivos de router existan en app/routers/
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"]) # <<<--- ACTIVAR ESTA LÍNEA
# app.include_router(plaid.router, prefix="/plaid", tags=["Plaid"])
# app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
# app.include_router(investment.router, prefix="/investment", tags=["Investment"])
# app.include_router(ia.router, prefix="/ia", tags=["AI"])


# --- Endpoint Raíz (Prueba de Salud) ---
@app.get("/")
async def read_root():
    """
    Endpoint raíz para verificar rápidamente que la API está activa.
    """
    return {"message": "NexusMC AI Backend is running!"}

# --- Ejecutar con Uvicorn ---
# Desde la terminal, dentro de la carpeta 'backend' (con venv activado):
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# --reload: Reinicia automáticamente al guardar cambios.
# --host 0.0.0.0: Permite acceso desde fuera de localhost (útil para emulador/dispositivo físico).
# --port 8000: Puerto estándar para APIs.