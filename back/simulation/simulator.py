import random
import heapq
import math
from simulation.models import Auto, Cabina, Evento
from simulation.config import CONFIG

def generar_llegada():
    rnd = random.random()
    return -CONFIG["media_llegadas"] * math.log(1 - rnd)

def determinar_tipo_auto():
    rnd = random.random()
    for prob, tipo in CONFIG["probabilidades_tipos_autos"]:
        if rnd < prob:
            return tipo
    return 5

def tiempo_atencion_por_tipo(tipo):
    return CONFIG["tiempos_atencion"][tipo]()

def simular(n_iteraciones=1000, mostrar_desde=0, mostrar_hasta=100):
    reloj = 0
    eventos = []
    autos = []
    cabinas = [Cabina(i + 1) for i in range(CONFIG["max_cabinas"])]
    cabinas[0].habilitada = True  # Al menos una al inicio

    heapq.heappush(eventos, Evento('llegada', generar_llegada()))

    registros = []
    contador_registros = 0

    tiempo_total = 0
    tiempo_cabinas_habilitadas = 0
    tiempo_por_cantidad = {}
    max_cabinas = 1
    monto_recaudado = 0
    reloj_anterior = 0

    while contador_registros < n_iteraciones and eventos:
        evento = heapq.heappop(eventos)
        reloj = evento.tiempo

        delta_t = reloj - reloj_anterior
        reloj_anterior = reloj

        habilitadas = sum(1 for c in cabinas if c.habilitada)
        tiempo_cabinas_habilitadas += habilitadas * delta_t
        tiempo_total += delta_t
        tiempo_por_cantidad[habilitadas] = tiempo_por_cantidad.get(habilitadas, 0) + delta_t
        max_cabinas = max(max_cabinas, habilitadas)

        if evento.tipo == 'llegada':
            tipo = determinar_tipo_auto()
            auto = Auto(len(autos) + 1, reloj, tipo)
            autos.append(auto)

            cabina_asignada = None

            # Buscar cabina habilitada con lugar
            for cabina in cabinas:
                if cabina.habilitada and len(cabina.cola) < CONFIG["max_autos_por_cola"]:
                    cabina_asignada = cabina
                    break

            if cabina_asignada is None:
                # Intentar habilitar una nueva
                for cabina in cabinas:
                    if not cabina.habilitada:
                        cabina.habilitada = True
                        cabina_asignada = cabina
                        break

            if cabina_asignada is not None:
                cabina_asignada.cola.append(auto)
                if cabina_asignada.libre:
                    iniciar_atencion(auto, cabina_asignada, reloj, eventos)
                # Si no está libre, se queda en cola
            # Si no hay cabina libre ni puedo habilitar más → auto se pierde (descartado)

            heapq.heappush(eventos, Evento('llegada', reloj + generar_llegada()))

        elif evento.tipo == 'fin_atencion':
            cabina = evento.cabina
            cabina.libre = True
            monto_recaudado += CONFIG["tarifas_por_tipo"][evento.auto.tipo]

            if cabina.cola:
                siguiente_auto = cabina.cola.pop(0)
                iniciar_atencion(siguiente_auto, cabina, reloj, eventos)
            else:
                # Ver si puede apagarse
                otras_habilitadas = [c for c in cabinas if c != cabina and c.habilitada]
                if otras_habilitadas:
                    cabina.habilitada = False

        if mostrar_desde <= contador_registros < mostrar_hasta:
            registros.append({
                "reloj": reloj,
                "evento": evento.tipo,
                "autos": len(autos),
                "en_sistema": sum(1 for a in autos if a.fin_atencion is None),
                "cabinas_habilitadas": habilitadas,
                "numero_iteracion": contador_registros
            })

        contador_registros += 1

    ultima_iteracion = None
    if contador_registros > 0:
        ultima_iteracion = {
            "reloj": reloj,
            "evento": evento.tipo,
            "autos": len(autos),
            "en_sistema": sum(1 for a in autos if a.fin_atencion is None),
            "cabinas_habilitadas": habilitadas,
            "numero_iteracion": contador_registros - 1
        }

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
        "monto_recaudado": monto_recaudado,
        "porcentaje_por_cantidad": porcentaje_por_cantidad,
        "max_cabinas": max_cabinas
    }

def iniciar_atencion(auto, cabina, reloj, eventos):
    cabina.libre = False
    auto.estado = 'AT'
    auto.inicio_atencion = reloj
    duracion = tiempo_atencion_por_tipo(auto.tipo)
    auto.fin_atencion = reloj + duracion
    evento_fin = Evento('fin_atencion', auto.fin_atencion, auto, cabina)
    heapq.heappush(eventos, evento_fin)
