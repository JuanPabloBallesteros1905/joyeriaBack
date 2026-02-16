



from pydantic import BaseModel 

class Produto_item (BaseModel):
    nombre: str
    imagen: str
    descripcion: str
    categoria_id: int
    subcategoria_id: int
    material_id: int
    peso: str
    tipo_medida: str
    dimensiones: str
    precio_compra: str
    precio_venta: str

    
    

