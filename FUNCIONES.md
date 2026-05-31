# Funciones y estructuras de datos en Epsilon_UDO

Este documento explica las estructuras de datos y las funciones principales usadas en el proyecto, y para qué se utilizan (pilas, colas, listas, árboles, grafos, hashing, etc.). Está pensado para desarrolladores que van a mantener o extender el sistema.

---

## Resumen por módulo

- `app.py` — Orquestador y rutas Flask. Coordina carga/guardado, vistas y acciones del usuario.
- `models.py` — Modelos de dominio: `Producto` y `Orden`.
- `persistencia.py` — Lectura y escritura en JSON (`cargar_datos`, `guardar_datos`).
- `arbol_inventario.py` — Árbol Binario de Búsqueda (BST) para almacenar productos por `id`.
- `cola_despacho.py` — Cola de prioridad (heap) para órdenes y pila de historial para deshacer despachos.
- `mapa_logistico.py` — Grafo ponderado y algoritmo de Dijkstra para cálculo de rutas.

---

## Estructuras y su propósito

### Árboles (BST) — `arbol_inventario.py`
- Estructura: Árbol Binario de Búsqueda (NodoBST + ArbolInventario).
- Propósito: Permitir búsquedas, inserciones y actualizaciones de `Producto` por `id` en tiempo promedio O(log n) si el árbol está balanceado (aquí es un BST simple).
- Funciones clave:
  - `insertar(producto)` — Inserta o reemplaza un `Producto` según su `id`.
  - `buscar(id)` — Busca y retorna el `Producto` con ese `id` o `None`.
  - `actualizar_stock(id, cantidad)` — Resta cantidad del stock (verifica disponibilidad).
  - `restaurar_stock(id, cantidad)` — Restaura stock (para "deshacer" despachos).
  - `obtener_todos()` — Recorrido inorden que devuelve los productos ordenados por `id`.
- Notas: Para grandes volúmenes y búsquedas altamente balanceadas considerar reemplazar por un árbol balanceado (AVL/Red-Black) o usar bases de datos.


### Colas y Pilas — `cola_despacho.py`
- Estructura principal: Cola de prioridad implementada con `heapq`.
  - Tupla almacenada: `(prioridad, contador, orden)` — `contador` evita reordenamiento no determinista entre elementos con la misma prioridad.
- Pila de historial (`pila_historial`): lista usada como LIFO para almacenar órdenes despachadas y permitir `deshacer`.
- Propósito:
  - Asegurar que órdenes `Express` (prioridad 0) sean procesadas antes que `Normal` (1).
  - Permitir revertir el último despacho restaurando la orden a la cola y el stock.
- Funciones clave:
  - `agregar_orden(orden)` — Encola una orden con su prioridad.
  - `despachar_siguiente()` — Extrae la orden más urgente y la guarda en la pila de historial.
  - `deshacer_ultimo_despacho()` — Saca la última orden despachada de la pila y la reinyecta en la cola.
  - `ver_cola()` — Devuelve listado de órdenes pendientes ordenadas por prioridad.


### Listas y Diccionarios (listas, arrays y hashing implícito)
- Uso general: Python `list` y `dict` en todo el proyecto.
  - `list` para colecciones ordenadas, resultados de recorridos, historial, etc.
  - `dict` (hash table interno de Python) para estructuras de adyacencia del grafo y para mapas rápidos `id -> objeto` cuando es necesario.
- Propósito: almacenamiento dinámico, retorno de datos a plantillas y serialización JSON.


### Grafos y Dijkstra — `mapa_logistico.py`
- Estructura: Grafo ponderado representado como un diccionario de adyacencia:
  - `grafo = { nodo: { vecino: {'gasolina': costo, 'tiempo': costo}, ... }, ... }`
- Algoritmo de ruta:
  - Implementa Dijkstra con `heapq` para calcular la ruta de menor costo según la `estrategia` ('gasolina' o 'tiempo').
  - Caso especial `tiempo` permite estimación directa usando Haversine si se solicita la ruta más rápida sin pasar por nodos intermedios.
- Funciones clave:
  - `cargar_mapa(archivo)` — Construye `grafo`, `coordenadas` y `descripciones` desde JSON.
  - `calcular_ruta(origen, destino, estrategia)` — Retorna `(costo_total, camino, detalles)`.
  - `obtener_nodos()`, `obtener_aristas()`, `obtener_destinos()` — Utilidades para UI.


### Persistencia — `persistencia.py`
- Uso: Leer y escribir listas de diccionarios a archivos JSON.
- Funciones:
  - `cargar_datos(archivo)` — Devuelve lista (o lista vacía si no existe o hay error). Maneja errores JSON.
  - `guardar_datos(datos, archivo)` — Guarda con `ensure_ascii=False` e indentación; crea directorio si hace falta.
- Propósito: mantenimiento sencillo del estado del sistema sin base de datos. Adecuado para prototipos y demos.


### Modelos — `models.py`
- Clases `Producto` y `Orden` con `__slots__` para reducir la memoria por instancia.
- Métodos comunes: `to_dict()` y `from_dict()` para serialización/deserialización.
- Importancia: centralizar la estructura de datos de dominio y facilitar la persistencia.


## Patrones y consideraciones adicionales

- Serialización/compatibilidad: `to_dict()` / `from_dict()` estandarizan el intercambio con JSON.
- Manejo de errores: `persistencia.py` captura errores de JSON; `app.py` usa `flash()` para feedback en la UI.
- Escalabilidad: El diseño actual es educativo y funcional para prototipos. Para producción considerar:
  - Reemplazar JSON por una base de datos (SQLite, PostgreSQL).
  - Sustituir el BST simple por una estructura balanceada o índice en BD.
  - Añadir autenticación/roles si la interfaz es multiusuario.


## Ejemplos de uso rápido (APIs internas)

- Insertar producto en el árbol:

```python
from arbol_inventario import ArbolInventario
from models import Producto

arbol = ArbolInventario()
producto = Producto(id=1001, nombre='Caja Agua', precio=12.5, stock=50)
arbol.insertar(producto)
```

- Agregar una orden express:

```python
from cola_despacho import ColaDespacho
from models import Orden

cola = ColaDespacho()
orden = Orden(id=2001, producto_id=1001, cantidad=2, destino='Sector_A', prioridad=0)
cola.agregar_orden(orden)
```

- Calcular ruta entre nodos:

```python
from mapa_logistico import MapaLogistico
mapa = MapaLogistico('datos/mapa.json')
costo, camino, detalles = mapa.calcular_ruta('Almacen_Central', 'Sector_B', 'gasolina')
```

---

Si quieres, puedo:
- Añadir diagramas (Mermaid) que muestren la relación entre módulos.
- Extender `FUNCIONES.md` con ejemplos más detallados por función y fragmentos de prueba (`pytest`).
- Crear `requirements-dev.txt` y configurar `pre-commit`.

Indica qué prefieres que haga a continuación.
