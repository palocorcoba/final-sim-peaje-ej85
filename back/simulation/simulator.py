import random
import heapq
import math
from simulation.models import Auto, Cabina, Evento
from simulation.config import CONFIG

# Devuelve una descripción del evento (ej: "llegada auto 5")
def describir_evento(evento, auto=None):
    if evento.tipo in ('llegada', 'fin_atencion', 'inicio_atencion'):
        id_auto = (auto.id if auto is not None else
                   evento.auto.id if evento.auto is not None else None)
        return f"{evento.tipo} auto {id_auto}" if id_auto is not None else evento.tipo
    return evento.tipo

# Genera el tiempo hasta la próxima llegada usando distribución exponencial negativa con media 1.2 min
def generar_llegada(config=CONFIG):
    rnd = random.random()
    return -config["media_llegadas"] * math.log(1 - rnd)

# Determina aleatoriamente el tipo de auto según las probabilidades definidas en CONFIG
def determinar_tipo_auto(config=CONFIG):
    rnd = random.random()
    acumulada = 0
    for tipo_data in config["tipos_autos"]:
        acumulada += tipo_data["probabilidad"]
        if rnd < acumulada:
            return tipo_data["tipo"]
    return config["tipos_autos"][-1]["tipo"]

# Devuelve el tiempo de atención del auto según su tipo
# Tipo 1: valor fijo, Tipos 2 a 5: tiempo uniforme entre [A, B]
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

# Devuelve la tarifa del peaje según el tipo de auto
def obtener_tarifa(tipo, config=CONFIG):
    tipo_data = next((t for t in config["tipos_autos"] if t["tipo"] == tipo), None)
    if not tipo_data:
        return 0
    return tipo_data["tarifa"]

# Inicia la atención de un auto en una cabina: se crean eventos de inicio y fin de atención
def iniciar_atencion(auto, cabina, reloj, eventos, config=CONFIG):
    cabina.libre = False
    auto.estado = 'AT'
    auto.inicio_atencion = reloj
    auto.cabina_asignada = cabina.numero
    duracion = auto.tiempo_atencion
    auto.fin_atencion = reloj + duracion
    evento_inicio = Evento('inicio_atencion', reloj, auto, cabina)
    evento_fin = Evento('fin_atencion', auto.fin_atencion, auto, cabina)
    heapq.heappush(eventos, evento_inicio)
    heapq.heappush(eventos, evento_fin)
    cabina.auto_actual = auto

