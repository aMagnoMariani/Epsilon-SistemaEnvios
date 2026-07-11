"""
Pruebas unitarias para ArbolB y ArbolInventario (Árbol B / 2-3).
Verifican inserción, búsqueda, actualización, restauración de stock y recorrido inorden.
"""

import pytest
import random
from models.product import Producto
from arbol_b import ArbolB, NodoB
from arbol_inventario import ArbolInventario


def test_creacion_vacia():
    arbol = ArbolB(M=3)
    assert len(arbol) == 0
    assert arbol.tamano == 0
    assert arbol.buscar(100) is None


def test_orden_invalido():
    with pytest.raises(ValueError):
        ArbolB(M=2)


def test_insertar_y_buscar():
    arbol = ArbolB(M=3)
    p1 = Producto(id=10, nombre="Producto A", precio=1.5, stock=100)
    p2 = Producto(id=20, nombre="Producto B", precio=2.5, stock=200)
    p3 = Producto(id=5, nombre="Producto C", precio=3.5, stock=300)

    arbol.insertar(p1)
    arbol.insertar(p2)
    arbol.insertar(p3)

    assert len(arbol) == 3
    assert arbol.buscar(10) is p1
    assert arbol.buscar(20) is p2
    assert arbol.buscar(5) is p3
    assert arbol.buscar(15) is None


def test_actualizacion_duplicados():
    arbol = ArbolB(M=3)
    p1 = Producto(id=10, nombre="Producto A", precio=1.5, stock=100)
    p1_nuevo = Producto(id=10, nombre="Producto A Modificado", precio=1.8, stock=150)

    arbol.insertar(p1)
    assert len(arbol) == 1
    assert arbol.buscar(10).nombre == "Producto A"

    # Insertar el mismo ID con datos actualizados
    arbol.insertar(p1_nuevo)
    assert len(arbol) == 1  # No debe aumentar el tamaño
    assert arbol.buscar(10).nombre == "Producto A Modificado"
    assert arbol.buscar(10).precio == 1.8
    assert arbol.buscar(10).stock == 150


def test_recorrido_inorden_2_3():
    arbol = ArbolB(M=3)  # Equivalente a Árbol 2-3
    ids = list(range(1, 100))
    random.seed(42)
    random.shuffle(ids)

    productos = [Producto(id=x, nombre=f"P_{x}", precio=float(x), stock=x) for x in ids]
    for p in productos:
        arbol.insertar(p)

    assert len(arbol) == 99
    todos = arbol.obtener_todos()
    assert len(todos) == 99
    
    # Verificar que el recorrido inorden devuelva la lista ordenada ascendentemente por ID
    for i in range(len(todos) - 1):
        assert todos[i].id < todos[i + 1].id
        assert todos[i].id == i + 1


def test_recorrido_inorden_general_b():
    arbol = ArbolB(M=5)  # Árbol B de Orden M=5
    ids = list(range(1, 200))
    random.seed(123)
    random.shuffle(ids)

    productos = [Producto(id=x, nombre=f"P_{x}", precio=float(x), stock=x) for x in ids]
    for p in productos:
        arbol.insertar(p)

    assert len(arbol) == 199
    todos = arbol.obtener_todos()
    assert len(todos) == 199
    
    # Verificar ordenamiento
    for i in range(len(todos) - 1):
        assert todos[i].id < todos[i + 1].id
        assert todos[i].id == i + 1


def test_actualizar_y_restaurar_stock():
    arbol = ArbolB(M=3)
    p = Producto(id=1, nombre="Item", precio=10.0, stock=5)
    arbol.insertar(p)

    # Actualizar stock (restar stock)
    assert arbol.actualizar_stock(1, 3) is True
    assert arbol.buscar(1).stock == 2

    # Intentar actualizar stock con más de lo disponible
    assert arbol.actualizar_stock(1, 5) is False
    assert arbol.buscar(1).stock == 2  # Debe mantenerse igual

    # Restaurar stock (sumar stock)
    assert arbol.restaurar_stock(1, 10) is True
    assert arbol.buscar(1).stock == 12

    # Intentar con ID inexistente
    assert arbol.actualizar_stock(99, 1) is False
    assert arbol.restaurar_stock(99, 1) is False


def test_arbol_inventario_herencia():
    # Probar que la clase ArbolInventario expone toda la funcionalidad requerida
    inventario = ArbolInventario()
    assert isinstance(inventario, ArbolB)
    assert inventario.M == 3

    p1 = Producto(id=50, nombre="Prod 50", precio=5.0, stock=10)
    p2 = Producto(id=30, nombre="Prod 30", precio=3.0, stock=20)
    p3 = Producto(id=70, nombre="Prod 70", precio=7.0, stock=30)

    inventario.insertar(p1)
    inventario.insertar(p2)
    inventario.insertar(p3)

    assert len(inventario) == 3
    assert inventario.buscar(30) is p2

    todos = inventario.obtener_todos()
    assert [p.id for p in todos] == [30, 50, 70]
