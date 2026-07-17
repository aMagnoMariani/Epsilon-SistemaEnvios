"""
Módulo Mapa Logístico — Unidad IV
Grafo ponderado con algoritmo de Dijkstra para cálculo de rutas óptimas.

REPRESENTACIÓN ELEGIDA:
- Se utiliza una LISTA DE ADYACENCIA implementada como diccionario de diccionarios.
- Estructura: {nodo_origen: {nodo_destino: {'gasolina': costo, 'tiempo': costo}, ...}, ...}
- Esta representación es eficiente para grafos dispersos (pocos arcos respecto a nodos).
- Permite acceso O(1) a los vecinos de un nodo y O(1) al costo de una arista específica.

ALGORITMO DE RECORRIDO:
- Se implementa el algoritmo de DIJKSTRA para encontrar la ruta de menor costo.
- Utiliza una cola de prioridad (heapq) para siempre procesar el nodo con menor costo acumulado.
- Complejidad: O((V + E) log V) donde V es el número de vértices y E el número de aristas.
- Garantiza encontrar la ruta óptima (menor costo) en grafos con pesos no negativos.

LIMITACIONES:
- No maneja pesos negativos (Dijkstra no es adecuado para esto).
- Para grafos muy densos, una matriz de adyacencia podría ser más eficiente en memoria.
- El algoritmo recalcula la ruta completa cada vez (no hay caché de rutas).
"""

import heapq
import math
from persistencia import cargar_datos


