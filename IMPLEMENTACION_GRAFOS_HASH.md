# Implementación de Grafos y Tablas Hash

## Resumen de Cambios

Este documento describe la implementación y mejora de estructuras de datos de grafos y tablas hash en el Sistema EnviosEpsilon_UDO.

---

## 1. Implementación de Tabla Hash

### Archivo: `tabla_hash.py`

Implementación completa de tabla hash con las siguientes características:

#### Representación Elegida
- **Estructura**: Lista de listas (buckets) donde cada bucket contiene pares clave-valor.
- **Resolución de colisiones**: Encadenamiento (chaining) con listas. Cuando dos claves producen el mismo índice, se almacenan juntas en el mismo bucket.
- **Redimensionamiento automático**: Cuando el factor de carga supera 75%, la tabla se duplica para mantener O(1) promedio.

#### Función Hash
- Utiliza la función `hash()` nativa de Python combinada con módulo: `abs(hash(clave)) % capacidad`.
- Para claves numéricas (IDs de productos), el hash es directo y eficiente.
- Para claves string (nombres), Python genera valores distribuidos uniformemente.
- `abs()` evita índices negativos; el módulo asegura el índice dentro de los límites de la tabla.

#### Limitaciones y Resolución de Colisiones
- **Colisiones**: Ocurren cuando dos claves diferentes producen el mismo índice después del módulo.
- **Resolución**: Encadenamiento con listas — cada bucket es una lista que puede contener múltiples pares clave-valor.
- **Factor de carga**: Umbral del 75% para redimensionamiento. Se verifica antes de cada inserción.
- **Complejidad**:
  - Mejor caso: O(1) — acceso directo sin colisiones.
  - Peor caso: O(n) — todas las claves colisionan en el mismo bucket.
  - Caso promedio: O(1) con buen factor de carga y función hash distribuida.

#### Métodos Implementados
| Método | Descripción | Complejidad |
|--------|-------------|-------------|
| `insertar(clave, valor)` | Inserta o actualiza un par clave-valor | O(1) promedio |
| `buscar(clave)` | Busca un valor por su clave | O(1) promedio |
| `eliminar(clave)` | Elimina un par clave-valor | O(1) promedio |
| `existe(clave)` | Verifica si una clave existe | O(1) promedio |
| `obtener_todos()` | Retorna todos los pares clave-valor | O(n) |
| `obtener_claves()` | Retorna todas las claves | O(n) |
| `limpiar()` | Elimina todos los elementos | O(capacidad) |
| `_redimensionar()` | Duplica la tabla y rehashea | O(n) |

---

## 2. Código de Grafo con Recorrido

### Archivo Modificado: `mapa_logistico.py`

#### Representación Elegida
- **Lista de Adyacencia**: Implementada como diccionario de diccionarios.
- **Estructura**: `{nodo_origen: {nodo_destino: {'gasolina': costo, 'tiempo': costo}, ...}, ...}`
- **Ventajas**: Eficiente para grafos dispersos (como un mapa de ciudad con pocas conexiones). Acceso O(1) a vecinos y costos de aristas.
- **Complementos**: `self.coordenadas` (lat/lng para Haversine) y `self.descripciones` (nombres de rutas).

#### Algoritmos de Recorrido

##### Dijkstra (Rutas Óptimas)
- Propósito: Encontrar la ruta de menor costo entre dos nodos (gasolina o tiempo).
- Implementación: Cola de prioridad `heapq` con min-heap. Procesa siempre el nodo con menor costo acumulado.
- Complejidad: O((V + E) log V).
- Garantía: Ruta óptima en grafos con pesos no negativos.
- Caso especial 'tiempo': Estima ruta directa usando fórmula de Haversine (sin Dijkstra).

##### BFS — Breadth-First Search (NUEVO)
- Propósito: Recorrido por niveles (nivel por nivel) para explorar todos los nodos alcanzables desde un origen.
- Implementación: Cola FIFO iterativa con conjunto de visitados.
- Complejidad: O(V + E).
- Uso: Encontrar camino más corto en número de aristas, explorar sectores alcanzables.

##### DFS — Depth-First Search (NUEVO)
- Propósito: Recorrido en profundidad (explora todo un camino antes de retroceder).
- Implementación: Pila LIFO iterativa para evitar recursión profunda y stack overflow.
- Complejidad: O(V + E).
- Uso: Detección de conectividad, ordenamiento topológico, exploración exhaustiva.

##### Conectividad (NUEVO)
- `es_conexo()`: Verifica si todos los nodos son alcanzables desde cualquier origen.
- Implementado con DFS desde un nodo arbitrario; si se visitan todos los vértices, el grafo es conexo.

#### Limitaciones
- No maneja pesos negativos (Dijkstra no es adecuado).
- Para grafos muy densos, una matriz de adyacencia podría ser más eficiente.
- Recalcula la ruta completa cada vez (sin caché de rutas).

