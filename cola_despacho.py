"""
Módulo de Cola de Despacho — Unidad III
Cola de prioridad con heapq y pila de historial para operaciones de deshacer.
"""

import heapq
from models.order import Orden
from lista_enlazada import ListaDobleEnlazada


class ColaDespacho:
    """Gestiona las órdenes de envío con una cola de prioridad.
    
    Las órdenes Express (prioridad 0) se despachan antes que las Normales (prioridad 1).
    Incluye una pila de historial para deshacer despachos.
    """

    def __init__(self):
        self._cola = []           # Cola de prioridad (heap)
        self._contador = 0        # Desempate para heapq (FIFO en misma prioridad)
        self.pila_historial = ListaDobleEnlazada[Orden]()  # Historial usando ListaDobleEnlazada LIFO

    def agregar_orden(self, orden: Orden) -> None:
        """Agrega (Enqueue) una orden a la cola de prioridad.
        
        Usa una tupla (prioridad, contador, orden) para el heap.
        El contador asegura orden FIFO cuando dos órdenes tienen la misma prioridad.
        
        Operación: Enqueue (o Push en el contexto del heap).
        Limitación: La inserción en el heap toma tiempo O(log N). La lista
        subyacente en Python puede requerir redimensionamiento ocasional.
        No es thread-safe sin mecanismos de sincronización adicionales.
        
        Args:
            orden: Objeto Orden a agregar.
        """
        heapq.heappush(self._cola, (orden.prioridad, self._contador, orden))
        self._contador += 1

    def despachar_siguiente(self) -> Orden:
        """Despacha (Dequeue) la orden más urgente de la cola.
        
        Extrae el elemento de mayor prioridad (menor valor) de la cola de 
        prioridad y lo inserta (Push) en la pila de historial (LIFO).
        
        Operación: Dequeue (Pop del heap) para la cola y Push para la pila.
        Limitación: Extraer del heap es O(log N). Guardar en la pila (append a 
        la lista) es amortizado O(1). La pila puede crecer indefinidamente y 
        consumir memoria si no se vacía el historial.
        
        Returns:
            La Orden con mayor prioridad (menor valor numérico).
            None si la cola está vacía.
        """
        if not self._cola:
            return None

        prioridad, _, orden = heapq.heappop(self._cola)
        # Guardar en la pila de historial (insertar al final de la ListaDobleEnlazada)
        self.pila_historial.insertar_final(orden)
        return orden

    def deshacer_ultimo_despacho(self) -> Orden:
        """Deshace el último despacho, extrayéndolo (Pop) de la pila de historial.
        
        Saca el último elemento insertado en la pila de historial y lo vuelve 
        a encolar (Enqueue) en la cola de prioridad.
        
        Operación: Pop de la pila LIFO (usando eliminar_ultimo) y Enqueue en la cola de prioridad.
        Limitación: Eliminar el último de nuestra ListaDobleEnlazada es O(1), pero la posterior
        inserción en el heap es O(log N). Depende del tamaño de la cola actual.
        
        Returns:
            La última Orden despachada, o None si no hay historial.
        """
        if len(self.pila_historial) == 0:
            return None

        # Pop de la pila
        orden = self.pila_historial.eliminar_ultimo()
        # Reinsertarla en la cola (Enqueue)
        self.agregar_orden(orden)
        return orden

    def ver_cola(self) -> list:
        """Retorna las órdenes pendientes ordenadas por prioridad.
        
        Returns:
            Lista de objetos Orden ordenados (no modifica el heap).
        """
        # Crear una copia ordenada sin modificar el heap original
        ordenes_ordenadas = sorted(self._cola, key=lambda x: (x[0], x[1]))
        return [item[2] for item in ordenes_ordenadas]

    def ver_historial(self) -> list:
        """Retorna el historial de despachos (el más reciente al final).
        
        Returns:
            Lista de objetos Orden despachados.
        """
        return self.pila_historial.to_list()

    @property
    def pendientes(self) -> int:
        """Cantidad de órdenes pendientes en la cola."""
        return len(self._cola)

    @property
    def despachos_realizados(self) -> int:
        """Cantidad de despachos en el historial."""
        return len(self.pila_historial)

    def esta_vacia(self) -> bool:
        """Verifica si la cola está vacía."""
        return len(self._cola) == 0

    def obtener_ordenes_pendientes_como_dicts(self) -> list:
        """Retorna las órdenes pendientes como lista de diccionarios para serialización."""
        ordenes = self.ver_cola()
        return [o.to_dict() for o in ordenes]
