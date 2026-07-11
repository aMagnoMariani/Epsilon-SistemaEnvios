"""
Módulo Árbol de Inventario — Unidad V
Árbol B (configurado como Árbol 2-3 con M=3) para búsqueda eficiente de productos.
"""

from models.product import Producto
from arbol_b import ArbolB


class ArbolInventario(ArbolB):
    """Árbol B de Orden M=3 (equivalente a Árbol 2-3) para gestionar el inventario de productos.
    
    Las operaciones de búsqueda e inserción se basan en el ID del producto.
    Hereda toda la lógica balanceada del Árbol B.
    """

    def __init__(self):
        super().__init__(M=3)  # Usar orden M=3 para que funcione como Árbol 2-3
