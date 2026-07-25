# Justificación de Estructuras de Datos No Implementadas

Este documento explica por qué ciertas estructuras vistas en clase no fueron implementadas en este proyecto
y qué alternativas se usaron en su lugar.

## Estructuras implementadas

| Estructura | Implementación | Ubicación |
|---|---|---|
| Árbol B (2-3) | Propia — `NodoB` + `ArbolB`, M=3 | `arbol_b.py` |
| Tabla Hash | Propia — chaining, redimensionamiento automático | `tabla_hash.py` |
| Cola de Prioridad | `heapq` nativo + wrapper propio | `cola_despacho.py` |
| Pila (LIFO) | `ListaDobleEnlazada` propia usada como pila | `lista_enlazada.py` → `cola_despacho.py` |
| Lista Doblemente Enlazada | Propia, genérica (`TypeVar`) | `lista_enlazada.py` |
| Grafo + Dijkstra | Propia + grafo vial de NetworkX (OSM real) | `mapa_logistico.py` |
| BFS / DFS | Propia sobre lista de adyacencia | `mapa_logistico.py` |

---

## Estructuras NO implementadas y su justificación

### 1. Árbol AVL o Árbol Rojo-Negro

**Justificación:** Se implementó un **Árbol B (2-3)** cuyo balanceo es automático y más eficiente
para operaciones de inserción/búsqueda en sistemas de inventario. Un Árbol B puede almacenar
múltiples llaves por nodo, reduciendo la altura del árbol y el número de accesos.
Un Árbol AVL o Rojo-Negro habría sido redundante ya que el Árbol B (2-3) cubre
los mismos casos de uso con igual complejidad O(log n).

### 2. Matriz de Adyacencia

**Justificación:** El grafo vial de Maturín tiene ~6,500 nodos. Una matriz de adyacencia
consumiría O(V²) = ~42 millones de celdas, la mayoría vacías (grafo disperso).
Se usa **lista de adyacencia** (NetworkX MultiDiGraph) que ocupa O(V + E) ≈ ~23,500
entradas, y permite acceso O(1) a los vecinos de cada nodo. Esto es más eficiente
en memoria y tiempo para grafos viales urbanos.

### 3. Tabla Hash con Direccionamiento Abierto (Open Addressing)

**Justificación:** Se implementó encadenamiento (chaining) porque es más simple de mantener
y depurar, no sufre de clustering primario/secundario, y permite manejar colisiones
sin buscar slots vacíos. Para la carga de trabajo de este proyecto (~11 productos),
no hay diferencia práctica de rendimiento. El chaining también maneja mejor
las eliminaciones sin necesidad de marcas especiales (tombstones).

### 4. Ordenamiento externo (External Sorting)

**Justificación:** Los datos se almacenan en archivos JSON locales con <20 registros.
No se requiere ordenamiento externo. Para conjuntos más grandes se usaría `sorted()`
nativo de Python (Timsort, O(n log n)) que es más que suficiente para la escala
de este proyecto.

### 5. Árbol B+ (B-plus Tree)

**Justificación:** Un Árbol B+ almacena todas las claves en las hojas y duplica las internas.
Es ideal para sistemas de base de datos que requieren barridos secuenciales.
En este proyecto, la operación más común es búsqueda puntual por ID, y el Árbol B
estándar ya cumple con O(log n). Implementar las hojas enlazadas de B+
añadiría complejidad sin beneficio para los patrones de acceso actuales.

### 6. Hashing Perfecto

**Justificación:** Requiere conocer todas las claves de antemano para construir una función
hash sin colisiones. Las claves de productos cambian dinámicamente (inserción/eliminación),
por lo que no es práctico. El chaining con redimensionamiento es más flexible.

### 7. Skip List

**Justificación:** Ofrece O(log n) promedio pero requiere aleatoriedad y más memoria.
El Árbol B ya proporciona O(log n) determinístico sin necesidad de aleatoriedad.
No aporta ventajas adicionales.

### 8. Colas Dobles (Deque) y Colas Circulares

**Justificación:** La `ListaDobleEnlazada` ya soporta operaciones en ambos extremos
en O(1) (`insertar_inicio`, `insertar_final`, `eliminar_inicio`, `eliminar_ultimo`),
cubriendo toda la funcionalidad de un Deque. Una cola circular en arreglo habría
requerido pre-dimensionamiento y lógica de wraparound sin aportar ventajas para
un historial de despachos que crece dinámicamente.

### 9. Árbol Trie / Árbol de Sufijos

**Justificación:** Trie es especializado para búsqueda de prefijos en strings.
En este proyecto los strings (nombres de productos) se buscan por igualdad exacta
usando la Tabla Hash en O(1), no por prefijo. Un Trie añadiría complejidad de
implementación y memoria sin un caso de uso que.

### 10. Fibonacci Heap para Dijkstra

**Justificación:** El algoritmo de Dijkstra usa `heapq` (binary hear) con complejidad
O((V + E) log V). Un Fibonacci Heap teóricamente alcanza O(V log V + E) pero su
complejidad constante es alta y rara vez es más rápido en la práctica para grafas
con miles de nodos. NetworkX usa binary heap optimizado en C que es más que adecuado.