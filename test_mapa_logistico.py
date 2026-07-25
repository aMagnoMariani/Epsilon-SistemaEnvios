"""
Pruebas unitarias para MapaLogistico — grafo vial real con Dijkstra y recorridos BFS/DFS.
Verifican carga del mapa, cálculo de rutas sobre calles, recorridos exhaustivos y conectividad.
"""
import pytest
from mapa_logistico import MapaLogistico


def test_creacion_vacia():
    mapa = MapaLogistico()
    assert len(mapa.obtener_nodos()) == 0
    assert len(mapa.obtener_aristas()) == 0


def test_carga_mapa():
    mapa = MapaLogistico()
    mapa.cargar_mapa('datos/mapa.json')

    assert len(mapa.obtener_nodos()) > 0
    assert 'Almacen_Central' in mapa.obtener_nodos()
    assert 'Sector_A' in mapa.obtener_nodos()
    assert 'Sector_B' in mapa.obtener_nodos()


def test_obtener_nodos():
    mapa = MapaLogistico('datos/mapa.json')
    nodos = mapa.obtener_nodos()
    assert 'Almacen_Central' in nodos
    assert 'Sector_A' in nodos
    assert 'Sector_H' in nodos
    assert len(nodos) == 9


def test_obtener_destinos():
    mapa = MapaLogistico('datos/mapa.json')
    destinos = mapa.obtener_destinos()
    assert 'Almacen_Central' not in destinos
    assert 'Sector_A' in destinos
    assert len(destinos) == 8


def test_obtener_aristas():
    mapa = MapaLogistico('datos/mapa.json')
    aristas = mapa.obtener_aristas()
    assert isinstance(aristas, list)


def test_calcular_ruta_gasolina_vial():
    mapa = MapaLogistico('datos/mapa.json')
    costo, waypoints, detalles = mapa.calcular_ruta('Almacen_Central', 'Sector_B', 'gasolina')

    assert costo != float('inf')
    assert len(waypoints) >= 2
    assert 'lat' in waypoints[0] and 'lng' in waypoints[0]
    assert len(detalles) >= 1


def test_calcular_ruta_tiempo_vial():
    mapa = MapaLogistico('datos/mapa.json')
    costo, waypoints, detalles = mapa.calcular_ruta('Almacen_Central', 'Sector_C', 'tiempo')

    assert costo != float('inf')
    assert len(waypoints) >= 2
    assert 'lat' in waypoints[0]


def test_ruta_origen_igual_destino():
    mapa = MapaLogistico('datos/mapa.json')
    costo, waypoints, detalles = mapa.calcular_ruta('Almacen_Central', 'Almacen_Central')

    assert costo == 0
    assert len(waypoints) == 1
    assert waypoints[0]['lat'] == 9.7456
    assert detalles == []


def test_ruta_nodo_inexistente():
    mapa = MapaLogistico('datos/mapa.json')

    costo, camino, detalles = mapa.calcular_ruta('Nodo_Inexistente', 'Sector_A')
    assert costo == float('inf')
    assert camino == []

    costo, camino, detalles = mapa.calcular_ruta('Almacen_Central', 'Nodo_Inexistente')
    assert costo == float('inf')
    assert camino == []


def test_estrategia_tiempo():
    mapa = MapaLogistico('datos/mapa.json')
    costo, waypoints, detalles = mapa.calcular_ruta('Almacen_Central', 'Sector_D', 'tiempo')

    assert costo != float('inf')
    assert len(waypoints) >= 2
    assert 'lat' in waypoints[0]


def test_reorrido_bfs():
    mapa = MapaLogistico('datos/mapa.json')
    orden = mapa.recorrido_bfs('Almacen_Central')

    assert len(orden) == 1
    assert orden[0] == 'Almacen_Central'


def test_bfs_inexistente():
    mapa = MapaLogistico('datos/mapa.json')
    orden = mapa.recorrido_bfs('Nodo_Fantasma')
    assert orden == []


def test_recorrido_dfs():
    mapa = MapaLogistico('datos/mapa.json')
    orden = mapa.recorrido_dfs('Almacen_Central')

    assert len(orden) == 1
    assert orden[0] == 'Almacen_Central'


def test_dfs_inexistente():
    mapa = MapaLogistico('datos/mapa.json')
    orden = mapa.recorrido_dfs('Nodo_Fantasma')
    assert orden == []


def test_es_conexo():
    mapa = MapaLogistico('datos/mapa.json')
    assert mapa.es_conexo() is False


def test_es_conexo_vacio():
    mapa = MapaLogistico()
    assert mapa.es_conexo() is True


def test_ruta_larga_vial():
    mapa = MapaLogistico('datos/mapa.json')
    costo, waypoints, detalles = mapa.calcular_ruta('Almacen_Central', 'Sector_H', 'gasolina')

    assert costo != float('inf')
    assert len(waypoints) >= 2
    for d in detalles:
        assert 'descripcion' in d


def test_descripciones_aristas_vial():
    mapa = MapaLogistico('datos/mapa.json')
    _, _, detalles = mapa.calcular_ruta('Almacen_Central', 'Sector_E', 'gasolina')

    assert len(detalles) > 0
    calles = [d['descripcion'] for d in detalles if d.get('descripcion')]
    assert len(calles) > 0


def test_agregar_nodo():
    mapa = MapaLogistico('datos/mapa.json')
    assert mapa.agregar_nodo('Sector_Z', 9.7500, -63.1900) is True
    assert 'Sector_Z' in mapa.obtener_nodos()
    assert mapa.agregar_nodo('Sector_Z', 9.7500, -63.1900) is False


def test_agregar_arista():
    mapa = MapaLogistico('datos/mapa.json')
    mapa.agregar_nodo('Sector_Z', 9.7500, -63.1900)
    assert mapa.agregar_arista('Almacen_Central', 'Sector_Z', 3.0, 5.0, 'Test', [{'lat': 9.748, 'lng': -63.185}]) is True
    assert 'Sector_Z' in mapa.grafo['Almacen_Central']
    assert mapa.waypoints.get(('Almacen_Central', 'Sector_Z')) is not None
    assert mapa.agregar_arista('Fake_A', 'Fake_B') is False


def test_to_dict():
    mapa = MapaLogistico('datos/mapa.json')
    d = mapa.to_dict()
    assert 'nodos' in d
    assert 'aristas' in d
    assert len(d['nodos']) == 9