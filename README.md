# Epsilon_UDO — SistemaEnvios

Aplicación educativa y funcional para gestionar inventario y despachos en Maturín, Estado Monagas, Venezuela. Implementa estructuras de datos y algoritmos fundamentales (Árbol B / 2-3, Cola de Prioridad, Pila, Lista Doblemente Enlazada, Tabla Hash, Grafo + Dijkstra con datos viales reales de OpenStreetMap) con mapa 100% offline y rutas sobre calles reales.

## Integrantes

- Alejandro Mariani
- José Félix Cedeño
- Diana Yeguez
- Victoria Santodomingo
- Ariadna Bucarito

## Instalación rápida

```bash
pip install -r requirements.txt --break-system-packages
python tools/generar_grafo_vial.py    # descargar calles reales
python tools/download_tiles.py        # descargar tiles offline
python app.py                         # iniciar en http://localhost:5000
```

## Documentación

| Documento | Descripción |
|---|---|
| [MANUAL_USUARIO.md](MANUAL_USUARIO.md) | Manual de usuario con instrucciones paso a paso |
| [docs/JUSTIFICACION.md](docs/JUSTIFICACION.md) | Justificación de estructuras no implementadas |
| [docs/INFORME_FINAL.md](docs/INFORME_FINAL.md) | Informe final del proyecto |
| [IMPLEMENTACION_GRAFOS_HASH.md](IMPLEMENTACION_GRAFOS_HASH.md) | Detalle técnico de grafo y tabla hash |
| [FUNCIONES.md](FUNCIONES.md) | Funciones y estructuras por módulo |
| [docs/PLAN.md](docs/PLAN.md) | Plan original de asignación |

## Estructuras de datos

| Estructura | Archivo | Operaciones | Complejidad |
|---|---|---|---|
| Árbol B (2-3) | `arbol_b.py` | Buscar, Insertar | O(log n) |
| Tabla Hash (chaining) | `tabla_hash.py` | Insertar, Buscar, Eliminar | O(1) promedio |
| Cola de Prioridad | `cola_despacho.py` | Enqueue, Dequeue | O(log n) |
| Pila (LIFO) | `lista_enlazada.py` | Push, Pop | O(1) |
| Lista Doblemente Enlazada | `lista_enlazada.py` | Insertar/Eliminar extremos | O(1) |
| Grafo + Dijkstra | `mapa_logistico.py` | Ruta más corta, BFS, DFS | O((V+E) log V) |

## Pruebas

```bash
pytest  # 49 tests unitarios
```

## Licencia

Proyecto académico — Universidad de Oriente, Núcleo Monagas, 2026.
