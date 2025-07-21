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
    auto.cabina_asignada = cabina.numero
    duracion = auto.tiempo_atencion
    auto.fin_atencion = reloj + duracion
    evento_fin = Evento('fin_atencion', auto.fin_atencion, auto, cabina)
    heapq.heappush(eventos, evento_fin)
    cabina.auto_actual = auto

def simular(n_iteraciones=1000, mostrar_desde=0, mostrar_hasta=100, config=CONFIG):
    reloj = 0
    eventos = []
    autos = []
    cabinas = [Cabina(i + 1) for i in range(config["max_cabinas"])]
    cabinas[0].habilitada = True
    for c in cabinas:
        c.auto_actual = None

    heapq.heappush(eventos, Evento('llegada', generar_llegada(config)))

    registros = []
    contador_registros = 0

    tiempo_total = 0
    tiempo_cabinas_habilitadas = 0
    tiempo_por_cantidad = {}
    max_cabinas = 1
    monto_recaudado_100 = 0
    autos_descartados = 0
    reloj_anterior = 0
    llego_a_6000 = False

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

        tiempo_aten = None
        auto = None
        fin_real_atencion = None

        if evento.tipo == 'llegada':
            tipo = determinar_tipo_auto(config)
            auto = Auto(len(autos) + 1, reloj, tipo)
            tiempo_aten = obtener_tiempo_atencion(tipo, config)
            auto.tiempo_atencion = tiempo_aten
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
                    fin_real_atencion = auto.fin_atencion
                else:
                    cabina_asignada.cola.append(auto)

            heapq.heappush(eventos, Evento('llegada', reloj + generar_llegada(config)))

        elif evento.tipo == 'fin_atencion':
            cabina = evento.cabina
            cabina.libre = True

            if reloj <= 6000:
                tarifa = obtener_tarifa(evento.auto.tipo, config)
                monto_recaudado_100 += tarifa

            if reloj >= 6000:
                llego_a_6000 = True

            if cabina.cola:
                siguiente_auto = cabina.cola.pop(0)
                iniciar_atencion(siguiente_auto, cabina, reloj, eventos, config)
                fin_real_atencion = siguiente_auto.fin_atencion

                if mostrar_desde <= contador_registros < mostrar_hasta:
                    registro = {
                        "reloj": reloj,
                        "evento": f"inicio_atencion auto {siguiente_auto.id}",
                        "autos": len(autos),
                        "en_sistema": sum(1 for a in autos if a.fin_atencion is None or reloj < a.fin_atencion),
                        "cabinas_habilitadas": habilitadas,
                        "autos_descartados": autos_descartados,
                        "tiempo_estimado_atencion": siguiente_auto.tiempo_atencion,
                        "fin_real_atencion": siguiente_auto.fin_atencion,
                        "numero_iteracion": contador_registros
                    }
                    for i, c in enumerate(cabinas, start=1):
                        registro[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
                        registro[f"cola_c{i}"] = len(c.cola)
                        registro[f"habilitada_c{i}"] = c.habilitada
                    registros.append(registro)
                    contador_registros += 1
            else:
                otras_habilitadas = [c for c in cabinas if c != cabina and c.habilitada]
                if otras_habilitadas:
                    cabina.habilitada = False
                cabina.auto_actual = None
                fin_real_atencion = None

            auto = evento.auto

        if mostrar_desde <= contador_registros < mostrar_hasta:
            if evento.tipo == 'llegada':
                evento_str = f"llegada auto {auto.id}"
            elif evento.tipo == 'fin_atencion':
                evento_str = f"fin_atencion auto {evento.auto.id}"
            else:
                evento_str = evento.tipo

            registro = {
                "reloj": reloj,
                "evento": evento_str,
                "autos": len(autos),
                "en_sistema": sum(1 for a in autos if a.fin_atencion is None or reloj < a.fin_atencion),
                "cabinas_habilitadas": habilitadas,
                "autos_descartados": autos_descartados,
                "tiempo_estimado_atencion": tiempo_aten if evento.tipo == 'llegada' else None,
                "fin_real_atencion": fin_real_atencion if evento.tipo == 'llegada' else None,
                "numero_iteracion": contador_registros
            }

            for i, c in enumerate(cabinas, start=1):
                registro[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
                registro[f"cola_c{i}"] = len(c.cola)
                registro[f"habilitada_c{i}"] = c.habilitada

            registros.append(registro)

        contador_registros += 1

    ultima_iteracion = None
    if contador_registros > 0:
        ultima_iteracion = {
            "reloj": reloj,
            "evento": evento.tipo,
            "autos": len(autos),
            "en_sistema": sum(1 for a in autos if a.fin_atencion is None or reloj < a.fin_atencion),
            "cabinas_habilitadas": habilitadas,
            "autos_descartados": autos_descartados,
            "numero_iteracion": contador_registros - 1
        }
        for i, c in enumerate(cabinas, start=1):
            ultima_iteracion[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
            ultima_iteracion[f"cola_c{i}"] = len(c.cola)
            ultima_iteracion[f"habilitada_c{i}"] = c.habilitada

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