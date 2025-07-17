# ------------------------------------------------------------------------------
# Archivo: config_schemas.py
# Propósito: Define los esquemas de validación de datos para la configuración 
#            de la simulación usando Pydantic. Este archivo se usa en el backend 
#            (main.py) para validar tanto la configuración por defecto como las 
#            configuraciones personalizadas enviadas desde el frontend.
# ------------------------------------------------------------------------------

from pydantic import BaseModel
from typing import List

# Representa la configuración individual de un tipo de auto (tipo, probabilidad, tiempo y tarifa)
class TipoAutoConfig(BaseModel):
    tipo: int  # Número identificador del tipo de auto (1 al 5)
    probabilidad: float  # Probabilidad asociada a ese tipo de auto (debe sumar 1 entre todos)
    tiempo_atencion: List[float]  # Tiempo de atención en segundos. Puede ser [valor fijo] o [mínimo, máximo] para intervalo.
    tarifa: float  # Monto a cobrar por ese tipo de auto

# Representa la configuración general del peaje
class ConfigPeaje(BaseModel):
    media_llegadas: float  # Media de tiempo entre llegadas (usado para generar llegadas exponenciales)
    tipos_autos: List[TipoAutoConfig]  # Lista de configuraciones para cada tipo de auto
