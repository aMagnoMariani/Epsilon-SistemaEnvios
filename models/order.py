"""
Modelo `Orden`.
"""
class Orden:
    """Representa una orden de compra de un cliente.
    Usa __slots__ para optimización de memoria.
    Prioridad: 0 = Express, 1 = Normal
    """
    __slots__ = ['id', 'producto_id', 'cantidad', 'destino', 'prioridad']

    def __init__(self, id: int, producto_id: int, cantidad: int, destino: str, prioridad: int = 1):
        self.id = id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.destino = destino
        self.prioridad = prioridad

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'destino': self.destino,
            'prioridad': self.prioridad
        }

    @classmethod
    def from_dict(cls, datos: dict) -> 'Orden':
        return cls(
            id=datos['id'],
            producto_id=datos['producto_id'],
            cantidad=datos['cantidad'],
            destino=datos['destino'],
            prioridad=datos.get('prioridad', 1)
        )

    def __lt__(self, otro):
        return self.prioridad < otro.prioridad

    def __repr__(self):
        tipo = "Express" if self.prioridad == 0 else "Normal"
        return f"Orden(id={self.id}, producto_id={self.producto_id}, destino='{self.destino}', tipo={tipo})"

    @property
    def tipo_prioridad(self):
        return "Express" if self.prioridad == 0 else "Normal"
