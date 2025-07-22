# Clase que representa a cada auto que llega al peaje
class Auto:
    def __init__(self, id, llegada, tipo):
        self.id = id  # Identificador único del auto
        self.llegada = llegada  # Momento en que el auto llega al sistema
        self.tipo = tipo  # Tipo de vehículo (1 a 5), según la tabla del enunciado
        self.estado = 'EA'  # Estado inicial: EA = Esperando Atención
        self.inicio_atencion = None  # Reloj en el que comienza la atención
        self.fin_atencion = None     # Reloj en el que finaliza la atención
        self.cabina_asignada = None  # Se setea cuando el auto entra en atención

# Clase que representa una cabina de peaje
class Cabina:
    def __init__(self, numero):
        self.numero = numero  # Número de cabina (1 a 4)
        self.cola = []        # Cola de autos esperando en esta cabina
        self.libre = True     # Estado actual de la cabina: True = libre, False = ocupada
        # Solo la cabina 1 empieza habilitada. Las otras se habilitan si la cola supera el límite
        self.habilitada = True if numero == 1 else False
        # (Opcional) auto_actual permite registrar qué auto está siendo atendido en esta cabina
        self.auto_actual = None

# Clase que representa un evento en la simulación
class Evento:
    def __init__(self, tipo, tiempo, auto=None, cabina=None):
        self.tipo = tipo      # Tipo de evento: 'llegada' o 'fin_atencion'
        self.tiempo = tiempo  # Tiempo (valor del reloj) en que ocurre el evento
        self.auto = auto      # Auto involucrado en el evento
        self.cabina = cabina  # Cabina involucrada (en caso de fin de atención)

    # Permite que la cola de eventos (heapq) mantenga orden por tiempo (menor primero)
    def __lt__(self, other):
        return self.tiempo < other.tiempo