class MapaLogistico:
    """Representa el mapa de la ciudad como un grafo ponderado.
    
    Los pesos representan el costo de combustible (combinación de
    distancia, tráfico promedio y topografía).
    Se implementa como una Lista de Adyacencia (diccionario de diccionarios).
    """

    def __init__(self, archivo_mapa: str = None):
        # Lista de adyacencia: {nodo: {vecino: {'gasolina': costo, 'tiempo': costo}, ...}, ...}
        # Esta estructura permite acceso eficiente a vecinos y costos
        self.grafo = {}
        
        # Coordenadas geográficas: {nodo: {'lat': lat, 'lng': lng}}
        # Utilizadas para cálculos de distancia directa (Haversine)
        self.coordenadas = {}
        
        # Descripciones de las aristas: {(origen, destino): 'descripción'}
        # Proporcionan contexto sobre cada ruta
        self.descripciones = {}

        
        if archivo_mapa:
            self.cargar_mapa(archivo_mapa)

    def cargar_mapa(self, archivo: str) -> None:
        """Carga el mapa desde un archivo JSON y construye la lista de adyacencia.
        
        Proceso:
        1. Lee el archivo JSON con la definición del grafo.
        2. Inicializa todos los nodos con sus coordenadas geográficas.
        3. Agrega las aristas (conexiones) entre nodos con sus pesos.
        4. El grafo es bidireccional (si A conecta con B, B conecta con A).
        
        Args:
            archivo: Ruta al archivo JSON con la definición del grafo.
        
        Formato esperado del JSON:
        {
            "nodos": {
                "Almacen_Central": {"lat": -33.45, "lng": -70.66},
                "Sector_A": {"lat": -33.46, "lng": -70.67}
            },
            "aristas": [
                {"origen": "Almacen_Central", "destino": "Sector_A", 
                 "costo_gasolina": 5.2, "tiempo": 15, "descripcion": "Av. Principal"}
            ]
        }
        """
        datos = cargar_datos(archivo)
        
        if not datos:
            return

        # Si es una lista, tomar el primer elemento (compatibilidad)
        if isinstance(datos, list):
            datos = datos[0] if datos else {}

        # Inicializar todos los nodos y sus coordenadas
        nodos_data = datos.get('nodos', {})
        if isinstance(nodos_data, dict):
            for nodo, coords in nodos_data.items():
                if nodo not in self.grafo:
                    self.grafo[nodo] = {}
                self.coordenadas[nodo] = coords
        else:
            # Fallback en caso de que aún sea una lista vieja
            for nodo in nodos_data:
                if nodo not in self.grafo:
                    self.grafo[nodo] = {}

        # Agregar aristas (bidireccionales)
        # Cada arista representa una conexión entre dos sectores con un costo
        for arista in datos.get('aristas', []):
            origen = arista['origen']
            destino = arista['destino']
            costo_gasolina = arista.get('costo_gasolina', arista.get('costo', 1))
            tiempo = arista.get('tiempo', costo_gasolina)
            descripcion = arista.get('descripcion', '')

            # Asegurar que los nodos existen
            if origen not in self.grafo:
                self.grafo[origen] = {}
            if destino not in self.grafo:
                self.grafo[destino] = {}

            # Grafo bidireccional: la conexión funciona en ambos sentidos
            self.grafo[origen][destino] = {'gasolina': costo_gasolina, 'tiempo': tiempo}
            self.grafo[destino][origen] = {'gasolina': costo_gasolina, 'tiempo': tiempo}

            # Guardar descripciones para ambos sentidos
            self.descripciones[(origen, destino)] = descripcion
            self.descripciones[(destino, origen)] = descripcion

    def _distancia_haversine(self, coord_a: dict, coord_b: dict) -> float:
        """Calcula la distancia en kilómetros entre dos coordenadas geográficas.
        
        Utiliza la fórmula de Haversine que calcula la distancia del gran círculo
        entre dos puntos en una esfera (la Tierra) dados sus latitudes y longitudes.
        
        Fórmula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1−a))
        d = R * c
        
        Donde R es el radio de la Tierra (6371 km).
        
        Args:
            coord_a: Diccionario con 'lat' y 'lng' del primer punto.
            coord_b: Diccionario con 'lat' y 'lng' del segundo punto.

        Returns:
            Distancia aproximada en kilómetros.
        """
        radio_tierra = 6371.0  # Radio de la Tierra en kilómetros
        lat1, lon1 = math.radians(coord_a['lat']), math.radians(coord_a['lng'])
        lat2, lon2 = math.radians(coord_b['lat']), math.radians(coord_b['lng'])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radio_tierra * c

    def _estimacion_tiempo_directo(self, distancia_km: float) -> float:
        """Estima el tiempo de viaje directo en minutos para la ruta más rápida.
        
        Utiliza una velocidad promedio urbana de 40 km/h para estimar el tiempo.
        Esta estimación se usa cuando se selecciona la estrategia 'tiempo' y
        se prefiere una ruta directa sin paradas intermedias.
        
        Args:
            distancia_km: Distancia en kilómetros entre origen y destino.
        
        Returns:
            Tiempo estimado en minutos (mínimo 2 minutos).
        """
        velocidad_promedio_kmh = 40.0  # Velocidad promedio en zona urbana
        minutos = (distancia_km / velocidad_promedio_kmh) * 60
        return round(max(minutos, 2), 1)  # Mínimo 2 minutos

    def calcular_ruta(self, origen: str, destino: str, estrategia: str = 'gasolina') -> tuple:
        """Calcula la ruta de menor costo usando el algoritmo de Dijkstra.
        
        ALGORITMO DIJKSTRA:
        1. Inicializar todas las distancias como infinito excepto el origen (0).
        2. Usar una cola de prioridad (min-heap) para siempre procesar el nodo con menor costo.
        3. Para cada nodo procesado, relajar las aristas hacia sus vecinos.
        4. Si encontramos un camino más corto a un vecino, actualizar su distancia y predecesor.
        5. Continuar hasta llegar al destino o procesar todos los nodos alcanzables.
        6. Reconstruir el camino siguiendo los predecesores desde el destino al origen.
        
        COMPLEJIDAD: O((V + E) log V)
        - V: número de vértices (nodos/sectores)
        - E: número de aristas (conexiones)
        - log V: costo de operaciones en el heap
        
        Args:
            origen: Nodo de origen (ej: 'Almacen_Central').
            destino: Nodo de destino (ej: 'Sector_C').
            estrategia: 'gasolina' (minimiza consumo) o 'tiempo' (ruta directa).
        
        Returns:
            Tupla (costo_total, camino, detalles) donde:
            - costo_total: Costo total (combustible o tiempo) de la ruta.
            - camino: Lista de nodos en orden ['Almacen_Central', 'Sector_A', 'Sector_C'].
            - detalles: Lista de diccionarios con info de cada tramo.
            Retorna (float('inf'), [], []) si no hay ruta posible.
        """
        # Estrategia 'tiempo': retorna ruta directa estimada (sin Dijkstra)
        if estrategia == 'tiempo':
            if origen not in self.coordenadas or destino not in self.coordenadas:
                return (float('inf'), [], [])
            if origen == destino:
                return (0, [origen], [])

            distancia = self._distancia_haversine(self.coordenadas[origen], self.coordenadas[destino])
            tiempo_est = self._estimacion_tiempo_directo(distancia)
            detalles = [{
                'desde': origen,
                'hasta': destino,
                'costo': tiempo_est,
                'pesos_completos': {'gasolina': None, 'tiempo': tiempo_est},
                'descripcion': 'Ruta directa más rápida sin paradas intermedias.'
            }]
            return (tiempo_est, [origen, destino], detalles)

        # Verificar que ambos nodos existen en el grafo
        if origen not in self.grafo or destino not in self.grafo:
            return (float('inf'), [], [])

        # PASO 1: Inicializar distancias y predecesores
        # distancias: costo mínimo conocido desde el origen a cada nodo
        distancias = {nodo: float('inf') for nodo in self.grafo}
        distancias[origen] = 0  # Distancia al origen es 0

        # predecesores: nodo anterior en el camino más corto (para reconstrucción)
        predecesores = {nodo: None for nodo in self.grafo}

        # PASO 2: Cola de prioridad (min-heap)
        # Almacena tuplas (costo_acumulado, nodo)
        # heapq siempre retorna el elemento con menor costo
        cola = [(0, origen)]

        # Conjunto de nodos ya procesados (optimización)
        visitados = set()

        # PASO 3: Bucle principal de Dijkstra
        while cola:
            # Extraer el nodo con menor costo acumulado
            costo_actual, nodo_actual = heapq.heappop(cola)

            # Si ya procesamos este nodo, saltar (puede estar duplicado en el heap)
            if nodo_actual in visitados:
                continue

            visitados.add(nodo_actual)

            # Si llegamos al destino, podemos terminar (Dijkstra garantiza optimalidad)
            if nodo_actual == destino:
                break

            # PASO 4: Relajar aristas hacia los vecinos
            # Explorar todos los nodos conectados al nodo actual
            for vecino, pesos in self.grafo[nodo_actual].items():
                if vecino in visitados:
                    continue  # Ya procesado, no necesitamos revisarlo

                # Obtener el costo de la arista según la estrategia
                costo_arista = pesos.get(estrategia, pesos['gasolina'])
                nuevo_costo = costo_actual + costo_arista

                # Si encontramos un camino más corto al vecino, actualizar
                if nuevo_costo < distancias[vecino]:
                    distancias[vecino] = nuevo_costo
                    predecesores[vecino] = nodo_actual
                    # Agregar a la cola de prioridad
                    heapq.heappush(cola, (nuevo_costo, vecino))

        # PASO 5: Verificar si se encontró una ruta
        if distancias[destino] == float('inf'):
            return (float('inf'), [], [])  # No hay ruta posible

        # PASO 6: Reconstruir el camino desde destino hacia origen
        camino = []
        nodo = destino
        while nodo is not None:
            camino.append(nodo)
            nodo = predecesores[nodo]
        camino.reverse()  # Invertir para tener origen -> destino

        # PASO 7: Construir detalles del camino para mostrar al usuario
        detalles = []
        for i in range(len(camino) - 1):
            tramo_origen = camino[i]
            tramo_destino = camino[i + 1]
            pesos = self.grafo[tramo_origen][tramo_destino]
            costo = pesos.get(estrategia, pesos['gasolina'])
            desc = self.descripciones.get((tramo_origen, tramo_destino), '')
            detalles.append({
                'desde': tramo_origen,
                'hasta': tramo_destino,
                'costo': costo,
                'pesos_completos': pesos,
                'descripcion': desc
            })

        return (distancias[destino], camino, detalles)

    def obtener_nodos(self) -> list:
        """Retorna la lista de todos los nodos (sectores) del grafo.
        
        Útil para mostrar opciones al usuario o para iterar sobre todos los sectores.
        
        Returns:
            Lista de strings con los nombres de los nodos.
        
        Complejidad: O(V) donde V es el número de vértices.
        """
        return list(self.grafo.keys())

    def obtener_aristas(self) -> list:
        """Retorna la lista de todas las aristas del grafo sin duplicados.
        
        Como el grafo es bidireccional, cada conexión aparece dos veces
        (A->B y B->A). Este método elimina duplicados retornando cada arista
        solo una vez.
        
        Returns:
            Lista de diccionarios con origen, destino, costo_gasolina, tiempo y descripcion.
        
        Complejidad: O(E) donde E es el número de aristas.
        """
        aristas = []
        visitadas = set()  # Para evitar duplicados en grafo bidireccional
        
        for origen in self.grafo:
            for destino, pesos in self.grafo[origen].items():
                # Crear un par ordenado para identificar aristas únicas
                par = tuple(sorted([origen, destino]))
                if par not in visitadas:
                    visitadas.add(par)
                    desc = self.descripciones.get((origen, destino), '')
                    aristas.append({
                        'origen': origen,
                        'destino': destino,
                        'costo_gasolina': pesos.get('gasolina', 0),
                        'tiempo': pesos.get('tiempo', 0),
                        'descripcion': desc
                    })
        return aristas

    def obtener_destinos(self) -> list:
        """Retorna todos los nodos excepto el Almacén Central (destinos posibles).
        
        Útil para mostrar opciones de destino al usuario en el formulario de órdenes,
        ya que el Almacén Central es el punto de partida y no un destino.
        
        Returns:
            Lista de strings con los nombres de los destinos.
        
        Complejidad: O(V) donde V es el número de vértices.
        """
        return [n for n in self.grafo.keys() if n != 'Almacen_Central']
