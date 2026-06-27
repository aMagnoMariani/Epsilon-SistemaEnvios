"""
Módulo de Lista Enlazada Doble — Unidad III / Estructura personalizada
Implementación de una lista doblemente enlazada para almacenar y gestionar
el historial de despachos u otros datos en la aplicación.
"""

from typing import TypeVar, Generic, Optional, Generator, Callable

T = TypeVar('T')


class NodoDoble(Generic[T]):
    """Nodo para una lista doblemente enlazada.
    
    Almacena un dato de tipo genérico y referencias a los nodos anterior y siguiente.
    """
    __slots__ = ['dato', 'anterior', 'siguiente']

    def __init__(self, dato: T):
        self.dato: T = dato
        self.anterior: Optional[NodoDoble[T]] = None
        self.siguiente: Optional[NodoDoble[T]] = None


class ListaDobleEnlazada(Generic[T]):
    """Estructura de datos Lista Doblemente Enlazada.
    
    Permite almacenar una secuencia de elementos con punteros al anterior y al siguiente.
    Es ideal para representar pilas, colas o colecciones con operaciones en los extremos en O(1).
    """

    def __init__(self):
        """Inicializa una lista doblemente enlazada vacía.
        
        Qué NO hace:
        - No reserva memoria de tamaño fijo (se expande dinámicamente según sea necesario).
        - No es segura para entornos multi-hilo (no es thread-safe) sin bloqueos externos.
        """
        self.cabeza: Optional[NodoDoble[T]] = None
        self.cola: Optional[NodoDoble[T]] = None
        self._tamano: int = 0

    def insertar_inicio(self, dato: T) -> None:
        """Inserta un elemento al inicio de la lista.
        
        Complejidad de tiempo: O(1)
        Complejidad de espacio: O(1) adicional
        
        Qué NO hace:
        - No realiza ordenamiento del dato insertado (no mantiene orden alfabético ni numérico).
        - No valida si el dato está duplicado (permite valores repetidos).
        - No es thread-safe (puede corromper punteros bajo acceso concurrente).
        - No realiza búsquedas para determinar la posición (inserta directamente en la cabeza).
        """
        nuevo_nodo = NodoDoble(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo_nodo
            self.cabeza = nuevo_nodo
        self._tamano += 1

    def insertar_final(self, dato: T) -> None:
        """Inserta un elemento al final de la lista.
        
        Complejidad de tiempo: O(1)
        Complejidad de espacio: O(1) adicional
        
        Qué NO hace:
        - No realiza ordenamiento del dato insertado.
        - No valida si el dato está duplicado.
        - No es thread-safe.
        - No realiza búsquedas para determinar la posición (inserta directamente en la cola).
        """
        nuevo_nodo = NodoDoble(dato)
        if self.cola is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self._tamano += 1

    def eliminar_inicio(self) -> Optional[T]:
        """Elimina y retorna el primer elemento de la lista (cabeza).
        
        Complejidad de tiempo: O(1)
        Complejidad de espacio: O(1)
        
        Qué NO hace:
        - No lanza una excepción si la lista está vacía (retorna None).
        - No es thread-safe.
        - No realiza búsquedas ni elimina otros elementos que no sean el primero.
        """
        if self.cabeza is None:
            return None
        
        temp = self.cabeza
        dato = temp.dato
        
        if self.cabeza == self.cola:
            self.cabeza = None
            self.cola = None
        else:
            self.cabeza = self.cabeza.siguiente
            self.cabeza.anterior = None
            
        self._tamano -= 1
        return dato

    def eliminar_ultimo(self) -> Optional[T]:
        """Elimina y retorna el último elemento de la lista (cola).
        
        Complejidad de tiempo: O(1)
        Complejidad de espacio: O(1)
        
        Qué NO hace:
        - No lanza una excepción si la lista está vacía (retorna None).
        - No es thread-safe.
        - No realiza búsquedas ni elimina otros elementos que no sean el último.
        """
        if self.cola is None:
            return None
            
        temp = self.cola
        dato = temp.dato
        
        if self.cabeza == self.cola:
            self.cabeza = None
            self.cola = None
        else:
            self.cola = self.cola.anterior
            self.cola.siguiente = None
            
        self._tamano -= 1
        return dato

    def eliminar(self, dato: T, comparador: Optional[Callable[[T, T], bool]] = None) -> bool:
        """Busca y elimina la primera aparición de un elemento coincidente en la lista.
        
        Complejidad de tiempo: O(N) en el peor de los casos (requiere buscar el elemento).
        Complejidad de espacio: O(1)
        
        Qué NO hace:
        - No elimina todas las apariciones del dato si está duplicado (solo la primera que encuentre).
        - No funciona en tiempo constante O(1) (a diferencia de eliminar de los extremos).
        - No soporta búsqueda binaria para acelerar la localización del nodo.
        - No es thread-safe.
        """
        actual = self.cabeza
        while actual is not None:
            es_igual = (comparador(actual.dato, dato) if comparador 
                        else actual.dato == dato)
            
            if es_igual:
                if actual == self.cabeza:
                    self.eliminar_inicio()
                elif actual == self.cola:
                    self.eliminar_ultimo()
                else:
                    actual.anterior.siguiente = actual.siguiente
                    actual.siguiente.anterior = actual.anterior
                    self._tamano -= 1
                return True
            actual = actual.siguiente
        return False

    def buscar(self, criterio: Callable[[T], bool]) -> Optional[T]:
        """Busca y retorna el primer elemento en la lista que cumpla con el criterio.
        
        Complejidad de tiempo: O(N) en el peor de los casos.
        Complejidad de espacio: O(1)
        
        Criterio:
            Una función/lambda que recibe un elemento de tipo T y retorna True o False.
            
        Qué NO hace:
        - No soporta búsqueda binaria ya que requiere acceso aleatorio O(1) que esta estructura no tiene.
        - No devuelve todos los elementos que coinciden (solo el primero encontrado desde la cabeza).
        - No devuelve el índice numérico ni el Nodo de la lista (devuelve el dato directamente).
        - No es thread-safe.
        """
        actual = self.cabeza
        while actual is not None:
            if criterio(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None

    def recorrer_adelante(self) -> Generator[T, None, None]:
        """Generador para recorrer la lista en orden, desde la cabeza hasta la cola.
        
        Complejidad de tiempo: O(N) para recorrer toda la lista.
        Complejidad de espacio: O(1)
        
        Qué NO hace:
        - No permite modificar la estructura de la lista (ej. insertar o eliminar nodos) de forma segura durante la iteración.
        - No es seguro contra modificaciones concurrentes en otros hilos.
        - No realiza acceso aleatorio; avanza estrictamente nodo por nodo.
        """
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def recorrer_atras(self) -> Generator[T, None, None]:
        """Generador para recorrer la lista en orden inverso, desde la cola hasta la cabeza.
        
        Complejidad de tiempo: O(N) para recorrer toda la lista en reversa.
        Complejidad de espacio: O(1)
        
        Qué NO hace:
        - No permite modificar la estructura de la lista de forma segura durante la iteración.
        - No es seguro contra modificaciones concurrentes.
        - No realiza acceso aleatorio; retrocede estrictamente nodo por nodo.
        """
        actual = self.cola
        while actual is not None:
            yield actual.dato
            actual = actual.anterior

    def to_list(self) -> list[T]:
        """Convierte la lista enlazada a una lista estándar de Python.
        
        Complejidad de tiempo: O(N)
        Complejidad de espacio: O(N) (crea una nueva lista con copias de las referencias a los datos).
        
        Qué NO hace:
        - No mantiene los enlaces entre nodos (retorna un array plano de Python).
        - No realiza copias profundas (deep copy) de los datos contenidos.
        """
        return list(self.recorrer_adelante())

    def __iter__(self) -> Generator[T, None, None]:
        """Permite iterar sobre los elementos usando bucles estándar (for x in lista).
        
        Qué NO hace:
        - No es thread-safe.
        - No permite iterar en reversa de forma nativa con este iterador (usar reversed() o recorrer_atras()).
        """
        return self.recorrer_adelante()

    def __reversed__(self) -> Generator[T, None, None]:
        """Permite iterar sobre los elementos en orden inverso usando la función reversed(lista).
        
        Qué NO hace:
        - No modifica la lista original ni cambia los punteros de los nodos.
        - No es thread-safe.
        """
        return self.recorrer_atras()

    def __len__(self) -> int:
        """Devuelve el tamaño actual de la lista.
        
        Complejidad de tiempo: O(1)
        Complejidad de espacio: O(1)
        
        Qué NO hace:
        - No recorre la lista para contar sus elementos en tiempo real (mantiene un atributo en caché).
        """
        return self._tamano
