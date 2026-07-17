# Implementación de Grafos y Tablas Hash

## Resumen de Cambios

Este documento describe la implementación y mejora de estructuras de datos de grafos y tablas hash en el Sistema de Logística de Última Milla.

## 1. Implementación de Tabla Hash

### Archivo Nuevo: `tabla_hash.py`

Se ha creado una implementación completa de tabla hash con las siguientes características:

#### Representación Elegida
- **Estructura**: Lista de listas (buckets) donde cada bucket contiene pares clave-valor
- **Resolución de colisiones**: Encadenamiento (chaining) con listas
- **Redimensionamiento automático**: Cuando el factor de carga supera 75%, la tabla se duplica

#### Función Hash
- Utiliza la función `hash()` nativa de Python combinada con módulo
- Para claves numéricas: `hash(clave) % capacidad`
- Para claves string: Python's `hash()` genera un valor numérico distribuido uniformemente
- Case-insensitive para búsquedas por nombre de productos

#### Limitaciones y Resolución de Colisiones
- **Colisiones**: Ocurren cuando dos claves diferentes producen el mismo índice
- **Resolución**: Encadenamiento con listas - cada bucket puede contener múltiples elementos
- **Factor de carga**: Umbral del 75% para redimensionamiento automático
- **Complejidad**:
  - Mejor caso: O(1) - acceso directo sin colisiones
  - Peor caso: O(n) - todas las claves colisionan en el mismo bucket
  - Caso promedio: O(1) con buen factor de carga

#### Métodos Implementados
- `insertar(clave, valor)`: Inserta o actualiza un par clave-valor
- `buscar(clave)`: Busca un valor por su clave
- `eliminar(clave)`: Elimina un par clave-valor
- `existe(clave)`: Verifica si una clave existe
- `obtener_todos()`: Retorna todos los pares clave-valor
- `obtener_claves()`: Retorna todas las claves
- `limpiar()`: Elimina todos los elementos

#### Pruebas Incluidas
El archivo incluye pruebas exhaustivas que demuestran:
- Inserción de elementos
- Búsqueda de elementos existentes y no existentes
- Manejo de colisiones
- Actualización de valores
- Eliminación de elementos
- Redimensionamiento automático

## 2. Mejoras al Código de Grafos

### Archivo Modificado: `mapa_logistico.py`

Se han agregado comentarios detallados explicando:

#### Representación Elegida
- **Lista de Adyacencia**: Implementada como diccionario de diccionarios
- **Estructura**: `{nodo_origen: {nodo_destino: {'gasolina': costo, 'tiempo': costo}, ...}, ...}`
- **Ventajas**: Eficiente para grafos dispersos, acceso O(1) a vecinos y costos

#### Algoritmo de Recorrido
- **Dijkstra**: Para encontrar la ruta de menor costo
- **Cola de prioridad**: Utiliza `heapq` para procesar siempre el nodo con menor costo acumulado
- **Complejidad**: O((V + E) log V) donde V es el número de vértices y E el número de aristas
- **Garantía**: Encuentra la ruta óptima en grafos con pesos no negativos

#### Limitaciones
- No maneja pesos negativos (Dijkstra no es adecuado)
- Para grafos muy densos, una matriz de adyacencia podría ser más eficiente
- Recalcula la ruta completa cada vez (sin caché)

#### Comentarios Agregados
- Explicación detallada de cada paso del algoritmo Dijkstra
- Documentación de la fórmula de Haversine para cálculo de distancias
- Complejidad de cada método
- Formato esperado del JSON de entrada

## 3. Integración en el Sistema

### Archivo Modificado: `core.py`

Se ha integrado la tabla hash en el sistema principal:

#### Cambios Realizados
1. **Importación de TablaHash**: Se importa la clase `TablaHash` del módulo `tabla_hash`
2. **Instancia Global**: Se crea `tabla_hash_productos` como estructura global
3. **Indexación Dual**: 
   - Árbol BST: Indexa productos por ID (O(log n))
   - Tabla Hash: Indexa productos por nombre (O(1) promedio)
4. **Función de Búsqueda**: Se agrega `buscar_producto_por_nombre()` para búsquedas rápidas por nombre
5. **Inicialización**: Al cargar productos, se indexan en ambas estructuras
6. **Logging**: Se muestra el número de entradas en el índice hash al iniciar

#### Uso Práctico
```python
# Búsqueda por ID (Árbol BST)
producto = arbol.buscar(105)  # O(log n)

# Búsqueda por nombre (Tabla Hash)
producto = buscar_producto_por_nombre("Samsung Galaxy")  # O(1) promedio
```

## 4. Estructuras de Datos del Sistema

El sistema ahora implementa las siguientes estructuras de datos:

| Estructura | Propósito | Complejidad | Archivo |
|------------|-----------|-------------|---------|
| **Árbol BST** | Búsqueda por ID de producto | O(log n) búsqueda, O(log n) inserción | `arbol_inventario.py` |
| **Tabla Hash** | Búsqueda por nombre de producto | O(1) promedio búsqueda, O(1) inserción | `tabla_hash.py` |
| **Cola de Prioridad** | Gestión de órdenes por urgencia | O(log n) inserción, O(log n) extracción | `cola_despacho.py` |
| **Pila** | Historial de despachos (deshacer) | O(1) push/pop | `cola_despacho.py` |
| **Grafo** | Cálculo de rutas óptimas | O((V+E) log V) Dijkstra | `mapa_logistico.py` |

## 5. Archivos Modificados/Creados

### Archivos Creados
- `tabla_hash.py`: Implementación completa de tabla hash con pruebas

### Archivos Modificados
- `mapa_logistico.py`: Agregados comentarios explicativos detallados
- `core.py`: Integración de tabla hash en el sistema

## 6. Ejecución de Pruebas

Para probar la tabla hash independientemente:

```bash
python tabla_hash.py
```

Esto ejecutará las pruebas incluidas que demuestran:
- Inserción y búsqueda
- Manejo de colisiones
- Redimensionamiento automático
- Actualización y eliminación

## 7. Beneficios de la Implementación

### Tabla Hash
- **Búsqueda ultra rápida**: O(1) promedio vs O(n) en búsqueda lineal
- **Case-insensitive**: Facilita búsquedas por nombre sin importar mayúsculas/minúsculas
- **Auto-redimensionamiento**: Mantiene buen rendimiento con crecimiento de datos
- **Complemento al BST**: Permite búsquedas por nombre además de por ID

### Grafo con Documentación
- **Mejor comprensión**: Comentarios detallados facilitan mantenimiento
- **Claridad algorítmica**: Explicación paso a paso de Dijkstra
- **Documentación de limitaciones**: Permite tomar decisiones informadas sobre uso

## 8. Próximos Pasos Sugeridos

1. **Agregar interfaz web** para búsqueda por nombre de producto usando la tabla hash
2. **Implementar caché de rutas** en el grafo para evitar recálculos
3. **Agregar métricas** de rendimiento para comparar BST vs Hash
4. **Implementar función hash personalizada** para mejor distribución si es necesario
5. **Agregar pruebas unitarias** automáticas con pytest

## Conclusión

Se ha implementado una tabla hash completa con documentación exhaustiva y se ha mejorado significativamente la documentación del código de grafos. La tabla hash está integrada en el sistema y complementa al árbol BST existente, permitiendo búsquedas eficientes tanto por ID como por nombre de producto.
