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

### Árboles B / 2-3 — `arbol_inventario.py` e `arbol_b.py`
- Estructura: Árbol B de Orden M (NodoB + ArbolB, configurado con M=3 para actuar como Árbol 2-3).
- Propósito: Permitir búsquedas, inserciones y actualizaciones de `Producto` por `id` en tiempo garantizado de $O(\log n)$ en el peor caso gracias a su propiedad auto-balanceada.
- Funciones clave:
  - `insertar(producto)` — Inserta un `Producto` según su `id` o lo actualiza si ya existe. Divide nodos hacia arriba de manera recursiva si se supera el límite de llaves (M-1).
  - `buscar(id)` — Busca y retorna el `Producto` con ese `id` o `None`.
  - `actualizar_stock(id, cantidad)` — Resta cantidad del stock (verifica disponibilidad).
  - `restaurar_stock(id, cantidad)` — Restaura stock (para "deshacer" despachos).
  - `obtener_todos()` — Recorrido inorden que devuelve los productos ordenados ascendentemente por `id`.
- Notas de diseño (Limitaciones):
  - Inserción y búsqueda balanceada implementada.
  - No implementa la operación de eliminación de nodos ni fusión/redistribución automática de nodos asociados a underflow en la eliminación.



### Colas y Pilas — `cola_despacho.py`
- Estructura principal: Cola de prioridad implementada con `heapq`.
  - Tupla almacenada: `(prioridad, contador, orden)` — `contador` evita reordenamiento no determinista entre elementos con la misma prioridad.
- Pila de historial (`pila_historial`): Lista doblemente enlazada (`ListaDobleEnlazada`) usada como LIFO para almacenar órdenes despachadas y permitir `deshacer` de forma óptima.
- Propósito:
  - Asegurar que órdenes `Express` (prioridad 0) sean procesadas antes que `Normal` (1).
  - Permitir revertir el último despacho restaurando la orden a la cola y el stock.
- Funciones clave:
  - `agregar_orden(orden)` — Encola una orden con su prioridad.
  - `despachar_siguiente()` — Extrae la orden más urgente de la cola de prioridad y la inserta al final de la lista doblemente enlazada (operación de empuje en la pila).
  - `deshacer_ultimo_despacho()` — Remueve el último elemento de la lista doblemente enlazada (operación LIFO pop) y lo vuelve a encolar en la cola de prioridad.
  - `ver_cola()` — Devuelve listado de órdenes pendientes ordenadas por prioridad.


### Listas Enlazadas (Personalizadas) — `lista_enlazada.py`
- Estructura: Lista Doblemente Enlazada (`ListaDobleEnlazada` que gestiona nodos `NodoDoble`).
- Propósito: Proveer una estructura lineal dinámica personalizada para el historial de despachos del operador, garantizando inserción y eliminación eficientes en los extremos en $O(1)$.
- Operaciones soportadas y limitaciones (lo que NO hace):
  - `insertar_inicio(dato)` / `insertar_final(dato)`: Inserta un elemento en la cabeza o cola en $O(1)$. *No realiza ordenamiento del dato ni valida si está duplicado.*
  - `eliminar_inicio()` / `eliminar_ultimo()`: Remueve y retorna el elemento en la cabeza o cola en $O(1)$. *No lanza excepciones si la lista está vacía (retorna None).*
  - `eliminar(dato)`: Busca secuencialmente y elimina la primera aparición del dato en $O(N)$. *No elimina todas las apariciones ni funciona en $O(1)$.*
  - `buscar(criterio)`: Busca el primer elemento que cumpla la función de criterio en $O(N)$. *No soporta búsqueda binaria ya que carece de acceso por índice en $O(1)$ (acceso aleatorio).*
  - `recorrer_adelante()` / `recorrer_atras()`: Generadores para iteración directa o inversa. *No permiten la modificación segura de la estructura durante la iteración.*


### Listas y Diccionarios (Estructuras nativas de Python)
- Uso general: Python `list` y `dict` en el resto del proyecto.
  - `list` para colecciones secuenciales nativas, retorno a plantillas y manipulación temporal.
  - `dict` (hash table interna) para representar las adyacencias del grafo de transporte y el mapeo de coordenadas.
- Propósito: Almacenamiento dinámico nativo y facilidad de serialización a JSON.


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
