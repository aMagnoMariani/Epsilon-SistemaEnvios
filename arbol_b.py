"""
Módulo Árbol B (e.g., Árbol 2-3 cuando M=3)
Estructura de datos balanceada para búsqueda, inserción y actualización eficiente.
"""

from typing import Optional, List, Any

class NodoB:
    """
    Nodo de un Árbol B.
    
    Atributos:
        leaf (bool): Indica si el nodo es una hoja.
        keys (List[Any]): Lista de elementos (objetos Producto) almacenados en el nodo.
        children (List[NodoB]): Lista de punteros a los nodos hijos.
    """
    __slots__ = ['leaf', 'keys', 'children']

    def __init__(self, leaf: bool = True):
        self.leaf = leaf
        self.keys: List[Any] = []
        self.children: List['NodoB'] = []

    def __repr__(self):
        tipo = "Hoja" if self.leaf else "Interno"
        ids = [k.id for k in self.keys]
        return f"NodoB({tipo}, Llaves={ids})"


class ArbolB:
    """
    Árbol B de Orden M.
    
    Cuando M=3, esta estructura funciona exactamente como un Árbol 2-3.
    Las llaves en los nodos son objetos (como Producto) y se comparan por su atributo '.id'.
    """

    def __init__(self, M: int = 3):
        """
        Inicializa un Árbol B de orden M.
        
        Args:
            M (int): El orden del árbol (máximo número de hijos que puede tener un nodo).
                     Debe ser mayor o igual a 3. Por defecto es 3 (Árbol 2-3).
        """
        if M < 3:
            raise ValueError("El orden M del Árbol B debe ser al menos 3.")
        self.M = M
        self.raiz = NodoB(leaf=True)
        self._tamano = 0

    @property
    def tamano(self) -> int:
        """Retorna el número total de llaves (productos) en el árbol."""
        return self._tamano

    def __len__(self) -> int:
        return self._tamano

    def buscar(self, id: int, nodo: Optional[NodoB] = None) -> Optional[Any]:
        """
        Busca un elemento por su ID en el árbol.
        
        Args:
            id (int): El ID a buscar.
            nodo (NodoB, opcional): El subárbol en el cual buscar. Si es None, se busca desde la raíz.
            
        Returns:
            El objeto con el ID especificado si se encuentra, de lo contrario None.
        """
        if nodo is None:
            nodo = self.raiz

        i = 0
        while i < len(nodo.keys) and id > nodo.keys[i].id:
            i += 1

        if i < len(nodo.keys) and id == nodo.keys[i].id:
            return nodo.keys[i]

        if nodo.leaf:
            return None

        return self.buscar(id, nodo.children[i])

    def insertar(self, producto: Any) -> None:
        """
        Inserta un producto en el árbol B.
        Si el ID del producto ya existe, actualiza el producto en el lugar sin alterar la estructura.
        
        Args:
            producto: El objeto a insertar (debe tener un atributo 'id').
        """
        # Si ya existe el producto con este ID, simplemente lo actualizamos
        # para evitar duplicados en el árbol.
        if self._actualizar_producto(self.raiz, producto):
            return

        # Si no existía, realizamos la inserción y aumentamos el tamaño
        resultado_division = self._insertar_recursivo(self.raiz, producto)
        
        # Si la raíz se divide, el árbol crece hacia arriba
        if resultado_division is not None:
            promoted_key, left_node, right_node = resultado_division
            
            # Crear una nueva raíz que deja de ser hoja y tiene como hijos
            # las dos particiones de la raíz anterior dividida.
            nueva_raiz = NodoB(leaf=False)
            nueva_raiz.keys = [promoted_key]
            nueva_raiz.children = [left_node, right_node]
            self.raiz = nueva_raiz
            
        self._tamano += 1

    def _actualizar_producto(self, nodo: NodoB, producto: Any) -> bool:
        """
        Busca un producto por su ID de manera recursiva y lo actualiza si existe.
        Retorna True si lo actualizó, False en caso contrario.
        """
        i = 0
        while i < len(nodo.keys) and producto.id > nodo.keys[i].id:
            i += 1

        if i < len(nodo.keys) and producto.id == nodo.keys[i].id:
            nodo.keys[i] = producto
            return True

        if nodo.leaf:
            return False

        return self._actualizar_producto(nodo.children[i], producto)

    def _insertar_recursivo(self, nodo: NodoB, producto: Any) -> Optional[tuple]:
        """
        Realiza la inserción recursiva bottom-up (de abajo hacia arriba).
        
        Args:
            nodo: Nodo actual en el recorrido.
            producto: El objeto Producto a insertar.
            
        Returns:
            None si no hubo división en el subárbol hijo.
            Una tupla (promoted_key, left_node, right_node) si el nodo hijo se dividió.
        """
        # Buscar el punto de inserción (índice i de la llave o hijo)
        i = 0
        while i < len(nodo.keys) and producto.id > nodo.keys[i].id:
            i += 1

        if nodo.leaf:
            # Caso Base: Es una hoja, insertamos la nueva llave directamente en orden
            nodo.keys.insert(i, producto)
        else:
            # Caso Recursivo: Insertamos en el hijo i correspondiente
            resultado = self._insertar_recursivo(nodo.children[i], producto)
            if resultado is not None:
                # El hijo i se dividió. Recibimos la llave promovida y los dos nuevos nodos resultantes.
                promoted_key, left_node, right_node = resultado
                
                # Insertamos la llave promovida en el nodo actual
                nodo.keys.insert(i, promoted_key)
                # Reemplazamos el hijo original que desbordó con las dos nuevas partes
                nodo.children[i] = left_node
                nodo.children.insert(i + 1, right_node)

        # =========================================================================
        # DETALLE DE DIVISIÓN DE NODOS (NODE SPLITTING)
        # =========================================================================
        # En un Árbol B de orden M, un nodo puede almacenar a lo sumo M - 1 llaves.
        # Si un nodo acumula M llaves tras una inserción directa (si es hoja) o tras
        # recibir una llave promovida por un hijo (si es interno), este nodo ha
        # desbordado (overflow) y DEBE dividirse.
        #
        # Para dividir el nodo:
        # 1. Se calcula la llave del medio en el índice 'mid = (M - 1) // 2'.
        #    - Para M=3 (Árbol 2-3), el nodo tiene 3 llaves (índices 0, 1, 2).
        #      La llave del medio es la de índice 1.
        # 2. Se divide el nodo en dos hermanos:
        #    - El nodo izquierdo ('izq') conserva las llaves anteriores a la del medio.
        #    - El nodo derecho ('der') conserva las llaves posteriores a la del medio.
        # 3. Si el nodo original era interno (no hoja), también se dividen sus hijos:
        #    - El nodo izquierdo se queda con los primeros 'mid + 1' hijos.
        #    - El nodo derecho se queda con los hijos restantes desde 'mid + 1'.
        # 4. La llave del medio ('promoted_key') se promueve hacia el nodo padre junto
        #    con las referencias a 'izq' y 'der'.
        # =========================================================================
        if len(nodo.keys) >= self.M:
            return self._dividir_nodo(nodo)

        return None

    def _dividir_nodo(self, nodo: NodoB) -> tuple:
        """
        Divide un nodo desbordado y retorna la llave del medio y las dos nuevas mitades.
        """
        mid = (self.M - 1) // 2
        promoted_key = nodo.keys[mid]

        # Crear nodo izquierdo y asignarle la primera mitad de llaves
        izq = NodoB(leaf=nodo.leaf)
        izq.keys = nodo.keys[:mid]

        # Crear nodo derecho y asignarle la segunda mitad de llaves
        der = NodoB(leaf=nodo.leaf)
        der.keys = nodo.keys[mid + 1:]

        # Si el nodo no es una hoja, también debemos dividir y redistribuir sus hijos
        if not nodo.leaf:
            izq.children = nodo.children[:mid + 1]
            der.children = nodo.children[mid + 1:]

        return promoted_key, izq, der

    # =========================================================================
    # DETALLE DE FUSIÓN DE NODOS Y DETALLES NO MANEJADOS (ELIMINACIÓN)
    # =========================================================================
    # Este algoritmo NO implementa la eliminación de llaves.
    #
    # La eliminación en un Árbol B (o Árbol 2-3) es sustancialmente más compleja
    # que la inserción y requiere operaciones inversas a la división para mantener
    # el balanceo y la propiedad de llenado mínimo de los nodos.
    #
    # Lo que no se implementa y cómo se solucionaría:
    # 1. Fusión de nodos (Node Fusion):
    #    - Si eliminamos una llave de un nodo y este queda con menos de las llaves
    #      mínimas requeridas (menos de ceil(M/2) - 1 llaves; para M=3, menos de 1 llave,
    #      es decir, vacío), ocurre un subdesbordo (underflow).
    #    - Si el nodo hermano inmediato tiene sólo la cantidad mínima de llaves,
    #      no podemos pedirle prestado. En este caso, se deben fusionar (combinar)
    #      el nodo actual, su hermano y la llave del padre que los separa en un solo
    #      nodo. Esto puede propagar el subdesbordo hacia arriba.
    # 2. Redistribución / Préstamo de llaves (Borrowing):
    #    - Si ocurre underflow en un nodo y su hermano inmediato tiene más de la
    #      cantidad mínima de llaves, se realiza una rotación: se toma una llave
    #      del padre para el nodo con underflow, y la llave sobrante del hermano
    #      se promueve para reemplazar la del padre.
    # 3. Eliminación en nodos internos:
    #    - Si la llave a eliminar está en un nodo interno, no se puede quitar directamente.
    #      Se debe buscar su predecesor o sucesor inorden (que siempre estará en una hoja),
    #      reemplazar el valor por ese predecesor/sucesor y luego proceder a eliminarlo
    #      físicamente de la hoja correspondiente, aplicando las reglas de underflow/fusión.
    # =========================================================================

    def actualizar_stock(self, id: int, cantidad: int) -> bool:
        """
        Modifica el stock de un producto en el árbol B.
        
        Args:
            id: ID del producto.
            cantidad: Cantidad a restar (positiva) o sumar (negativa) al stock.
        
        Returns:
            True si la operación fue exitosa, False si no hay stock suficiente
            o el producto no existe.
        """
        producto = self.buscar(id)
        if producto is None:
            return False

        nuevo_stock = producto.stock - cantidad
        if nuevo_stock < 0:
            return False

        producto.stock = nuevo_stock
        return True

    def restaurar_stock(self, id: int, cantidad: int) -> bool:
        """
        Restaura stock de un producto (para operación de deshacer).
        
        Args:
            id: ID del producto.
            cantidad: Cantidad a sumar al stock.
        
        Returns:
            True si la operación fue exitosa.
        """
        producto = self.buscar(id)
        if producto is None:
            return False

        producto.stock += cantidad
        return True

    def obtener_todos(self) -> list:
        """
        Realiza un recorrido inorden del árbol. Retorna todos los productos ordenados por ID.
        
        Returns:
            Lista de objetos Producto en orden ascendente de ID.
        """
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo: NodoB, resultado: list) -> None:
        """Recorrido inorden recursivo de un Árbol B."""
        for i in range(len(nodo.keys)):
            # Primero visitar el hijo izquierdo de la llave i (si existe)
            if not nodo.leaf:
                self._inorden(nodo.children[i], resultado)
            # Luego registrar la llave i
            resultado.append(nodo.keys[i])
        
        # Finalmente, visitar el hijo derecho de la última llave (si existe)
        if not nodo.leaf:
            self._inorden(nodo.children[-1], resultado)
