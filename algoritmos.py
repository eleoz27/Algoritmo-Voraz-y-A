import heapq
import itertools
import time


def estado_inicial(origen):
    return {
        "nodo": origen,
        "tiempo": 0,
        "costo_centimos": 0,
        "transbordos": 0,
        "servicio_actual": None,
        "ultimo_servicio": None,
        "recorrido": [],
        "visitados": [origen],
    }


def validar_entrada(red, origen, destino, limites, pasajeros):
    if type(pasajeros) is not int or pasajeros <= 0:
        raise ValueError("La cantidad de pasajeros debe ser un entero positivo")
    if origen not in red["nodos"] or destino not in red["nodos"] or origen == destino:
        raise ValueError("Origen y destino deben existir y ser distintos")
    for nombre in ("presupuesto_centimos", "tiempo_maximo", "transbordos_maximos"):
        if type(limites[nombre]) is not int or limites[nombre] < 0:
            raise ValueError("Los límites deben ser enteros no negativos (presupuesto en céntimos)")


def calcular_heuristica(red, destino):
    estimaciones = {nodo: float("inf") for nodo in red["nodos"]}
    estimaciones[destino] = 0
    for _ in range(len(red["nodos"]) - 1):
        cambio = False
        for conexion in red["conexiones"]:
            candidato = conexion["recorrido_min"] + estimaciones[conexion["destino"]]
            if candidato < estimaciones[conexion["origen"]]:
                estimaciones[conexion["origen"]] = candidato
                cambio = True
        if not cambio:
            break
    return estimaciones


def siguiente_estado(red, estado, conexion, limites, permitir_revisita=False):
    if not permitir_revisita and conexion["destino"] in estado["visitados"]:
        return None
    servicio = conexion["servicio"]
    if servicio is not None and not red["servicios"][servicio]["disponible"]:
        return None

    abordaje = servicio is not None and servicio != estado["servicio_actual"]
    cambio = abordaje and estado["ultimo_servicio"] is not None and servicio != estado["ultimo_servicio"]
    espera = conexion["espera_min"] if abordaje else 0
    cobro = red["servicios"][servicio]["tarifa_centimos"] if abordaje else 0

    tiempo = estado["tiempo"] + espera + conexion["recorrido_min"]
    costo = estado["costo_centimos"] + cobro
    transbordos = estado["transbordos"] + int(cambio)

    if (
        tiempo > limites["tiempo_maximo"]
        or costo > limites["presupuesto_centimos"]
        or transbordos > limites["transbordos_maximos"]
    ):
        return None

    paso = {
        **conexion,
        "espera_aplicada": espera,
        "cobro_centimos": cobro,
        "cambio_servicio": bool(cambio),
        "tiempo_acumulado": tiempo,
        "costo_acumulado_centimos": costo,
        "transbordos_acumulados": transbordos,
    }
    return {
        "nodo": conexion["destino"],
        "tiempo": tiempo,
        "costo_centimos": costo,
        "transbordos": transbordos,
        "servicio_actual": servicio,
        "ultimo_servicio": servicio if servicio is not None else estado["ultimo_servicio"],
        "recorrido": estado["recorrido"] + [paso],
        "visitados": estado["visitados"] + [conexion["destino"]],
    }


