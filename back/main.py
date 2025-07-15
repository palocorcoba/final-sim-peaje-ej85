from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from simulation.simulator import simular
from simulation.config import CONFIG
from config_schemas import ConfigPeaje  # lo creás aparte

app = FastAPI()

# CORS para permitir conexiones desde el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Podés restringir esto a tu frontend (ej: ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/simular")
def ejecutar_simulacion(
    n_iteraciones: int = 1000,
    desde: int = 1,
    hasta: int = 100,
    media_llegadas: float = 1.2,
    max_cabinas: int = 4,
    max_autos_por_cola: int = 4,
    prob_tipo1: float = 0.1,
    prob_tipo2: float = 0.5,
    prob_tipo3: float = 0.15,
    prob_tipo4: float = 0.15,
    prob_tipo5: float = 0.1,
    monto_tipo1: int = 0,
    monto_tipo2: int = 3,
    monto_tipo3: int = 6,
    monto_tipo4: int = 9,
    monto_tipo5: int = 12,
    tiempo_tipo1: float = 0.5,
    tiempo_tipo2_a: float = 0.75,
    tiempo_tipo2_b: float = 0.92,
    tiempo_tipo3_a: float = 0.92,
    tiempo_tipo3_b: float = 1.42,
    tiempo_tipo4_a: float = 1.5,
    tiempo_tipo4_b: float = 2.17,
    tiempo_tipo5_a: float = 2.5,
    tiempo_tipo5_b: float = 3.5,
):
    config_simulacion = {
        "media_llegadas": media_llegadas,
        "max_cabinas": max_cabinas,
        "max_autos_por_cola": max_autos_por_cola,
        "tipos_autos": [
            {"tipo": 1, "probabilidad": prob_tipo1, "tiempo_atencion": tiempo_tipo1, "tarifa": monto_tipo1},
            {"tipo": 2, "probabilidad": prob_tipo2, "tiempo_atencion": [tiempo_tipo2_a, tiempo_tipo2_b], "tarifa": monto_tipo2},
            {"tipo": 3, "probabilidad": prob_tipo3, "tiempo_atencion": [tiempo_tipo3_a, tiempo_tipo3_b], "tarifa": monto_tipo3},
            {"tipo": 4, "probabilidad": prob_tipo4, "tiempo_atencion": [tiempo_tipo4_a, tiempo_tipo4_b], "tarifa": monto_tipo4},
            {"tipo": 5, "probabilidad": prob_tipo5, "tiempo_atencion": [tiempo_tipo5_a, tiempo_tipo5_b], "tarifa": monto_tipo5},
        ]
    }

    resultado = simular(
        n_iteraciones=n_iteraciones,
        mostrar_desde=desde,
        mostrar_hasta=hasta,
        config=config_simulacion
    )
    return resultado

@app.get("/ping")
def ping():
    """
    Endpoint para verificar que el servidor está activo.
    """
    return {"message": "pong"}

@app.get("/config", response_model=ConfigPeaje)
def obtener_config():
    return {
        "media_llegadas": CONFIG["media_llegadas"],
        "tipos_autos": CONFIG["tipos_autos"]
    }

@app.post("/config")
def actualizar_config(nueva_config: ConfigPeaje):
    if len(nueva_config.tipos_autos) != 5:
        raise HTTPException(status_code=400, detail="Debe haber 5 tipos de autos")

    suma_probabilidades = sum(t.probabilidad for t in nueva_config.tipos_autos)
    if abs(suma_probabilidades - 1.0) > 0.01:
        raise HTTPException(status_code=400, detail="La suma de probabilidades debe ser 1")

    CONFIG["media_llegadas"] = nueva_config.media_llegadas
    CONFIG["tipos_autos"] = [t.dict() for t in nueva_config.tipos_autos]
    return {"status": "Configuración actualizada correctamente"}
