"""
Pruebas unitarias para TablaHash.
Verifican inserción, búsqueda, eliminación, manejo de colisiones,
redimensionamiento automático y casos borde.
"""

import pytest
from tabla_hash import TablaHash


def test_creacion_vacia():
    tabla = TablaHash()
    assert len(tabla) == 0
    assert tabla.capacidad == 10
    assert tabla.obtener_todos() == []
    assert tabla.obtener_claves() == []


def test_insertar_y_buscar():
    tabla = TablaHash(capacidad_inicial=5)
    tabla.insertar(1, "Producto A")
    tabla.insertar(2, "Producto B")
    tabla.insertar(3, "Producto C")

    assert len(tabla) == 3
    assert tabla.buscar(1) == "Producto A"
    assert tabla.buscar(2) == "Producto B"
    assert tabla.buscar(3) == "Producto C"
    assert tabla.buscar(99) is None


def test_actualizar_valor():
    tabla = TablaHash()
    tabla.insertar(1, "Original")
    assert tabla.buscar(1) == "Original"

    tabla.insertar(1, "Actualizado")
    assert len(tabla) == 1
    assert tabla.buscar(1) == "Actualizado"


def test_eliminar():
    tabla = TablaHash(capacidad_inicial=5)
    tabla.insertar(1, "A")
    tabla.insertar(2, "B")
    tabla.insertar(3, "C")

    assert tabla.eliminar(2) is True
    assert len(tabla) == 2
    assert tabla.buscar(2) is None

    assert tabla.eliminar(99) is False
    assert len(tabla) == 2


def test_existe():
    tabla = TablaHash()
    tabla.insertar("clave", "valor")

    assert tabla.existe("clave") is True
    assert tabla.existe("no_existe") is False


def test_obtener_todos():
    tabla = TablaHash(capacidad_inicial=5)
    tabla.insertar(1, "A")
    tabla.insertar(2, "B")
    tabla.insertar(3, "C")

    elementos = tabla.obtener_todos()
    assert len(elementos) == 3
    assert (1, "A") in elementos
    assert (2, "B") in elementos
    assert (3, "C") in elementos


def test_obtener_claves():
    tabla = TablaHash()
    tabla.insertar(1, "A")
    tabla.insertar(2, "B")

    claves = tabla.obtener_claves()
    assert len(claves) == 2
    assert 1 in claves
    assert 2 in claves


def test_limpiar():
    tabla = TablaHash()
    tabla.insertar(1, "A")
    tabla.insertar(2, "B")

    assert len(tabla) == 2
    tabla.limpiar()
    assert len(tabla) == 0
    assert tabla.obtener_todos() == []


def test_colisiones_encadenamiento():
    tabla = TablaHash(capacidad_inicial=2)

    tabla.insertar(1, "A")

    clave_colision = 3
    while hash(clave_colision) % 2 != hash(1) % 2:
        clave_colision += 2
    tabla.insertar(clave_colision, "B")

    assert len(tabla) == 2
    assert tabla.buscar(clave_colision) == "B"


def test_redimensionamiento_automatico():
    tabla = TablaHash(capacidad_inicial=4)

    for i in range(20):
        tabla.insertar(i, f"Valor {i}")

    assert len(tabla) == 20
    assert tabla.capacidad > 4

    for i in range(20):
        assert tabla.buscar(i) == f"Valor {i}"

    for i in range(20):
        assert tabla.existe(i) is True


def test_claves_string():
    tabla = TablaHash(capacidad_inicial=5)
    tabla.insertar("nombre", "Producto X")
    tabla.insertar("categoria", "Electrónicos")
    tabla.insertar("precio", 150.0)

    assert tabla.buscar("nombre") == "Producto X"
    assert tabla.buscar("categoria") == "Electrónicos"
    assert tabla.buscar("precio") == 150.0
    assert tabla.buscar("inexistente") is None


def test_insercion_masiva_verifica_total():
    tabla = TablaHash(capacidad_inicial=5)

    for i in range(100):
        tabla.insertar(i, f"Valor-{i}")

    assert len(tabla) == 100

    todos = tabla.obtener_todos()
    assert len(todos) == 100

    for clave, valor in todos:
        assert valor == f"Valor-{clave}"


def test_eliminar_ulti_element_libre_bucket():
    tabla = TablaHash(capacidad_inicial=3)

    claves = [1, 4, 7]
    for k in claves:
        tabla.insertar(k, f"V{k}")

    for k in claves:
        assert tabla.eliminar(k) is True

    assert len(tabla) == 0


def test_reinsercion_despues_de_eliminar():
    tabla = TablaHash(capacidad_inicial=5)
    tabla.insertar(1, "A")
    tabla.eliminar(1)
    assert len(tabla) == 0

    tabla.insertar(1, "B")
    assert len(tabla) == 1
    assert tabla.buscar(1) == "B"