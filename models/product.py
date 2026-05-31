"""
Modelo `Producto`.
"""
class Producto:
    """Representa un producto en el inventario.
    Usa __slots__ para optimización de memoria al evitar
    la creación de un __dict__ por instancia.
    """
    __slots__ = ['id', 'nombre', 'precio', 'stock']

    def __init__(self, id: int, nombre: str, precio: float, stock: int):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'stock': self.stock
        }

    @classmethod
    def from_dict(cls, datos: dict) -> 'Producto':
        return cls(
            id=datos['id'],
            nombre=datos['nombre'],
            precio=datos['precio'],
            stock=datos['stock']
        )

    def __repr__(self):
        return f"Producto(id={self.id}, nombre='{self.nombre}', precio=${self.precio}, stock={self.stock})"
