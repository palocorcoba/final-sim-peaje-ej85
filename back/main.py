from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from simulation.simulator import simular

app = FastAPI()

# CORS para permitir conexiones desde el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # podés cambiar esto por "http://localhost:3000" si querés limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/simular")
def ejecutar_simulacion(n_iteraciones: int = 1000, desde: int = 0, hasta: int = 100):
    """
    Ejecuta la simulación y devuelve las iteraciones solicitadas.
    - n_iteraciones: cuántas iteraciones simular (máx 100000).
    - desde: desde qué iteración mostrar.
    - hasta: hasta qué iteración mostrar.
    """
    resultado = simular(
        n_iteraciones=n_iteraciones,
        mostrar_desde=desde,
        mostrar_hasta=hasta
    )
    return resultado

@app.get("/ping")
def ping():
    """
    Endpoint para verificar que el servidor está activo.
    """
    return {"message": "pong"}