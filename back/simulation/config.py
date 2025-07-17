import random

# Configuración general de la simulación
CONFIG = {
    "media_llegadas": 1.2,           # Media en minutos de la distribución exponencial de llegadas
    "max_cabinas": 4,                # Máximo número de cabinas que pueden habilitarse
    "max_autos_por_cola": 4,         # Máximo de autos permitidos en cola por cabina

     # Lista de tipos de autos definidos por:
    # - tipo: identificador (1 a 5)
    # - probabilidad: peso relativo en la generación aleatoria
    # - tiempo_atencion: duración de atención en minutos (puede ser un valor fijo o un rango)
    # - tarifa: monto a cobrar según el tipo

    "tipos_autos": [
        {"tipo": 1, "probabilidad": 0.10, "tiempo_atencion": [0.5], "tarifa": 0},
        {"tipo": 2, "probabilidad": 0.50, "tiempo_atencion": [0.75, 0.92], "tarifa": 3},
        {"tipo": 3, "probabilidad": 0.15, "tiempo_atencion": [0.92, 1.42], "tarifa": 6},
        {"tipo": 4, "probabilidad": 0.15, "tiempo_atencion": [1.50, 2.17], "tarifa": 9},
        {"tipo": 5, "probabilidad": 0.10, "tiempo_atencion": [2.50, 3.50], "tarifa": 12},
    ]
}

# Función auxiliar para calcular tiempo de atención dado un tipo de auto
def obtener_tiempo_atencion(tipo: int, config=None):
    if config is None:
        config = CONFIG
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        raise ValueError(f"Tipo {tipo} no encontrado")

    tiempo = tipo_data["tiempo_atencion"]

    # Si el tiempo es fijo (tipo 1), simplemente lo retorna
    if len(tiempo) == 1:
        return tiempo[0]
    else:
        # Si el tiempo es un rango, devuelve un valor uniforme en ese intervalo
        return tiempo[0] + random.random() * (tiempo[1] - tiempo[0])
