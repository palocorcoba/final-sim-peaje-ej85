from pydantic import BaseModel
from typing import List

class TipoAutoConfig(BaseModel):
    tipo: int
    probabilidad: float
    tiempo_atencion: List[float]  # puede ser [valor] o [a, b]
    tarifa: float

class ConfigPeaje(BaseModel):
    media_llegadas: float
    tipos_autos: List[TipoAutoConfig]
