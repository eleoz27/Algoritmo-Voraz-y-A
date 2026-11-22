from datos import ORIGEN, DESTINO, cargar_red, crear_limites
from algoritmos import voraz, a_estrella, estado_inicial, siguiente_estado


def pedir_entero(mensaje, minimo=1):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and int(valor) >= minimo:
            return int(valor)
        print(f"Escribe un numero entero mayor o igual a {minimo}.")


def nombre_ruta(red, estado):
    nombres = []
    for paso in estado["recorrido"]:
        servicio = paso["servicio"]
        nombre = red["servicios"][servicio]["nombre"] if servicio else "Caminata"
        if not nombres or nombres[-1] != nombre:
            nombres.append(nombre)
    return " -> ".join(nombres)


def evaluar_rutas(red, limites):
    """Recorre las alternativas del grafo para compararlas, sin reemplazar Voraz o A*."""
    rutas = []

    def visitar(estado):
        if estado["nodo"] == DESTINO:
            rutas.append(estado)
            return
        for conexion in red["grafo"][estado["nodo"]]:
            nuevo = siguiente_estado(red, estado, conexion, limites)
            if nuevo is not None:
                visitar(nuevo)

    visitar(estado_inicial(ORIGEN))
    directa = [r for r in rutas if r["transbordos"] == 0]
    transbordo = [r for r in rutas if r["transbordos"] > 0]
    return [("Directa (La Z)", min(directa, key=lambda r: r["tiempo"], default=None)),
            ("Con transbordo (El Loro)", min(transbordo, key=lambda r: r["tiempo"], default=None))]


def mostrar_resultado(resultado, red):
    print(f"\n--- Algoritmo {resultado['algoritmo']} ---")
    if not resultado["encontrado"]:
        print("No se encontro una ruta completa.")
        print(resultado["motivo"])
    else:
        ruta = {"recorrido": resultado["recorrido"]}
        print("Ruta:", nombre_ruta(red, ruta))
        print("Tiempo:", resultado["tiempo_min"], "minutos")
        print(f"Costo por persona: S/ {resultado['costo_individual']:.2f}")
        print(f"Costo del grupo: S/ {resultado['costo_grupal']:.2f}")
        print("Transbordos:", resultado["transbordos"])
    print("Estados explorados:", resultado["explorados"])
    print(f"Ejecucion: {resultado['ejecucion_ms']:.4f} ms")


def main():
    red = cargar_red()
    limites = crear_limites()
    print("=" * 48)
    print(" BUSCADOR DE RUTAS - VORAZ Y A*")
    print("=" * 48)
    print("Origen: Santa Clara, Ate")
    print("Destino: Av. Abancay, Cercado de Lima")
    print("Limites: S/ 5 por persona, 90 min, 2 transbordos")
    pasajeros = pedir_entero("\nNumero de pasajeros: ")
    print("\n1. Voraz\n2. A*\n3. Comparar ambos")
    opcion = pedir_entero("Elige una opcion (1-3): ")
    while opcion not in (1, 2, 3):
        opcion = pedir_entero("Elige 1, 2 o 3: ")

    if opcion in (1, 3):
        mostrar_resultado(voraz(red, ORIGEN, DESTINO, limites, pasajeros), red)
    if opcion in (2, 3):
        mostrar_resultado(a_estrella(red, ORIGEN, DESTINO, limites, pasajeros), red)

    print("\n--- Comparacion de rutas ---")
    alternativas = evaluar_rutas(red, limites)
    tiempos = [ruta["tiempo"] for _, ruta in alternativas if ruta is not None]
    mejor = min(tiempos) if tiempos else None
    for nombre, ruta in alternativas:
        if ruta is None:
            print(f"{nombre}: No disponible")
            continue
        diferencia = ruta["tiempo"] - mejor
        etiqueta = "RECOMENDADA" if diferencia == 0 else f"NO RECOMENDADA POR TIEMPO (+{diferencia} min)"
        print(f"{nombre}: {ruta['tiempo']} min | S/ {ruta['costo_centimos']/100:.2f} por persona | "
              f"S/ {ruta['costo_centimos']*pasajeros/100:.2f} grupo | {etiqueta}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma finalizado.")