def crear_resultado(
    nombre, estado, encontrado, explorados, generados, inicio, eventos, limites, pasajeros, motivo
):
    servicios = []
    for paso in estado["recorrido"]:
        if paso["servicio"] and paso["servicio"] not in servicios:
            servicios.append(paso["servicio"])

    cumplimiento = None
    if encontrado:
        cumplimiento = {
            "presupuesto_individual": estado["costo_centimos"] <= limites["presupuesto_centimos"],
            "tiempo": estado["tiempo"] <= limites["tiempo_maximo"],
            "transbordos": estado["transbordos"] <= limites["transbordos_maximos"],
            "disponibilidad_modelada": True,
        }

    return {
        "algoritmo": nombre,
        "encontrado": encontrado,
        "motivo": motivo,
        "tiempo_min": estado["tiempo"] if encontrado else None,
        "costo_individual": estado["costo_centimos"] / 100 if encontrado else None,
        "costo_grupal": estado["costo_centimos"] * pasajeros / 100 if encontrado else None,
        "transbordos": estado["transbordos"] if encontrado else None,
        "pasajeros": pasajeros,
        "nodos": estado["visitados"] if encontrado else [],
        "servicios": servicios if encontrado else [],
        "recorrido": estado["recorrido"] if encontrado else [],
        "traza_parcial": estado["recorrido"] if not encontrado else [],
        "cumplimiento": cumplimiento,
        "explorados": explorados,
        "generados": generados,
        "eventos": eventos,
        "ejecucion_ms": (time.perf_counter() - inicio) * 1000,
    }


def voraz(red, origen, destino, limites, pasajeros=1):
    validar_entrada(red, origen, destino, limites, pasajeros)
    inicio = time.perf_counter()
    estado = estado_inicial(origen)
    explorados, generados = 0, 1
    eventos = []

    while True:
        explorados += 1
        if estado["nodo"] == destino:
            return crear_resultado(
                "Voraz", estado, True, explorados, generados, inicio,
                eventos, limites, pasajeros, "Ruta factible; Voraz no garantiza optimalidad",
            )

        mejor = None
        candidatas = []
        for conexion in red["grafo"][estado["nodo"]]:
            opcion = siguiente_estado(red, estado, conexion, limites)
            if opcion is not None:
                generados += 1
                inmediato = opcion["tiempo"] - estado["tiempo"]
                candidatas.append({"conexion": conexion["id"], "minutos": inmediato})
                if mejor is None or opcion["tiempo"] < mejor["tiempo"]:
                    mejor = opcion

        eventos.append({
            "nodo": estado["nodo"],
            "g": estado["tiempo"],
            "candidatas": candidatas,
            "seleccion": mejor["recorrido"][-1]["id"] if mejor else None,
        })

        if mejor is None:
            return crear_resultado(
                "Voraz", estado, False, explorados, generados, inicio,
                eventos, limites, pasajeros,
                "Sin continuación factible; Voraz no retrocede. Puede existir otra ruta.",
            )
        estado = mejor


def a_estrella(red, origen, destino, limites, pasajeros=1):
    validar_entrada(red, origen, destino, limites, pasajeros)
    inicio = time.perf_counter()
    heuristica = calcular_heuristica(red, destino)
    contador = itertools.count()
    estado = estado_inicial(origen)
    pendientes = [(heuristica[origen], next(contador), estado)]
    explorados, generados = 0, 1
    eventos = []

    while pendientes:
        prioridad, _, estado = heapq.heappop(pendientes)
        explorados += 1
        eventos.append({
            "nodo": estado["nodo"],
            "g": estado["tiempo"],
            "h": heuristica[estado["nodo"]],
            "f": prioridad,
            "costo_centimos": estado["costo_centimos"],
            "transbordos": estado["transbordos"],
        })

        if estado["nodo"] == destino:
            return crear_resultado(
                "A*", estado, True, explorados, generados, inicio,
                eventos, limites, pasajeros, "Ruta de menor tiempo factible bajo el modelo",
            )

        for conexion in red["grafo"][estado["nodo"]]:
            opcion = siguiente_estado(red, estado, conexion, limites, permitir_revisita=True)
            if opcion is not None and heuristica[opcion["nodo"]] != float("inf"):
                generados += 1
                prioridad = opcion["tiempo"] + heuristica[opcion["nodo"]]
                heapq.heappush(pendientes, (prioridad, next(contador), opcion))

    return crear_resultado(
        "A*", estado, False, explorados, generados, inicio,
        eventos, limites, pasajeros, "No existe una ruta factible",
    )
