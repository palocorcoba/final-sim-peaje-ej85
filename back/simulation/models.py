class Auto:
    def __init__(self, id, llegada, tipo):
        self.id = id
        self.llegada = llegada
        self.tipo = tipo
        self.estado = 'EA'  # Esperando atención
        self.inicio_atencion = None
        self.fin_atencion = None

class Cabina:
    def __init__(self, numero):
        self.numero = numero
        self.cola = []
        self.libre = True
        self.habilitada = True if numero == 1 else False
        self.auto_actual = None  # Podés dejarlo si lo usás para rastrear qué auto atiende


class Evento:
    def __init__(self, tipo, tiempo, auto=None, cabina=None):
        self.tipo = tipo  # 'llegada' o 'fin_atencion'
        self.tiempo = tiempo
        self.auto = auto
        self.cabina = cabina

    def __lt__(self, other):
        return self.tiempo < other.tiempo
