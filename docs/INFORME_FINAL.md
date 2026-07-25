# Informe Final — Epsilon_UDO

Sistema de Logística de Última Milla  
Universidad de Oriente, Núcleo Monagas  
**Fecha:** Julio 2026

---

## Enlace al repositorio

[github.com/aMagnoMariani/Epsilon-SistemaEnvios](https://github.com/aMagnoMariani/Epsilon-SistemaEnvios)

---

## Integrantes del equipo

- Alejandro Mariani
- José Félix Cedeño
- Diana Yeguez
- Victoria Santodomingo
- Ariadna Bucarito

---

## Resumen ejecutivo

Epsilon_UDO es una aplicación web desarrollada en **Flask + Python** que implementa
un sistema completo de gestión de inventario y despacho de última milla para la ciudad
de **Maturín, Estado Monagas**. El sistema integra cinco estructuras de datos
fundamentales implementadas desde cero, utilizando datos reales del mapa vial
de Maturín descargados de OpenStreetMap.

---

## Estructura del proyecto

```
Epsilon_UDO/
├── app.py                        Lanzador Flask
├── core.py                       Estado global e inicialización
├── persistencia.py               Carga/guardado JSON
├── arbol_b.py                    Árbol B (2-3) auto-balanceado
├── arbol_inventario.py           Subclase de ÁrbolB para productos
├── tabla_hash.py                 Tabla Hash con chaining
├── lista_enlazada.py             Lista Doblemente Enlazada genérica
├── cola_despacho.py              Cola de Prioridad + Pila de historial
├── mapa_logistico.py             Grafo vial real + Dijkstra + Haversine
├── controllers/web.py            Rutas Flask (controlador MVC)
├── models/product.py             Modelo Producto
├── models/order.py               Modelo Orden
├── templates/                    7 vistas HTML (Jinja2)
├── static/                       CSS, Leaflet.js, tiles offline
├── datos/                        Persistencia JSON + grafo vial
├── tools/                        Generación de grafo vial y tiles
├── docs/                         Documentación técnica
├── test_*.py                     47 pruebas unitarias (pytest)
├── MANUAL_USUARIO.md             Manual de usuario
├── docs/JUSTIFICACION.md         Justificación de implementación
├── docs/INFORME_FINAL.md         Este documento
└── README.md
```

---

## Estructuras de datos implementadas

| Estructura | Implementación | Operación principal | Complejidad |
|---|---|---|---|
| **Árbol B (2-3)** | Propia, 307 líneas | Buscar, Insertar | O(log n) |
| **Tabla Hash** | Propia, 228 líneas | Buscar por nombre | O(1) promedio |
| **Cola de Prioridad** | `heapq` + wrapper | Despachar más urgente | O(log n) |
| **Pila (LIFO)** | `ListaDobleEnlazada` | Deshacer despacho | O(1) |
| **Lista Doble Enlazada** | Propia, 263 líneas | Insertar/Eliminar extremos | O(1) |
| **Grafo + Dijkstra** | `networkx` + grafo vial real de OSM | Ruta más corta | O((V+E) log V) |
| **BFS / DFS** | Propia sobre lista de adyacencia | Recorridos | O(V+E) |

### Grafo vial real de Maturín
- Descargado con `osmnx` desde OpenStreetMap
- **6,507 nodos** y **17,032 aristas** — todas las calles y avenidas de la ciudad
- Cada arista tiene geometría real (`LineString` con coordenadas GPS)
- Pesos calculados: costo de gasolina (km × 0.7) y tiempo (km / velocidad por tipo de vía)
- Interpolación de puntos cada ~15 metros para que las polilíneas sigan las curvas de las calles

### Lógica de rutas
- **⛽ Ahorro de gasolina:** Greedy Nearest Neighbor entre nuevos que están entre origen y destino → ruta por calles reales entre cada par
- **⚡ Ruta más rápida:** Shortest path sobre grafo vial

---

## Capturas de ejecución

### Dashboard

```
==================================================
Sistema de Logística de Última Milla (core)
   Productos carados: 11
   Órdenes pendientes: 5
   Nodos del mapa:     9
   Índice hash:       11 entradas
==================================================
 * Running on http://127.0.0.1:5000
```

### Pruebas unitarias (pytest)
```
============================= 21 passed in 17.84s ==============================
```

### Mapa logístico
- Visualización de Maturín con tiles de OSM — 100% offline
- 9 sectores georreferenciados con puntos de marcador
- Click en cualquier SO del mapa para agregar nuevos sectores automáticamente
- Panel de comparación de rutas

### Ruta de ahorro de gasolina
```
Almacén_Central → Sector_H
  Costo: 11.3 UDG, Waypoints: 486 puntos sobre calles
  Paradas: Sector_A → Sector_B → Sector_H
  Calles: Avenida Bolívar → Calle Sucre → Avenida Juanito Primero...
```

---

## Funcionalidades completas

| Funcionalidad | Estado |
|---|---|
| Gestión de inventario (CRUD) | ✅ |
| Búsqueda por ID (Árbol B) | ✅ |
| Búsqueda por nombre (Hash) | ✅ |
| Creación de órdenes | ✅ |
| Prioridad Express/Normal | ✅ |
| Despacho automático con ruta | ✅ |
| Deshacer último despacho | ✅ |
| Historial completo | ✅ |
| Mapa offline de Maturín | ✅ |
| Rutas sobre calles reales | ✅ |
| Waypoints interpolados (15m) | ✅ |
| Agregar nuevos sectores | ✅ |
| Estrategias de ruta duales | ✅ |
| Persistencia JSON | ✅ |
| 21 tests unitarios | ✅ |

---

## Dificultades encontradas

1. **Generación del grafo vial:** La dependencia `osmnx` requiere geopandas, pyproj,
   y scikit-learn — instalación compleja en entornos con PEP 668.
2. **Tamaño del grafo:** 17,032 aristas generan rutas con cientos de waypoints.
   Fue necesario implementar interpolación para seguir las curvas de calles fielmente.
3. **Rutas greedy:** La izquierda inicial de nearest-neighbor visitaba TODOS los sectores
   de la ciudad. Se corrigió filtrando solo los sectores entre origen y destino.
4. **Tiles offline:** Descarga de +2000 tiles individuales desde OpenStreetMap
   tomó varios minutos y requirió manejar límites del API.

---

## Aprendizajes

- La aplicación práctica de estructuras de datos (Árboles B, Tablas Hash, Colas de
  Prioridad) en un sistema real de reparto.
- Integración de datos geográficos de OpenStreetMap.
- Generación de visualización de mapas 100% offline.
- Arquitectura Flask + MVC con estado global en Python.
- Testing unitario sistemático con pytest.

---

## Referencias

- [Manual de usuario](../MANUAL_USUARIO.md)
- [Justificación de DE no incompletas](JUSTIFICACION.md)
- [Plan de estamos](PLAN.md)
- [Documentación de AlgoHash y Grafo](../IMPLEMENTACION_GRAFOS_HASH.md)
- [Documentación de funciones](../FUNCIONES.md)