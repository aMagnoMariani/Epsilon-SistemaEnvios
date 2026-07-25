"""
Módulo Mapa Logístico — Grafo vial real de Maturín con rutas sobre calles (Dijkstra).
Depende de datos/grafo_vial.pkl (generado con tools/generar_grafo_vial.py) — si no existe opera con coordenadas Haversine.
"""

import os
import json
import pickle
import math
import heapq
import networkx as nx
from persistencia import cargar_datos


class MapaLogistico:
    """Mapa logístico con grafo vial real de Maturín."""

    def __init__(self, archivo_mapa: str = None):
        self.grafo = {}           # {nombre_sector: {vecino: {gasolina, tiempo}, ...}, ...}
        self.coordenadas = {}     # {nombre_sector: {lat, lng}}
        self.descripciones = {}   # {(origen, destino): descripcion}
        self.waypoints = {}       # {(origen, destino): [{lat, lng}, ...]}

        self.grafo_vial = None    # NetworkX MultiDiGraph — grafo vial real
        self.nodos_ref = {}       # {nombre_sector: osm_node_id}

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self._grafo_vial_path = os.path.join(BASE_DIR, 'datos', 'grafo_vial.pkl')
        self._nodos_ref_path = os.path.join(BASE_DIR, 'datos', 'mapa_nodos.json')

        self._cargar_grafo_vial()

        if archivo_mapa:
            self.cargar_mapa(archivo_mapa)

    def _cargar_grafo_vial(self):
        """Carga el grafo vial real desde pickle cache o graphml."""
        if os.path.exists(self._grafo_vial_path):
            with open(self._grafo_vial_path, 'rb') as f:
                self.grafo_vial = pickle.load(f)

        if self.grafo_vial is None and os.path.exists(self._grafo_vial_path.replace('.pkl', '.graphml')):
            import osmnx as ox
            self.grafo_vial = ox.load_graphml(self._grafo_vial_path.replace('.pkl', '.graphml'))

        if os.path.exists(self._nodos_ref_path):
            with open(self._nodos_ref_path, 'r') as f:
                self.nodos_ref = json.load(f)

    def _nodo_a_osm(self, nombre: str):
        """Convierte nombre de sector a node_id del grafo vial."""
        if nombre in self.nodos_ref:
            return self.nodos_ref[nombre]['node_id']
        return nombre

    def cargar_mapa(self, archivo: str) -> None:
        datos = cargar_datos(archivo)
        if not datos:
            return

        if isinstance(datos, list):
            datos = datos[0] if datos else {}

        nodos_data = datos.get('nodos', {})
        if isinstance(nodos_data, dict):
            for nodo, coords in nodos_data.items():
                if nodo not in self.grafo:
                    self.grafo[nodo] = {}
                self.coordenadas[nodo] = coords

        for arista in datos.get('aristas', []):
            origen = arista['origen']
            destino = arista['destino']
            costo_gasolina = arista.get('costo_gasolina', arista.get('costo', 1))
            tiempo = arista.get('tiempo', costo_gasolina)
            descripcion = arista.get('descripcion', '')

            if origen not in self.grafo:
                self.grafo[origen] = {}
            if destino not in self.grafo:
                self.grafo[destino] = {}

            self.grafo[origen][destino] = {'gasolina': costo_gasolina, 'tiempo': tiempo}
            self.grafo[destino][origen] = {'gasolina': costo_gasolina, 'tiempo': tiempo}
            self.descripciones[(origen, destino)] = descripcion
            self.descripciones[(destino, origen)] = descripcion

            waypoints_data = arista.get('waypoints', [])
            if waypoints_data:
                self.waypoints[(origen, destino)] = waypoints_data
                self.waypoints[(destino, origen)] = list(reversed(waypoints_data))

    def _interpolar_waypoints(self, waypoints: list, paso_metros: float = 15) -> list:
        """Interpola puntos adicionales entre waypoints para mayor precisión.

        Cada ~paso_metros se inserta un punto intermedio, haciendo que la
        polilínea siga fielmente las curvas reales de las calles.
        """
        if not waypoints or len(waypoints) < 2:
            return waypoints

        resultado = [waypoints[0]]
        radio_tierra = 6371000.0

        for i in range(len(waypoints) - 1):
            a = waypoints[i]
            b = waypoints[i + 1]

            dlat = math.radians(b['lat'] - a['lat'])
            dlng = math.radians(b['lng'] - a['lng'])
            lat_a_rad = math.radians(a['lat'])
            lat_b_rad = math.radians(b['lat'])

            a_hav = math.sin(dlat / 2) ** 2 + math.cos(lat_a_rad) * math.cos(lat_b_rad) * math.sin(dlng / 2) ** 2
            c_hav = 2 * math.atan2(math.sqrt(a_hav), math.sqrt(1 - a_hav))
            distancia_m = radio_tierra * c_hav

            if distancia_m <= paso_metros:
                resultado.append(b)
                continue

            num_pasos = int(distancia_m / paso_metros)
            for j in range(1, num_pasos + 1):
                t = j / (num_pasos + 1)
                lat_inter = a['lat'] + t * (b['lat'] - a['lat'])
                lng_inter = a['lng'] + t * (b['lng'] - a['lng'])
                resultado.append({'lat': lat_inter, 'lng': lng_inter})
            resultado.append(b)

        return resultado

    def _distancia_haversine(self, coord_a: dict, coord_b: dict) -> float:
        radio_tierra = 6371.0
        lat1, lon1 = math.radians(coord_a['lat']), math.radians(coord_a['lng'])
        lat2, lon2 = math.radians(coord_b['lat']), math.radians(coord_b['lng'])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radio_tierra * c

    def _estimacion_tiempo_directo(self, distancia_km: float) -> float:
        velocidad_promedio_kmh = 40.0
        minutos = (distancia_km / velocidad_promedio_kmh) * 60
        return round(max(minutos, 2), 1)

    def _ruta_vial(self, origen_nombre: str, destino_nombre: str, weight: str) -> tuple:
        """Calcula ruta sobre el grafo vial real usando Dijkstra (NetworkX).

        Returns:
            (costo_total, waypoints_geo, nombres_sectores_en_ruta)
            waypoints_geo: [{lat, lng}, ...] — TODOS los puntos de la ruta sobre calles
        """
        if self.grafo_vial is None:
            return (float('inf'), [], [])

        osm_origen = self._nodo_a_osm(origen_nombre)
        osm_destino = self._nodo_a_osm(destino_nombre)

        try:
            osm_origen_int = int(osm_origen)
            osm_destino_int = int(osm_destino)
        except (ValueError, TypeError):
            return (float('inf'), [], [])

        if osm_origen_int not in self.grafo_vial.nodes or osm_destino_int not in self.grafo_vial.nodes:
            return (float('inf'), [], [])

        try:
            path_nodes = nx.shortest_path(
                self.grafo_vial,
                osm_origen_int,
                osm_destino_int,
                weight=weight,
                method='dijkstra'
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return (float('inf'), [], [])

        waypoints_geo = []
        costo_total = 0.0

        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]

            edge_data = self.grafo_vial.get_edge_data(u, v)
            if edge_data is None:
                edge_data = self.grafo_vial.get_edge_data(v, u)

            if edge_data:
                data = list(edge_data.values())[0]

                costo = data.get(weight, data.get('costo_gasolina', data.get('length', 0) / 1000 * 0.7))
                costo_total += costo

                if 'geometry' in data:
                    geom = data['geometry']
                    if hasattr(geom, 'coords'):
                        for pt in geom.coords:
                            waypoints_geo.append({'lat': pt[1], 'lng': pt[0]})
                    elif hasattr(geom, 'geoms'):
                        for ls in geom.geoms:
                            for pt in ls.coords:
                                waypoints_geo.append({'lat': pt[1], 'lng': pt[0]})

        if waypoints_geo:
            seen = set()
            dedup = []
            for w in waypoints_geo:
                key = (round(w['lat'], 8), round(w['lng'], 8))
                if key not in seen:
                    seen.add(key)
                    dedup.append(w)
            waypoints_geo = dedup

            interpolados = self._interpolar_waypoints(waypoints_geo, paso_metros=15)
            waypoints_geo = interpolados

        sectores_en_ruta = [origen_nombre, destino_nombre]

        return (round(costo_total, 1), waypoints_geo, sectores_en_ruta)

    def calcular_ruta(self, origen: str, destino: str, estrategia: str = 'gasolina') -> tuple:
        """Calcula la ruta óptima entre origen y destino.

        ESTRATEGIA 'gasolina' (ahorro):
        - Recorre los sectores del grafo manual (self.coordenadas) del más cercano 
          al más lejano desde el origen hacia el destino.
        - Algoritmo greedy: desde el origen, elige el sector no visitado más cercano
          que reduzca la distancia al destino, lo visita, y continúa.
        - Cada tramo entre sectores consecutivos se resuelve con el grafo vial real,
          concatenando waypoints y sumando costos.
        - Simula un camión de reparto haciendo paradas por los sectores cercanos.

        ESTRATEGIA 'tiempo' (rápida):
        - Ruta directa origen → destino sobre el grafo vial real sin paradas intermedias.

        Returns:
            (costo_total, camino_waypoints, detalles)
            camino_waypoints: [{lat, lng}, ...] — ruta geográfica completa
        """
        if origen not in self.coordenadas or destino not in self.coordenadas:
            return (float('inf'), [], [])

        if origen == destino:
            return (0, [{'lat': self.coordenadas[origen]['lat'], 'lng': self.coordenadas[origen]['lng']}], [])

        if estrategia == 'tiempo':
            if self.grafo_vial is not None:
                cost, wpts, _ = self._ruta_vial(origen, destino, 'tiempo')
                if wpts:
                    detalles = self._extraer_detalles_viales(origen, destino, 'tiempo')
                    return (cost, wpts, detalles)
            dist = self._distancia_haversine(self.coordenadas[origen], self.coordenadas[destino])
            tiempo_est = self._estimacion_tiempo_directo(dist)
            wpts = [self.coordenadas[origen], self.coordenadas[destino]]
            return (tiempo_est, wpts, [{'desde': origen, 'hasta': destino, 'costo': tiempo_est, 'descripcion': 'Ruta directa'}])

        dist = self._distancia_haversine
        dist_origen_destino = dist(self.coordenadas[origen], self.coordenadas[destino])
        sectores_intermedios = []
        for n in self.coordenadas:
            if n == origen or n == destino:
                continue
            d_origen = dist(self.coordenadas[origen], self.coordenadas[n])
            d_destino = dist(self.coordenadas[n], self.coordenadas[destino])
            if d_origen < dist_origen_destino and d_destino < dist_origen_destino:
                sectores_intermedios.append(n)

        no_visitados = list(sectores_intermedios)
        ruta_sectores = [origen]
        actual = origen

        while no_visitados:
            mejor_vecino = None
            mejor_dist = float('inf')

            for vecino in no_visitados:
                d = dist(self.coordenadas[actual], self.coordenadas[vecino])
                if d < mejor_dist:
                    mejor_dist = d
                    mejor_vecino = vecino

            if mejor_vecino is None:
                break
            ruta_sectores.append(mejor_vecino)
            no_visitados.remove(mejor_vecino)
            actual = mejor_vecino

        ruta_sectores.append(destino)

        waypoints_totales = []
        todos_detalles = []
        costo_total = 0.0

        for i in range(len(ruta_sectores) - 1):
            a, b = ruta_sectores[i], ruta_sectores[i + 1]
            if self.grafo_vial is not None:
                c, w, _ = self._ruta_vial(a, b, 'costo_gasolina')
            else:
                w = [self.coordenadas[a], self.coordenadas[b]]
                c = self._distancia_haversine(self.coordenadas[a], self.coordenadas[b]) * 0.7

            costo_total += c
            nombre_calle = self._obtener_calle_principal(a, b)
            todos_detalles.append({
                'desde': a, 'hasta': b,
                'costo': round(c, 1),
                'descripcion': nombre_calle or f'{a} → {b}'
            })
            waypoints_totales.extend(w)

        if waypoints_totales:
            seen = set()
            dedup = []
            for w in waypoints_totales:
                key = (round(w['lat'], 8), round(w['lng'], 8))
                if key not in seen:
                    seen.add(key)
                    dedup.append(w)
            waypoints_totales = dedup
            waypoints_totales = self._interpolar_waypoints(waypoints_totales, paso_metros=15)

        return (round(costo_total, 1), waypoints_totales, todos_detalles)

    def _extraer_detalles_viales(self, origen, destino, weight):
        osm_origen = self._nodo_a_osm(origen)
        osm_destino = self._nodo_a_osm(destino)
        nombre_aristas = []
        try:
            path_nodes = nx.shortest_path(
                self.grafo_vial,
                int(osm_origen), int(osm_destino),
                weight=weight, method='dijkstra'
            )
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i + 1]
                edge = self.grafo_vial.get_edge_data(u, v)
                if edge is None:
                    edge = self.grafo_vial.get_edge_data(v, u)
                if edge:
                    data = list(edge.values())[0]
                    name = data.get('name', '')
                    if isinstance(name, list):
                        name = name[0] if name else ''
                    c = data.get(weight, 0)
                    nombre_aristas.append({
                        'desde': str(u), 'hasta': str(v),
                        'costo': round(c, 1),
                        'descripcion': name or 'Calle sin nombre'
                    })
        except Exception:
            pass
        return nombre_aristas

    def _obtener_calle_principal(self, origen, destino):
        if self.grafo_vial is None:
            return ''
        try:
            o = int(self._nodo_a_osm(origen))
            d = int(self._nodo_a_osm(destino))
            if o in self.grafo_vial.nodes and d in self.grafo_vial.nodes:
                path_nodes = nx.shortest_path(self.grafo_vial, o, d, weight='costo_gasolina', method='dijkstra')
                todos_nombres = []
                for i in range(len(path_nodes) - 1):
                    u, v = path_nodes[i], path_nodes[i + 1]
                    edge = self.grafo_vial.get_edge_data(u, v)
                    if edge is None:
                        edge = self.grafo_vial.get_edge_data(v, u)
                    if edge:
                        data = list(edge.values())[0]
                        name = data.get('name', '')
                        if isinstance(name, list):
                            name = name[0] if name else ''
                        if name and name not in todos_nombres:
                            todos_nombres.append(name)
                return ' → '.join(todos_nombres[:3]) if todos_nombres else 'Calle sin nombre'
        except Exception:
            pass
        return ''

    def obtener_nodos(self) -> list:
        return list(self.coordenadas.keys())

    def obtener_aristas(self) -> list:
        aristas = []
        visitadas = set()
        for origen in self.grafo:
            for destino, pesos in self.grafo[origen].items():
                par = tuple(sorted([origen, destino]))
                if par not in visitadas:
                    visitadas.add(par)
                    desc = self.descripciones.get((origen, destino), '')
                    wps = self.waypoints.get((origen, destino), [])
                    aristas.append({
                        'origen': origen, 'destino': destino,
                        'costo_gasolina': pesos.get('gasolina', 0),
                        'tiempo': pesos.get('tiempo', 0),
                        'descripcion': desc, 'waypoints': wps
                    })
        return aristas

    def recorrido_bfs(self, origen: str) -> list:
        if origen not in self.grafo:
            return []
        visitados = set([origen])
        cola = [origen]
        orden = []
        while cola:
            actual = cola.pop(0)
            orden.append(actual)
            for vecino in self.grafo.get(actual, {}):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)
        return orden

    def recorrido_dfs(self, origen: str) -> list:
        if origen not in self.grafo:
            return []
        visitados = set()
        pila = [origen]
        orden = []
        while pila:
            actual = pila.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            orden.append(actual)
            for vecino in sorted(self.grafo.get(actual, {}).keys(), reverse=True):
                if vecino not in visitados:
                    pila.append(vecino)
        return orden

    def es_conexo(self) -> bool:
        if not self.grafo:
            return True
        origen = next(iter(self.grafo))
        visitados = self.recorrido_dfs(origen)
        return len(visitados) == len(self.grafo)

    def agregar_nodo(self, nombre: str, lat: float, lng: float) -> bool:
        if nombre in self.grafo:
            return False
        self.grafo[nombre] = {}
        self.coordenadas[nombre] = {'lat': lat, 'lng': lng}

        if self.grafo_vial is not None:
            import osmnx as ox
            try:
                osm_node_id, dist = ox.distance.nearest_nodes(self.grafo_vial, lng, lat, return_dist=True)
                self.nodos_ref[nombre] = {
                    'node_id': str(osm_node_id),
                    'lat': lat, 'lng': lng,
                    'osm_node_lat': self.grafo_vial.nodes[osm_node_id]['y'],
                    'osm_node_lng': self.grafo_vial.nodes[osm_node_id]['x'],
                    'distancia_al_nodo': round(dist, 1)
                }
            except Exception:
                pass

        return True

    def to_dict(self) -> dict:
        nodos_dict = {}
        for nombre, coords in self.coordenadas.items():
            nodos_dict[nombre] = {'lat': coords['lat'], 'lng': coords['lng']}
        aristas_list = []
        visitadas = set()
        for origen in self.grafo:
            for destino, pesos in self.grafo[origen].items():
                par = tuple(sorted([origen, destino]))
                if par not in visitadas:
                    visitadas.add(par)
                    wps = self.waypoints.get((origen, destino), [])
                    aristas_list.append({
                        'origen': origen, 'destino': destino,
                        'costo_gasolina': pesos.get('gasolina', 0),
                        'tiempo': pesos.get('tiempo', 0),
                        'descripcion': self.descripciones.get((origen, destino), ''),
                        'waypoints': wps
                    })
        return {'nodos': nodos_dict, 'aristas': aristas_list}

    def agregar_arista(self, origen: str, destino: str, costo_gasolina: float = 1.0,
                       tiempo: float = 1.0, descripcion: str = '',
                       waypoints: list = None) -> bool:
        if origen not in self.grafo or destino not in self.grafo:
            return False
        self.grafo[origen][destino] = {'gasolina': costo_gasolina, 'tiempo': tiempo}
        self.grafo[destino][origen] = {'gasolina': costo_gasolina, 'tiempo': tiempo}
        self.descripciones[(origen, destino)] = descripcion
        self.descripciones[(destino, origen)] = descripcion
        if waypoints:
            self.waypoints[(origen, destino)] = waypoints
            self.waypoints[(destino, origen)] = list(reversed(waypoints))
        return True

    def obtener_destinos(self) -> list:
        return [n for n in self.coordenadas.keys() if n != 'Almacen_Central']