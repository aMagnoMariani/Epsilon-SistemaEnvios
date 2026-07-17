"""
Core del sistema: inicialización de estructuras y carga/guardado de datos.
Centraliza el estado (modelo) que luego usan los controladores (controllers).

ESTRUCTURAS DE DATOS IMPLEMENTADAS:
- Árbol BST: Para búsqueda eficiente por ID de producto (O(log n))
- Tabla Hash: Para búsqueda rápida por nombre de producto (O(1) promedio)
- Cola de Prioridad: Para gestión de órdenes por urgencia
- Pila: Para historial de despachos (deshacer operaciones)
- Grafo: Para cálculo de rutas óptimas (Dijkstra)
"""
import os
import time
from persistencia import cargar_datos, guardar_datos
from arbol_inventario import ArbolInventario
from cola_despacho import ColaDespacho
from mapa_logistico import MapaLogistico
from tabla_hash import TablaHash
from models.product import Producto
from models.order import Orden

# Directorio de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, 'datos')
PRODUCTOS_FILE = os.path.join(DATOS_DIR, 'productos.json')
ORDENES_FILE = os.path.join(DATOS_DIR, 'ordenes.json')
MAPA_FILE = os.path.join(DATOS_DIR, 'mapa.json')

# Estado global (modelo)
arbol = ArbolInventario()  # Búsqueda por ID: O(log n)
tabla_hash_productos = TablaHash(capacidad_inicial=20)  # Búsqueda por nombre: O(1) promedio
cola = ColaDespacho()
mapa = MapaLogistico()


def inicializar_sistema():
    """Carga datos desde JSON e inicializa las estructuras globales.
    Diseñado para ser llamado una vez al arranque.
    
    Estructuras inicializadas:
    - Árbol BST: Indexa productos por ID para búsqueda eficiente
    - Tabla Hash: Indexa productos por nombre para búsqueda O(1)
    - Cola de Prioridad: Gestiona órdenes por urgencia
    - Grafo: Carga el mapa logístico para cálculo de rutas
    """
    global arbol, cola, mapa, tabla_hash_productos

    # Cargar productos en el Árbol BST y Tabla Hash
    datos_productos = cargar_datos(PRODUCTOS_FILE)
    for datos in datos_productos:
        producto = Producto.from_dict(datos)
        arbol.insertar(producto)
        # Indexar por nombre en la tabla hash para búsquedas rápidas
        tabla_hash_productos.insertar(producto.nombre.lower(), producto)

    # Cargar órdenes en la Cola de Prioridad
    datos_ordenes = cargar_datos(ORDENES_FILE)
    for datos in datos_ordenes:
        orden = Orden.from_dict(datos)
        cola.agregar_orden(orden)

    # Cargar mapa logístico
    mapa.cargar_mapa(MAPA_FILE)

    print('=' * 50)
    print('Sistema de Logística de Última Milla (core)')
    print(f'   Productos cargados: {arbol.tamano}')
    print(f'   Órdenes pendientes: {cola.pendientes}')
    print(f'   Nodos del mapa:     {len(mapa.obtener_nodos())}')
    print(f'   Índice hash:        {len(tabla_hash_productos)} entradas')
    print('=' * 50)


def buscar_producto_por_nombre(nombre: str):
    """Busca un producto por nombre usando la tabla hash.
    
    Esta función demuestra el uso práctico de la tabla hash para búsquedas
    por nombre, complementando al árbol BST que busca por ID.
    
    Args:
        nombre: Nombre del producto a buscar (case-insensitive).
    
    Returns:
        Objeto Producto si se encuentra, None en caso contrario.
    
    Complejidad: O(1) promedio, O(n) peor caso (colisiones).
    """
    return tabla_hash_productos.buscar(nombre.lower())


def guardar_estado():
    """Guarda el estado actual (productos y órdenes pendientes) a JSON."""
    productos = arbol.obtener_todos()
    datos_productos = [p.to_dict() for p in productos]
    guardar_datos(datos_productos, PRODUCTOS_FILE)

    datos_ordenes = cola.obtener_ordenes_pendientes_como_dicts()
    guardar_datos(datos_ordenes, ORDENES_FILE)
