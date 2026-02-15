
from pydantic import BaseModel


class SubCategoria_item(BaseModel):
    categoria_id: int
    nombre: str
    descripcion: str
    activa: int
    
