import random
import heapq
import math
from simulation.models import Auto, Cabina, Evento
from simulation.config import CONFIG

def generar_llegada(config=CONFIG):
    rnd = random.random()
    return -config["media_llegadas"] * math.log(1 - rnd)

def determinar_tipo_auto(config=CONFIG):
    rnd = random.random()
    acumulada = 0
    for tipo_data in config["tipos_autos"]:
        acumulada += tipo_data["probabilidad"]
        if rnd < acumulada:
            return tipo_data["tipo"]
    return config["tipos_autos"][-1]["tipo"]

def obtener_tiempo_atencion(tipo, config=CONFIG):
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        raise ValueError(f"Tipo {tipo} no encontrado en configuración")
    
    tiempo = tipo_data["tiempo_atencion"]
    if isinstance(tiempo, (int, float)):
        return tiempo
    if isinstance(tiempo, list) and len(tiempo) == 2:
        a, b = tiempo
        return random.uniform(a, b)

    raise ValueError(f"Tiempos de atención mal definidos para tipo {tipo}: {tiempo}")

def obtener_tarifa(tipo, config=CONFIG):
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        return 0
    return tipo_data["tarifa"]

def iniciar_atencion(auto, cabina, reloj, eventos, config=CONFIG):
    cabina.libre = False
    auto.estado = 'AT'
    auto.inicio_atencion = reloj
    duracion = obtener_tiempo_atencion(auto.tipo, config)
    auto.fin_atencion = reloj + duracion
    evento_fin = Evento('fin_atencion', auto.fin_atencion, auto, cabina)
    heapq.heappush(eventos, evento_fin)

def simular(n_iteraciones=1000, mostrar_desde=0, mostrar_hasta=100, config=CONFIG):
    reloj = 0
    eventos = []
    autos = []
    cabinas = [Cabina(i + 1) for i in range(config["max_cabinas"])]
    cabinas[0].habilitada = True  # Al menos una al inicio

    heapq.heappush(eventos, Evento('llegada', generar_llegada(config)))

    registros = []
    contador_registros = 0

    tiempo_total = 0
    tiempo_cabinas_habilitadas = 0
    tiempo_por_cantidad = {}
    max_cabinas = 1
    monto_recaudado = 0
    monto_recaudado_100 = 0
    autos_descartados = 0
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
            tipo = determinar_tipo_auto(config)
            auto = Auto(len(autos) + 1, reloj, tipo)
            autos.append(auto)

            cabina_asignada = None

            for cabina in cabinas:
                if cabina.habilitada and len(cabina.cola) < config["max_autos_por_cola"]:
                    cabina_asignada = cabina
                    break

            if cabina_asignada is None:
                for cabina in cabinas:
                    if not cabina.habilitada:
                        cabina.habilitada = True
                        cabina_asignada = cabina
                        break

            # 🚫 Si no se puede asignar cabina, se descarta el auto
            if cabina_asignada is None:
                todas_ocupadas_y_llenas = all(
                    c.habilitada and not c.libre and len(c.cola) >= config["max_autos_por_cola"]
                    for c in cabinas
                )
                if todas_ocupadas_y_llenas:
                    autos_descartados += 1
            else:
                if cabina_asignada.libre:
                    iniciar_atencion(auto, cabina_asignada, reloj, eventos, config)
                else:
                    cabina_asignada.cola.append(auto)

            heapq.heappush(eventos, Evento('llegada', reloj + generar_llegada(config)))

        elif evento.tipo == 'fin_atencion':
            cabina = evento.cabina
            cabina.libre = True
            monto_recaudado += obtener_tarifa(evento.auto.tipo, config)

            if cabina.cola:
                siguiente_auto = cabina.cola.pop(0)
                iniciar_atencion(siguiente_auto, cabina, reloj, eventos, config)
            else:
                otras_habilitadas = [c for c in cabinas if c != cabina and c.habilitada]
                if otras_habilitadas:
                    cabina.habilitada = False

        if mostrar_desde <= contador_registros < mostrar_hasta:
            registro = {
                "reloj": reloj,
                "evento": evento.tipo,
                "autos": len(autos),
                "en_sistema": sum(1 for a in autos if a.fin_atencion is None),
                "cabinas_habilitadas": habilitadas,
                "autos_descartados": autos_descartados,
                "numero_iteracion": contador_registros
            }

            for i, c in enumerate(cabinas, start=1):
                registro[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
                registro[f"cola_c{i}"] = len(c.cola)

            registros.append(registro)

        contador_registros += 1

        if reloj == 6000:
            monto_recaudado_100 = monto_recaudado

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
        "monto_recaudado_100": monto_recaudado_100,
        "porcentaje_por_cantidad": porcentaje_por_cantidad,
        "max_cabinas": max_cabinas
    }

