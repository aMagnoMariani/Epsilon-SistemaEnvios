"""
Módulo Tabla Hash — Unidad III
Implementación de tabla hash con resolución de colisiones por encadenamiento (chaining).

REPRESENTACIÓN ELEGIDA:
- Se utiliza una lista de listas (buckets) donde cada bucket contiene pares clave-valor.
- Esta representación permite manejar colisiones de manera eficiente mediante encadenamiento.
- Cada posición de la tabla es una lista que puede contener múltiples elementos con el mismo hash.

FUNCIÓN HASH:
- Se utiliza la función hash() nativa de Python combinada con módulo para mapear claves a índices.
- Para claves numéricas (como IDs de productos), el hash es directo: hash(clave) % capacidad.
- Para claves string, Python's hash() genera un valor numérico que luego se reduce con módulo.

LIMITACIONES Y RESOLUCIÓN DE COLISIONES:
- COLISIONES: Ocurren cuando dos claves diferentes producen el mismo índice después de aplicar la función hash.
- RESOLUCIÓN: Se usa encadenamiento (chaining) con listas. Cada bucket puede contener múltiples elementos.
- FACTOR DE CARGA: Cuando el número de elementos supera el 75% de la capacidad, se redimensiona la tabla.
- COMPLEJIDAD:
  - Mejor caso: O(1) - acceso directo sin colisiones
  - Peor caso: O(n) - todas las claves colisionan en el mismo bucket
  - Caso promedio: O(1) con buen factor de carga y función hash distribuida
"""

from typing import Any, Optional, List, Tuple


class TablaHash:
    """Implementación de tabla hash con resolución de colisiones por encadenamiento."""

    def __init__(self, capacidad_inicial: int = 10):
        """Inicializa la tabla hash con una capacidad inicial.
        
        Args:
            capacidad_inicial: Tamaño inicial de la tabla (número de buckets).
                              Por defecto es 10, pero se redimensiona automáticamente.
        """
        self.capacidad = capacidad_inicial
        self.tabla: List[List[Tuple[Any, Any]]] = [[] for _ in range(capacidad_inicial)]
        self.tamano = 0  # Número total de elementos almacenados
        self.factor_carga_max = 0.75  # Umbral para redimensionamiento

    def _hash(self, clave: Any) -> int:
        """Calcula el índice de la tabla para una clave dada.
        
        Esta función hash utiliza el método hash() nativo de Python y lo reduce
        usando el operador módulo para asegurar que el índice esté dentro de los
        límites de la tabla.
        
        Args:
            clave: La clave a hashear (puede ser int, str, o cualquier objeto hasheable).
        
        Returns:
            Índice en el rango [0, capacidad-1].
        
        Nota:
            - Para claves numéricas (IDs de productos), el hash es eficiente.
            - Para strings, Python's hash() genera valores distribuidos uniformemente.
            - La función hash de Python es consistente dentro de una misma ejecución.
        """
        # Usamos hash() de Python y abs() para evitar índices negativos
        # Luego aplicamos módulo para asegurar que esté dentro de los límites
        return abs(hash(clave)) % self.capacidad

    def _redimensionar(self) -> None:
        """Redimensiona la tabla cuando el factor de carga supera el umbral.
        
        Este método duplica la capacidad de la tabla y rehashea todos los elementos
        para mantener una distribución uniforme y evitar colisiones excesivas.
        
        Proceso:
        1. Crear una nueva tabla con el doble de capacidad.
        2. Rehashear cada elemento de la tabla actual en la nueva tabla.
        3. Reemplazar la tabla antigua con la nueva.
        
        Complejidad: O(n) donde n es el número de elementos.
        """
        nueva_capacidad = self.capacidad * 2
        nueva_tabla: List[List[Tuple[Any, Any]]] = [[] for _ in range(nueva_capacidad)]
        
        # Rehashear todos los elementos
        for bucket in self.tabla:
            for clave, valor in bucket:
                nuevo_indice = abs(hash(clave)) % nueva_capacidad
                nueva_tabla[nuevo_indice].append((clave, valor))
        
        self.tabla = nueva_tabla
        self.capacidad = nueva_capacidad

    def insertar(self, clave: Any, valor: Any) -> None:
        """Inserta o actualiza un par clave-valor en la tabla.
        
        Args:
            clave: La clave del elemento (debe ser hasheable).
            valor: El valor a almacenar.
        
        Comportamiento:
            - Si la clave ya existe, actualiza su valor.
            - Si la clave no existe, agrega un nuevo par clave-valor.
            - Si el factor de carga supera el umbral, redimensiona la tabla.
        
        Complejidad promedio: O(1)
        """
        # Verificar factor de carga y redimensionar si es necesario
        if self.tamano / self.capacidad > self.factor_carga_max:
            self._redimensionar()
        
        indice = self._hash(clave)
        bucket = self.tabla[indice]
        
        # Buscar si la clave ya existe en el bucket
        for i, (clave_existente, _) in enumerate(bucket):
            if clave_existente == clave:
                # Clave encontrada: actualizar valor
                bucket[i] = (clave, valor)
                return
        
        # Clave no encontrada: insertar nuevo par
        bucket.append((clave, valor))
        self.tamano += 1

    def buscar(self, clave: Any) -> Optional[Any]:
        """Busca un valor por su clave en la tabla.
        
        Args:
            clave: La clave a buscar.
        
        Returns:
            El valor asociado a la clave, o None si no existe.
        
        Complejidad promedio: O(1)
        Peor caso (todas las claves colisionan): O(n)
        """
        indice = self._hash(clave)
        bucket = self.tabla[indice]
        
        for clave_existente, valor in bucket:
            if clave_existente == clave:
                return valor
        
        return None

    def eliminar(self, clave: Any) -> bool:
        """Elimina un par clave-valor de la tabla.
        
        Args:
            clave: La clave del elemento a eliminar.
        
        Returns:
            True si se eliminó el elemento, False si no se encontró.
        
        Complejidad promedio: O(1)
        """
        indice = self._hash(clave)
        bucket = self.tabla[indice]
        
        for i, (clave_existente, _) in enumerate(bucket):
            if clave_existente == clave:
                del bucket[i]
                self.tamano -= 1
                return True
        
        return False

    def existe(self, clave: Any) -> bool:
        """Verifica si una clave existe en la tabla.
        
        Args:
            clave: La clave a verificar.
        
        Returns:
            True si la clave existe, False en caso contrario.
        
        Complejidad promedio: O(1)
        """
        return self.buscar(clave) is not None

    def obtener_todos(self) -> List[Tuple[Any, Any]]:
        """Retorna todos los pares clave-valor almacenados en la tabla.
        
        Returns:
            Lista de tuplas (clave, valor) con todos los elementos.
        
        Complejidad: O(n) donde n es el número de elementos.
        """
        elementos = []
        for bucket in self.tabla:
            elementos.extend(bucket)
        return elementos

    def obtener_claves(self) -> List[Any]:
        """Retorna todas las claves almacenadas en la tabla.
        
        Returns:
            Lista de todas las claves.
        
        Complejidad: O(n)
        """
        return [clave for clave, _ in self.obtener_todos()]

    def limpiar(self) -> None:
        """Elimina todos los elementos de la tabla.
        
        Complejidad: O(capacidad) - recrea la tabla vacía.
        """
        self.tabla = [[] for _ in range(self.capacidad)]
        self.tamano = 0

    def __len__(self) -> int:
        """Retorna el número de elementos en la tabla."""
        return self.tamano

    def __str__(self) -> str:
        """Representación en string de la tabla para debugging."""
        resultado = []
        for i, bucket in enumerate(self.tabla):
            if bucket:
                resultado.append(f"Bucket {i}: {bucket}")
        return "\n".join(resultado) if resultado else "Tabla vacía"