#### Métodos del Grafo
| Método | Propósito | Complejidad |
|--------|-----------|-------------|
| `cargar_mapa(archivo)` | Construye el grafo desde JSON | O(V + E) |
| `calcular_ruta(origen, destino, estrategia)` | Dijkstra para ruta óptima | O((V+E) log V) |
| `recorrido_bfs(origen)` | Recorrido BFS por niveles | O(V + E) |
| `recorrido_dfs(origen)` | Recorrido DFS en profundidad | O(V + E) |
| `es_conexo()` | Verifica conectividad total | O(V + E) |
| `obtener_nodos()` | Lista de todos los vértices | O(V) |
| `obtener_aristas()` | Lista de aristas sin duplicados | O(E) |
| `obtener_destinos()` | Nodos excepto Almacén Central | O(V) |

---

## 3. Integración en el Sistema

### Archivo: `core.py`

La tabla hash está integrada en el sistema principal:

#### Indexación Dual
- Árbol BST (`arbol_inventario.py`): Indexa productos por **ID** — O(log n).
- Tabla Hash (`tabla_hash.py`): Indexa productos por **nombre** — O(1) promedio.

#### Uso Práctico
```python
# Búsqueda por ID (Árbol BST)
producto = arbol.buscar(105)  # O(log n)

# Búsqueda por nombre (Tabla Hash)
producto = buscar_producto_por_nombre("Samsung Galaxy")  # O(1) promedio
```

---

## 4. Estructuras de Datos del Sistema

| Estructura | Propósito | Complejidad | Archivo |
|------------|-----------|-------------|---------|
| **Árbol B (2-3)** | Búsqueda por ID de producto | O(log n) | `arbol_inventario.py` |
| **Tabla Hash** | Búsqueda por nombre de producto | O(1) promedio | `tabla_hash.py` |
| **Cola de Prioridad** | Gestión de órdenes por urgencia | O(log n) | `cola_despacho.py` |
| **Lista Doble Enlazada** | Pila de historial (deshacer) | O(1) push/pop | `lista_enlazada.py` |
| **Grafo Ponderado** | Cálculo de rutas + recorridos BFS/DFS | O((V+E) log V) Dijkstra | `mapa_logistico.py` |

---

## 5. Archivos Creados/Modificados

### Archivos Creados
- `test_tabla_hash.py` — 14 pruebas unitarias (inserción, búsqueda, colisiones, redimensionamiento, casos borde).
- `test_mapa_logistico.py` — 19 pruebas unitarias (carga, Dijkstra, BFS, DFS, conectividad, casos borde).

### Archivos Modificados
- `mapa_logistico.py` — Agregados métodos `recorrido_bfs()`, `recorrido_dfs()`, `es_conexo()` con documentación completa de representación y algoritmos.

### Archivos Existentes (ya completos)
- `tabla_hash.py` — Tabla hash con chaining, documentación y pruebas inline.
- `core.py` — Integración de tabla hash con el árbol BST.

---

## 6. Ejecución de Pruebas

```bash
# Todas las pruebas (47 tests)
python -m pytest -v

# Solo tabla hash (14 tests)
python -m pytest test_tabla_hash.py -v

# Solo grafo (19 tests)
python -m pytest test_mapa_logistico.py -v

# Prueba inline de tabla hash
python tabla_hash.py
```

### Resultados
```
test_tabla_hash.py .............. 14 passed
test_mapa_logistico.py ................... 19 passed
test_lista_enlazada.py ...... 6 passed
test_arbol_b.py ........ 8 passed
TOTAL: 47 passed in 0.07s
```

---

## 7. Comentarios sobre Representación, Función Hash y Limitaciones

### Tabla Hash (`tabla_hash.py`)
Los comentarios en el módulo explican:
- **Representación**: Lista de buckets con tuplas (clave, valor) en cada bucket para chaining.
- **Función hash**: `abs(hash(clave)) % capacidad`, documentada con casos para claves numéricas y string.
- **Colisiones**: Resueltas por encadenamiento con listas. El método `_redimensionar()` mantiene el factor de carga bajo 75%.
- **Limitaciones**: Peor caso O(n) si todas las claves colisionan; dependencia de la función hash de Python.

### Grafo (`mapa_logistico.py`)
Los comentarios en el módulo explican:
- **Representación**: Lista de adyacencia como `dict` de `dict`, eficiente para grafos dispersos.
- **Dijkstra**: Documentado paso a paso (inicialización, heap, relajación, reconstrucción del camino).
- **BFS**: Recorrido por niveles con cola FIFO, documentado con propósito y casos de uso.
- **DFS**: Recorrido en profundidad iterativo con pila LIFO, evitando recursión para grafos grandes.
- **Limitaciones**: No maneja pesos negativos; sin caché de rutas; matriz de adyacencia podría ser mejor para grafos muy densos.
