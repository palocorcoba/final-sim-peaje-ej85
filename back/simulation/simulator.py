import random
import heapq
import math
from simulation.models import Auto, Cabina, Evento
from simulation.config import CONFIG

# Genera un tiempo entre llegadas según distribución exponencial negativa con media configurable
def generar_llegada(config=CONFIG):
    rnd = random.random()
    return -config["media_llegadas"] * math.log(1 - rnd)

# Determina el tipo de auto usando la tabla de probabilidades acumuladas
def determinar_tipo_auto(config=CONFIG):
    rnd = random.random()
    acumulada = 0
    for tipo_data in config["tipos_autos"]:
        acumulada += tipo_data["probabilidad"]
        if rnd < acumulada:
            return tipo_data["tipo"]
    return config["tipos_autos"][-1]["tipo"]

# Obtiene el tiempo de atención en segundos de acuerdo al tipo de auto
def obtener_tiempo_atencion(tipo, config=CONFIG):
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        raise ValueError(f"Tipo {tipo} no encontrado en configuración")
    
    tiempo = tipo_data["tiempo_atencion"]
    # Si es un valor fijo (por ejemplo, 30 segundos para tipo 1)
    if isinstance(tiempo, (int, float)):
        return tiempo
    # Si es un rango [a, b], se usa una distribución uniforme
    if isinstance(tiempo, list) and len(tiempo) == 2:
        a, b = tiempo
        return random.uniform(a, b)

    raise ValueError(f"Tiempos de atención mal definidos para tipo {tipo}: {tiempo}")

# Devuelve la tarifa (costo del peaje) asociada al tipo de auto
def obtener_tarifa(tipo, config=CONFIG):
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        return 0
    return tipo_data["tarifa"]

# Inicia la atención de un auto en una cabina:
# - marca la cabina como ocupada
# - calcula su duración
# - programa el evento fin_atencion correspondiente
def iniciar_atencion(auto, cabina, reloj, eventos, config=CONFIG):
    cabina.libre = False
    auto.estado = 'AT'
    auto.inicio_atencion = reloj
    duracion = obtener_tiempo_atencion(auto.tipo, config)
    auto.fin_atencion = reloj + duracion
    evento_fin = Evento('fin_atencion', auto.fin_atencion, auto, cabina)
    heapq.heappush(eventos, evento_fin)