# ============================================
# EJEMPLO DE USO Y PRUEBAS
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE TABLA HASH")
    print("=" * 60)
    
    # Crear tabla hash
    tabla = TablaHash(capacidad_inicial=5)
    
    # Insertar elementos
    print("\n1. Insertando elementos...")
    tabla.insertar(1, "Producto A")
    tabla.insertar(2, "Producto B")
    tabla.insertar(3, "Producto C")
    tabla.insertar(11, "Producto AA")  # Colisionará con 1 (hash(1) % 5 == hash(11) % 5)
    tabla.insertar("nombre", "Producto D")
    
    print(f"Elementos insertados: {len(tabla)}")
    print(f"Capacidad actual: {tabla.capacidad}")
    
    # Buscar elementos
    print("\n2. Buscando elementos...")
    print(f"Buscar clave 1: {tabla.buscar(1)}")
    print(f"Buscar clave 11: {tabla.buscar(11)}")
    print(f"Buscar clave 'nombre': {tabla.buscar('nombre')}")
    print(f"Buscar clave 99: {tabla.buscar(99)}")  # No existe
    
    # Verificar existencia
    print("\n3. Verificando existencia...")
    print(f"Existe clave 2: {tabla.existe(2)}")
    print(f"Existe clave 99: {tabla.existe(99)}")
    
    # Actualizar valor
    print("\n4. Actualizando valor...")
    tabla.insertar(1, "Producto A Actualizado")
    print(f"Buscar clave 1 después de actualizar: {tabla.buscar(1)}")
    
    # Eliminar elemento
    print("\n5. Eliminando elemento...")
    eliminado = tabla.eliminar(2)
    print(f"¿Se eliminó clave 2? {eliminado}")
    print(f"Buscar clave 2 después de eliminar: {tabla.buscar(2)}")
    
    # Mostrar estado de la tabla
    print("\n6. Estado de la tabla:")
    print(tabla)
    
    # Obtener todos los elementos
    print("\n7. Todos los elementos:")
    for clave, valor in tabla.obtener_todos():
        print(f"  {clave}: {valor}")
    
    # Prueba de redimensionamiento
    print("\n8. Prueba de redimensionamiento...")
    tabla_pequena = TablaHash(capacidad_inicial=3)
    print(f"Capacidad inicial: {tabla_pequena.capacidad}")
    
    for i in range(10):
        tabla_pequena.insertar(i, f"Valor {i}")
    
    print(f"Capacidad después de insertar 10 elementos: {tabla_pequena.capacidad}")
    print(f"Elementos totales: {len(tabla_pequena)}")
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)
