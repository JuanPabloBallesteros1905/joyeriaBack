from pydantic import BaseModel 




class ProductoBase(BaseModel):
    producto: Produto_item
    detalle: ProductosDetalles
    imagen: ImagenProducto


    



class Produto_item (BaseModel):
    nombre: str    
    descripcion: str
    categoria_id: int
    subcategoria_id: int
    material_id: int
    peso: float
    precio: float
    activo: int
    destacado: int

    

     

class ProductosDetalles(BaseModel):
    
    medida: int
    unidad: str
    precio: float
    precio_compra: float
    activo: int



class ImagenProducto (BaseModel):
    
    url: str
