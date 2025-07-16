import random

# Configuración general de la simulación
CONFIG = {
    "media_llegadas": 1.2,
    "max_cabinas": 4,
    "max_autos_por_cola": 4,
    "tipos_autos": [
        {"tipo": 1, "probabilidad": 0.10, "tiempo_atencion": [0.5], "tarifa": 0},
        {"tipo": 2, "probabilidad": 0.50, "tiempo_atencion": [0.75, 0.92], "tarifa": 3},
        {"tipo": 3, "probabilidad": 0.15, "tiempo_atencion": [0.92, 1.42], "tarifa": 6},
        {"tipo": 4, "probabilidad": 0.15, "tiempo_atencion": [1.50, 2.17], "tarifa": 9},
        {"tipo": 5, "probabilidad": 0.10, "tiempo_atencion": [2.50, 3.50], "tarifa": 12},
    ]
}

def obtener_tiempo_atencion(tipo: int, config=None):
    if config is None:
        config = CONFIG
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        raise ValueError(f"Tipo {tipo} no encontrado")

    tiempo = tipo_data["tiempo_atencion"]
    if len(tiempo) == 1:
        return tiempo[0]
    else:
        return tiempo[0] + random.random() * (tiempo[1] - tiempo[0])
