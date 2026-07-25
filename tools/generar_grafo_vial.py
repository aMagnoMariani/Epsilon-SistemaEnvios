"""
Descarga el grafo vial real de Maturín y lo guarda como:
1. datos/grafo_vial.graphml — grafo completo de calles para routing
2. datos/mapa_nodos.json — sectores de interés anclados al nodo más cercano del grafo
"""
import json
import os
import pickle

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GRAPHML_FILE = os.path.join(BASE_DIR, 'datos', 'grafo_vial.graphml')
PICKLE_FILE = os.path.join(BASE_DIR, 'datos', 'grafo_vial.pkl')
NODOS_REF_FILE = os.path.join(BASE_DIR, 'datos', 'mapa_nodos.json')

import osmnx as ox
import networkx as nx
from shapely.geometry import Point

LAT_CENTER = 9.7456
LNG_CENTER = -63.1832
RADIUS = 6000  # 6 km para cubrir bien Maturín

print(f'Descargando grafo vial de Maturín (radio {RADIUS}m)...')

G = ox.graph_from_point(
    (LAT_CENTER, LNG_CENTER),
    dist=RADIUS,
    network_type='drive',
    simplify=True,
    retain_all=False
)

print(f'Grafo vial: {len(G.nodes)} nodos, {len(G.edges)} aristas')

for u, v, key, data in G.edges(keys=True, data=True):
    speed = data.get('maxspeed', None)
    if isinstance(speed, list):
        speed = speed[0] if speed else None
    if isinstance(speed, str):
        try:
            speed = float(speed)
        except ValueError:
            speed = None
    highway = data.get('highway', '')
    if isinstance(highway, list):
        highway = highway[0] if highway else ''
    if speed is None or not isinstance(speed, (int, float)) or speed <= 0:
        if highway in ('motorway', 'motorway_link'):
            speed = 80
        elif highway in ('trunk', 'trunk_link'):
            speed = 60
        elif highway in ('primary', 'primary_link'):
            speed = 50
        elif highway in ('secondary', 'secondary_link'):
            speed = 40
        elif highway in ('tertiary', 'tertiary_link'):
            speed = 30
        else:
            speed = 25

    length_km = data.get('length', 0.0) / 1000.0
    tiempo_min = round(length_km / speed * 60, 1)
    if tiempo_min < 0.1:
        tiempo_min = 0.1
    costo_gas = round(length_km * 0.7, 1)
    if costo_gas < 0.1:
        costo_gas = 0.1

    data['tiempo'] = tiempo_min
    data['costo_gasolina'] = costo_gas
    data['length_km'] = round(length_km, 3)
    data['speed_kph'] = speed

print('Atributos calculados: costo_gasolina, tiempo, speed_kph')

ox.save_graphml(G, GRAPHML_FILE)
print(f'Grafo guardado: {GRAPHML_FILE}')

with open(PICKLE_FILE, 'wb') as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
print(f'Pickle cache: {PICKLE_FILE}')

sectores = {
    'Almacen_Central': (9.7456, -63.1832),
    'Sector_A': (9.7532, -63.1875),
    'Sector_B': (9.7440, -63.1710),
    'Sector_C': (9.7365, -63.1895),
    'Sector_D': (9.7484, -63.1608),
    'Sector_E': (9.7318, -63.1790),
    'Sector_F': (9.7560, -63.1960),
    'Sector_G': (9.7420, -63.2045),
    'Sector_H': (9.7598, -63.1690),
}

nodos_ref = {}
for nombre, (lat, lng) in sectores.items():
    node_id, dist = ox.distance.nearest_nodes(G, lng, lat, return_dist=True)
    nodos_ref[nombre] = {
        'node_id': str(node_id),
        'lat': lat,
        'lng': lng,
        'osm_node_lat': G.nodes[node_id]['y'],
        'osm_node_lng': G.nodes[node_id]['x'],
        'distancia_al_nodo': round(dist, 1)
    }
    print(f'  {nombre}: anclado a nodo OSM {node_id} (a {dist:.0f}m)')

with open(NODOS_REF_FILE, 'w', encoding='utf-8') as f:
    json.dump(nodos_ref, f, ensure_ascii=False, indent=2)

print(f'Nodos de referencia guardados: {NODOS_REF_FILE}')
print(f'Total sectores anclados: {len(nodos_ref)}')

mapa_json_out = os.path.join(BASE_DIR, 'datos', 'mapa.json')
mapa_manual_bak = os.path.join(BASE_DIR, 'datos', 'mapa_manual.json')
if os.path.exists(mapa_json_out):
    import shutil
    shutil.copy(mapa_json_out, mapa_manual_bak)
    print(f'Backup mapa manual → {mapa_manual_bak}')

mapa_simple = {
    'nodos': {n: {'lat': i['lat'], 'lng': i['lng']} for n, i in nodos_ref.items()},
    'aristas': []
}
with open(mapa_json_out, 'w', encoding='utf-8') as f:
    json.dump(mapa_simple, f, ensure_ascii=False, indent=2)
print(f'mapa.json simplificado (solo sectores, sin aristas fijas)')
print('¡Listo!')