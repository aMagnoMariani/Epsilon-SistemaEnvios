# Manual de Usuario — Epsilon_UDO

Sistema Epsilon SistemaEnvios Maturín, Estado Monagas, Venezuela.

## Requisitos

- **Python** 3.8 o superior
- Dependencias del proyecto:

```bash
pip install -r requirements.txt --break-system-packages
```

- **Archivos de datos requeridos**:
  - `datos/grafo_vial.pkl` — grafo vial real (generar con: `python tools/generar_grafo_vial.py`)
  - `datos/mapa_nodos.json` — anclaje de sectores al grafo
  - `static/tiles/` — tiles offline de Maturín (generar con: `python tools/download_tiles.py`)

> **Nota:** Si no se generan el grafo vial ni los tiles, el mapa usará tiles de un archivo local y las rutas serán líneas rectas de Haversine.

## Instalación y ejecución

```bash
# 1. Clonar / descomprimir el repositorio
cd Epsilon_UDO

# 2. Instalar dependencias
pip install -r requirements.txt --break-system-packages

# 3. (Opcional) Generar datos offline
python tools/generar_grafo_vial.py
python tools/download_tiles.py

# 4. Iniciar el servidor
python app.py
```

Abrir en el navegador: **http://localhost:5000**

## Pantallas del sistema

### 1. Dashboard (Inicio)
Métricas generales: productos, órdenes pendientes, despachos, nodos del mapa.

### 2. Inventario (Productos)
- **Agregar producto:** ID, nombre, precio, stock.
- **Buscar por ID:** usa el Árbol B (O(log n)).
- **Buscar por nombre:** usa la Tabla Hash (O(1) promedio).

### 3. Órdenes
- Crear nuevas órdenes (producto, cantidad, destino, prioridad Normal/Express).
- Las Express (prioridad 0) se despachan antes que las Normal (prioridad 1).
- También se pueden crear desde los popups del mapa.

### 4. Despacho
- Despachar la siguiente orden más urgente (botón "Despachar Siguiente").
- Al despachar se calcula automáticamente la ruta óptima con Dijkstra.
- Muestra el costo de gasolina y el tiempo estimado.

### 5. Mapa Logístico
- **Ver sectores** en el mapa de Maturín offline.
- **Calcular ruta:** seleccionar origen y destino, elegir estrategia:
  - **⛽ Ahorro de gasolina:** ruta greedy que pasa por sectores intermedios cercanos.
  - **⚡ Ruta más rápida:** trayecto directo sin paradas.
- **Agregar sector:** clic en cualquier lugar del mapa → elegir nombre y conectar con sector existente. Se ancla automáticamente al grafo vial real.
- **Panel de información** abajo izquierda con costo y calles de la ruta.
- Popup en cada sector para crear órdenes directo desde el mapa.

### 6. Historial
- Ver órdenes despachadas.
- **Deshacer último despacho:** revierte el despacho y restaura el stock.

## Estrategias de ruta

| Estrategia | Algoritmo | Resultado |
|---|---|---|
| Ahorro de gasolina | Greedy nearest-neighbor entre sectores + Dijkstra vial | Visita sectores intermedios |
| Ruta más rápida | Dijkstra directo sobre grafo vial | Origen → Destino sin paradas |

## Persistencia
- Los datos se guardan en `datos/` como JSON.
- Usar **Guardar Datos** desde el Dashboard para persistir manualmente.

## Solución de problemas

| Problema | Solución |
|---|---|
| `No module named 'osmnx'` | `pip install osmnx --break-system-packages` |
| `No module named 'networkx'` | `pip install networkx --break-system-packages` |
| Mapa sin tiles | Ejecutar `python tools/download_tiles.py` |
| Rutas en línea recta | Ejecutar `python tools/generar_grafo_vial.py` para regenerar el grafo |
| Puerto 5000 ocupado | Editar `app.py` y cambiar el puerto |