# Función principal de simulación
def simular(n_iteraciones=1000, mostrar_desde=0, mostrar_hasta=100, config=CONFIG):
    reloj = 0
    eventos = []
    autos = []
    cabinas = [Cabina(i + 1) for i in range(config["max_cabinas"])]
    cabinas[0].habilitada = True  # Al menos una al inicio

    # Primer evento: llegada de auto inicial
    heapq.heappush(eventos, Evento('llegada', generar_llegada(config)))

    registros = []
    contador_registros = 0

    # Variables para métricas de los puntos a, b, c y d
    tiempo_total = 0
    tiempo_cabinas_habilitadas = 0
    tiempo_por_cantidad = {}
    max_cabinas = 1
    #monto_recaudado = 0
    monto_recaudado_100 = 0
    autos_descartados = 0
    reloj_anterior = 0
    llego_a_6000 = False

    # Bucle principal de eventos
    while contador_registros < n_iteraciones and eventos:
        evento = heapq.heappop(eventos)
        reloj = evento.tiempo

        # Calculo del tiempo transcurrido desde el último evento
        delta_t = reloj - reloj_anterior
        reloj_anterior = reloj

        # Actualiza métricas de cabinas habilitadas
        habilitadas = sum(1 for c in cabinas if c.habilitada)
        tiempo_cabinas_habilitadas += habilitadas * delta_t
        tiempo_total += delta_t
        tiempo_por_cantidad[habilitadas] = tiempo_por_cantidad.get(habilitadas, 0) + delta_t
        max_cabinas = max(max_cabinas, habilitadas)

        # Evento de llegada de auto
        if evento.tipo == 'llegada':
            tipo = determinar_tipo_auto(config)
            auto = Auto(len(autos) + 1, reloj, tipo)
            autos.append(auto)

            cabina_asignada = None

            # Intentar asignar auto a cabina habilitada con espacio en la cola
            for cabina in cabinas:
                if cabina.habilitada and len(cabina.cola) < config["max_autos_por_cola"]:
                    cabina_asignada = cabina
                    break

            # Si no hay cabina con espacio, se habilita una nueva si es posible
            if cabina_asignada is None:
                for cabina in cabinas:
                    if not cabina.habilitada:
                        cabina.habilitada = True
                        cabina_asignada = cabina
                        break

            # Si no se puede asignar cabina, se descarta el auto
            if cabina_asignada is None:
                todas_ocupadas_y_llenas = all(
                    c.habilitada and not c.libre and len(c.cola) >= config["max_autos_por_cola"]
                    for c in cabinas
                )
                if todas_ocupadas_y_llenas:
                    autos_descartados += 1
            else:
                # Si la cabina está libre, se atiende inmediatamente
                if cabina_asignada.libre:
                    iniciar_atencion(auto, cabina_asignada, reloj, eventos, config)
                else:
                    cabina_asignada.cola.append(auto)
            # Se agenda la próxima llegada
            heapq.heappush(eventos, Evento('llegada', reloj + generar_llegada(config)))

        # Evento de fin de atención
        elif evento.tipo == 'fin_atencion':
            cabina = evento.cabina
            cabina.libre = True

            # Se suma la tarifa recaudada, esto lo hacia antes y acumulaba todo, sin importar el reloj
            #monto_recaudado += obtener_tarifa(evento.auto.tipo, config)

            #Porfe Carena me contestó al mail y me dijo que de esta forma era lo correcto
            if reloj <= 6000:
                tarifa = obtener_tarifa(evento.auto.tipo, config)
                monto_recaudado_100 += tarifa

            if reloj >= 6000:
                llego_a_6000 = True

            if cabina.cola:
                # Si hay autos esperando, se inicia atención al siguiente
                siguiente_auto = cabina.cola.pop(0)
                iniciar_atencion(siguiente_auto, cabina, reloj, eventos, config)
            else:
                # Si la cabina queda vacía y hay otras habilitadas, se deshabilita
                otras_habilitadas = [c for c in cabinas if c != cabina and c.habilitada]
                if otras_habilitadas:
                    cabina.habilitada = False

        # Guardar iteraciones dentro del rango a mostrar
        if mostrar_desde <= contador_registros < mostrar_hasta:
            registro = {
                "reloj": reloj,
                "evento": evento.tipo,
                "autos": len(autos),
                "en_sistema": sum(1 for a in autos if a.fin_atencion is None or reloj < a.fin_atencion),
                "cabinas_habilitadas": habilitadas,
                "autos_descartados": autos_descartados,
                "numero_iteracion": contador_registros
            }

            # Estado y cola de cada cabina
            for i, c in enumerate(cabinas, start=1):
                registro[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
                registro[f"cola_c{i}"] = len(c.cola)

            registros.append(registro)

        contador_registros += 1

        # Al llegar a 100 horas (6000 min), guardar monto recaudado parcial
        # Ver esta logica cuando contesten los profes
        #if reloj == 6000:
         #   monto_recaudado_100 = monto_recaudado

    # Última iteración a mostrar siempre
    ultima_iteracion = None
    if contador_registros > 0:
        ultima_iteracion = {
            "reloj": reloj,
            "evento": evento.tipo,
            "autos": len(autos),
            "en_sistema": sum(1 for a in autos if a.fin_atencion is None),
            "cabinas_habilitadas": habilitadas,
            "autos_descartados": autos_descartados,
            "numero_iteracion": contador_registros - 1
        }

        for i, c in enumerate(cabinas, start=1):
            ultima_iteracion[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
            ultima_iteracion[f"cola_c{i}"] = len(c.cola)

    # Cálculos finales para los puntos del enunciado
    promedio_cabinas = tiempo_cabinas_habilitadas / tiempo_total if tiempo_total > 0 else 0
    porcentaje_por_cantidad = {
        k: (v / tiempo_total * 100) if tiempo_total > 0 else 0
        for k, v in tiempo_por_cantidad.items()
    }

    return {
        "iteraciones": registros,
        "ultima_iteracion": ultima_iteracion,
        "total_iteraciones": n_iteraciones,
        "total_autos": len(autos),
        "promedio_cabinas": promedio_cabinas,
        "monto_recaudado_100": monto_recaudado_100 if llego_a_6000 else 0,
        "porcentaje_por_cantidad": porcentaje_por_cantidad,
        "max_cabinas": max_cabinas
    }

