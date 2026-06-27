"""
Pruebas unitarias para ListaDobleEnlazada.
Verifican todas las operaciones requeridas: inserción, eliminación, búsqueda y recorrido.
"""

import pytest
from lista_enlazada import ListaDobleEnlazada


def test_insertar_inicio():
    lista = ListaDobleEnlazada[int]()
    assert len(lista) == 0
    assert lista.cabeza is None
    assert lista.cola is None

    lista.insertar_inicio(10)
    assert len(lista) == 1
    assert lista.cabeza.dato == 10
    assert lista.cola.dato == 10

    lista.insertar_inicio(20)
    assert len(lista) == 2
    assert lista.cabeza.dato == 20
    assert lista.cola.dato == 10
    assert lista.cabeza.siguiente.dato == 10
    assert lista.cola.anterior.dato == 20


def test_insertar_final():
    lista = ListaDobleEnlazada[int]()
    lista.insertar_final(10)
    assert len(lista) == 1
    assert lista.cabeza.dato == 10
    assert lista.cola.dato == 10

    lista.insertar_final(20)
    assert len(lista) == 2
    assert lista.cabeza.dato == 10
    assert lista.cola.dato == 20
    assert lista.cabeza.siguiente.dato == 20
    assert lista.cola.anterior.dato == 10


def test_eliminar_inicio_y_final():
    lista = ListaDobleEnlazada[int]()
    assert lista.eliminar_inicio() is None
    assert lista.eliminar_ultimo() is None

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    # Eliminar inicio
    val = lista.eliminar_inicio()
    assert val == 10
    assert len(lista) == 2
    assert lista.cabeza.dato == 20

    # Eliminar final
    val = lista.eliminar_ultimo()
    assert val == 30
    assert len(lista) == 1
    assert lista.cola.dato == 20

    # Eliminar el único restante
    val = lista.eliminar_inicio()
    assert val == 20
    assert len(lista) == 0
    assert lista.cabeza is None
    assert lista.cola is None


def test_eliminar_por_valor():
    lista = ListaDobleEnlazada[str]()
    lista.insertar_final("A")
    lista.insertar_final("B")
    lista.insertar_final("C")
    lista.insertar_final("B")  # Duplicado

    # Eliminar un elemento intermedio (primera aparición de B)
    assert lista.eliminar("B") is True
    assert len(lista) == 3
    assert lista.to_list() == ["A", "C", "B"]

    # Eliminar cabeza ("A")
    assert lista.eliminar("A") is True
    assert len(lista) == 2
    assert lista.cabeza.dato == "C"

    # Eliminar cola ("B")
    assert lista.eliminar("B") is True
    assert len(lista) == 1
    assert lista.cola.dato == "C"
    assert lista.cabeza.dato == "C"

    # Intentar eliminar inexistente
    assert lista.eliminar("X") is False
    assert len(lista) == 1


def test_buscar():
    lista = ListaDobleEnlazada[dict]()
    lista.insertar_final({"id": 1, "nombre": "Manzana"})
    lista.insertar_final({"id": 2, "nombre": "Pera"})
    lista.insertar_final({"id": 3, "nombre": "Banana"})

    # Buscar existente
    elem = lista.buscar(lambda x: x["id"] == 2)
    assert elem == {"id": 2, "nombre": "Pera"}

    # Buscar inexistente
    elem = lista.buscar(lambda x: x["id"] == 99)
    assert elem is None


def test_recorridos():
    lista = ListaDobleEnlazada[int]()
    for i in range(1, 4):
        lista.insertar_final(i)

    # Recorrido adelante
    valores_adelante = list(lista.recorrer_adelante())
    assert valores_adelante == [1, 2, 3]

    # Recorrido atrás
    valores_atras = list(lista.recorrer_atras())
    assert valores_atras == [3, 2, 1]

    # Iterador estándar
    valores_iter = [x for x in lista]
    assert valores_iter == [1, 2, 3]

    # Reversed
    valores_rev = list(reversed(lista))
    assert valores_rev == [3, 2, 1]
