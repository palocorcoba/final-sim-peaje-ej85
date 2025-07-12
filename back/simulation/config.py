import random

CONFIG = {
    "media_llegadas": 1.2,
    "max_cabinas": 4,
    "max_autos_por_cola": 4,
    "probabilidades_tipos_autos": [
        (0.10, 1),
        (0.60, 2),
        (0.75, 3),
        (0.90, 4),
        (1.00, 5),
    ],
    "tiempos_atencion": {
        1: lambda: 0.5,  # 30 segundos
        2: lambda: 0.75 + random.random() * (0.92 - 0.75), #uniforme u(45";55")
        3: lambda: 0.92 + random.random() * (1.42 - 0.92), #uniforme u(55";85")
        4: lambda: 1.50 + random.random() * (2.17 - 1.50), #uniforme u(90";130")
        5: lambda: 2.50 + random.random() * (3.50 - 2.50), #uniforme u(2'30":3'30")
    },
        "tarifas_por_tipo": {
        1: 0,
        2: 3,
        3: 6,
        4: 9,
        5: 12,
    }
}