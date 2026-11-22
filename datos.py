from copy import deepcopy

ORIGEN = "santa_clara"
DESTINO = "abancay"


NODOS = {
    "santa_clara": "Av. La Estrella con Av. Nicolás Ayllón, frente al Real Plaza Santa Clara, Ate",
    "balta_acho": "Sector Puente Balta/Acho",
    "9_octubre": "Av. 9 de Octubre",
    "abancay": "Av. Abancay, Cercado de Lima",
}

SERVICIOS = {
    "la_z": {
        "nombre": "La Z",
        "empresa": "Transportes y Servicios Santa Rosa de Lima S.A.",
        "tarifa_centimos": 350,
        "disponible": True,
    },
    "el_loro": {
        "nombre": "El Loro",
        "empresa": "Inversiones y Representaciones Polo S.A.C.",
        "tarifa_centimos": 300,
        "disponible": True,
    },
    "104": {"nombre": "Ruta 104", "empresa": None, "tarifa_centimos": 100, "disponible": True},
    "31": {"nombre": "Ruta 31", "empresa": None, "tarifa_centimos": 100, "disponible": True},
    "08": {"nombre": "Ruta 08", "empresa": None, "tarifa_centimos": 100, "disponible": True},
}

CONEXIONES = [
    {
        "id": "directa",
        "origen": "santa_clara",
        "destino": "abancay",
        "tipo": "vehiculo",
        "servicio": "la_z",
        "espera_tipo": "inicial",
        "espera_min": 15,
        "recorrido_min": 38,
    },
    {
        "id": "loro",
        "origen": "santa_clara",
        "destino": "balta_acho",
        "tipo": "vehiculo",
        "servicio": "el_loro",
        "espera_tipo": "inicial",
        "espera_min": 8,
        "recorrido_min": 30,
    },
    {
        "id": "caminata",
        "origen": "balta_acho",
        "destino": "9_octubre",
        "tipo": "caminata",
        "servicio": None,
        "espera_tipo": None,
        "espera_min": 0,
        "recorrido_min": 2,
    },
    {
        "id": "conexion_104",
        "origen": "9_octubre",
        "destino": "abancay",
        "tipo": "vehiculo",
        "servicio": "104",
        "espera_tipo": "conexion",
        "espera_min": 3,
        "recorrido_min": 3,
    },
    {
        "id": "conexion_31",
        "origen": "9_octubre",
        "destino": "abancay",
        "tipo": "vehiculo",
        "servicio": "31",
        "espera_tipo": "conexion",
        "espera_min": 3,
        "recorrido_min": 3,
    },
    {
        "id": "conexion_08",
        "origen": "9_octubre",
        "destino": "abancay",
        "tipo": "vehiculo",
        "servicio": "08",
        "espera_tipo": "conexion",
        "espera_min": 3,
        "recorrido_min": 3,
    },
]


def cargar_red():
    """Construye una copia fresca de la red y su lista de adyacencia."""
    nodos = deepcopy(NODOS)
    servicios = deepcopy(SERVICIOS)
    conexiones = deepcopy(CONEXIONES)
    grafo = {nodo: [] for nodo in nodos}
    for conexion in conexiones:
        grafo[conexion["origen"]].append(conexion)
    return {
        "nodos": nodos,
        "servicios": servicios,
        "conexiones": conexiones,
        "grafo": grafo,
    }


def crear_limites(presupuesto_centimos=500, tiempo_maximo=90, transbordos_maximos=2):
    """Construye el diccionario de restricciones del caso de estudio."""
    return {
        "presupuesto_centimos": presupuesto_centimos,
        "tiempo_maximo": tiempo_maximo,
        "transbordos_maximos": transbordos_maximos,
    }