# Función principal que simula el sistema de peaje
def simular(n_iteraciones=1000, mostrar_desde=0, mostrar_hasta=100, config=CONFIG):
    reloj = 0  # Tiempo actual del sistema
    eventos = []  # Cola de eventos (min-heap)
    autos = []  # Lista de todos los autos que pasaron por el sistema

    # Crear todas las cabinas (hasta max_cabinas), pero solo la primera empieza habilitada
    cabinas = [Cabina(i + 1) for i in range(config["max_cabinas"])]
    cabinas[0].habilitada = True
    for c in cabinas:
        c.auto_actual = None

    # Agregar el primer evento de llegada
    heapq.heappush(eventos, Evento('llegada', generar_llegada(config)))

    registros = []  # Registros de eventos para análisis/visualización
    contador_registros = 0  # Número de iteraciones realizadas

    # Variables para métricas del sistema
    tiempo_total = 0  # Tiempo total de simulación
    tiempo_cabinas_habilitadas = 0  # Acumulador de (tiempo * cabinas habilitadas)
    tiempo_por_cantidad = {}  # Tiempo acumulado por cantidad de cabinas habilitadas
    max_cabinas = 1  # Máximo número de cabinas habilitadas al mismo tiempo
    monto_recaudado_100 = 0  # Recaudación acumulada en los primeros 6000 minutos (100 horas)
    autos_descartados = 0  # Autos que no pudieron ingresar por falta de espacio
    reloj_anterior = 0  # Marca temporal para calcular delta_t
    llego_a_6000 = False  # Marca si se alcanzaron los 6000 minutos

    while contador_registros < n_iteraciones and eventos:
        evento = heapq.heappop(eventos)
        reloj = evento.tiempo
        delta_t = reloj - reloj_anterior
        reloj_anterior = reloj

        # Actualizar métricas de tiempo
        habilitadas = sum(1 for c in cabinas if c.habilitada)
        tiempo_cabinas_habilitadas += habilitadas * delta_t
        tiempo_total += delta_t
        tiempo_por_cantidad[habilitadas] = tiempo_por_cantidad.get(habilitadas, 0) + delta_t
        max_cabinas = max(max_cabinas, habilitadas)

        tiempo_aten = None
        auto = None
        fin_real_atencion = None

        # Evento: llegada de auto
        if evento.tipo == 'llegada':
            tipo = determinar_tipo_auto(config)
            auto = Auto(len(autos) + 1, reloj, tipo)
            tiempo_aten = obtener_tiempo_atencion(tipo, config)
            auto.tiempo_atencion = tiempo_aten
            autos.append(auto)

            # Buscar una cabina habilitada con espacio
            cabina_asignada = None
            for cabina in cabinas:
                if cabina.habilitada and len(cabina.cola) < config["max_autos_por_cola"]:
                    cabina_asignada = cabina
                    break

            # Si no hay espacio, habilitar nueva cabina (hasta el máximo permitido)
            if cabina_asignada is None:
                for cabina in cabinas:
                    if not cabina.habilitada:
                        cabina.habilitada = True
                        cabina_asignada = cabina
                        break

            # Si todas las cabinas están llenas y habilitadas → descartar el auto
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

            # Programar la siguiente llegada
            heapq.heappush(eventos, Evento('llegada', reloj + generar_llegada(config)))

        # Evento: fin de atención
        elif evento.tipo == 'fin_atencion':
            cabina = evento.cabina
            cabina.libre = True

            # Sumar a la recaudación solo si estamos dentro de los primeros 6000 minutos
            if reloj <= 6000:
                tarifa = obtener_tarifa(evento.auto.tipo, config)
                monto_recaudado_100 += tarifa

            if reloj >= 6000:
                llego_a_6000 = True

            # Si hay cola en la cabina, iniciar atención al siguiente auto
            if cabina.cola:
                siguiente_auto = cabina.cola.pop(0)
                iniciar_atencion(siguiente_auto, cabina, reloj, eventos, config)
                fin_real_atencion = siguiente_auto.fin_atencion
            else:
                # Si no hay cola y hay otras cabinas habilitadas → deshabilitar esta
                otras_habilitadas = [c for c in cabinas if c != cabina and c.habilitada]
                if otras_habilitadas:
                    cabina.habilitada = False
                cabina.auto_actual = None
                fin_real_atencion = None

            auto = evento.auto

        # Evento: inicio de atención
        elif evento.tipo == 'inicio_atencion':
            auto = evento.auto
            if mostrar_desde <= contador_registros < mostrar_hasta:
                # Guardar el estado del sistema para visualización
                registro = {
                    "reloj": reloj,
                    "evento": f"inicio_atencion auto {auto.id}",
                    "autos": len(autos),
                    "en_sistema": sum((1 for c in cabinas if c.habilitada for _ in c.cola)) + sum((1 for c in cabinas if c.habilitada and not c.libre)),
                    "cabinas_habilitadas": habilitadas,
                    "autos_descartados": autos_descartados,
                    "tiempo_estimado_atencion": auto.tiempo_atencion,
                    "fin_real_atencion": auto.fin_atencion,
                    "cabina_atendida": auto.cabina_asignada,
                    "numero_iteracion": contador_registros
                }
                for i, c in enumerate(cabinas, start=1):
                    registro[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
                    registro[f"cola_c{i}"] = len(c.cola)
                    registro[f"habilitada_c{i}"] = c.habilitada
                registros.append(registro)

        evento_str = describir_evento(evento, auto)

        # Guardar el evento en el registro si corresponde
        if evento.tipo != 'inicio_atencion':
            if mostrar_desde <= contador_registros < mostrar_hasta:
                registro = {
                    "reloj": reloj,
                    "evento": evento_str,
                    "autos": len(autos),
                    "en_sistema": sum((1 for c in cabinas if c.habilitada for _ in c.cola)) + sum((1 for c in cabinas if c.habilitada and not c.libre)),
                    "cabinas_habilitadas": habilitadas,
                    "autos_descartados": autos_descartados,
                    "tiempo_estimado_atencion": tiempo_aten if evento.tipo == 'llegada' else None,
                    "fin_real_atencion": fin_real_atencion if evento.tipo == 'llegada' else None,
                    "cabina_atendida": None,
                    "numero_iteracion": contador_registros
                }

                if evento.tipo == 'llegada' and auto is not None:
                    registro["tipo_auto"] = auto.tipo

                for i, c in enumerate(cabinas, start=1):
                    registro[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
                    registro[f"cola_c{i}"] = len(c.cola)
                registros.append(registro)

        contador_registros += 1

    # Guardar estado de la última iteración
    ultima_iteracion = None
    if contador_registros > 0:
        evento_str = describir_evento(evento, auto)
        ultima_iteracion = {
            "reloj": reloj,
            "evento": evento_str,
            "autos": len(autos),
            "en_sistema": sum((1 for c in cabinas if c.habilitada for _ in c.cola)) + sum((1 for c in cabinas if c.habilitada and not c.libre)),
            "cabinas_habilitadas": habilitadas,
            "autos_descartados": autos_descartados,
            "numero_iteracion": contador_registros - 1,
            "tiempo_estimado_atencion": auto.tiempo_atencion,
            "fin_real_atencion": auto.fin_atencion,
            "cabina_atendida": auto.cabina_asignada,
        }

        if evento.tipo == 'llegada' and auto is not None:
            ultima_iteracion["tipo_auto"] = auto.tipo
            ultima_iteracion["tiempo_estimado_atencion"] = auto.tiempo_atencion
            if auto.fin_atencion:
                ultima_iteracion["fin_real_atencion"] = auto.fin_atencion

        for i, c in enumerate(cabinas, start=1):
            ultima_iteracion[f"estado_c{i}"] = "libre" if c.libre else "ocupado"
            ultima_iteracion[f"cola_c{i}"] = len(c.cola)

    # Calcular métricas finales
    promedio_cabinas = tiempo_cabinas_habilitadas / tiempo_total if tiempo_total > 0 else 0
    porcentaje_por_cantidad = {
        k: (v / tiempo_total * 100) if tiempo_total > 0 else 0
        for k, v in tiempo_por_cantidad.items()
    }

    # Retornar resultados para análisis
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
