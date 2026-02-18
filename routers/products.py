from fastapi import APIRouter,  File, UploadFile, Depends, Header, HTTPException
from fastapi import status
from jose import JWTError
from app.utils.token import decode_token
from typing import Optional
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.productos_model import ProductosModel
from app.models.materials_model import MaterialsModel
from app.models.imgenes_productos_model import ImagenProducto
from app.models.productos_v2_model import ProductoVariante
from app.models.categorias_model import CategoriesModel
from app.models.sub_categorias_model import Subcategoria
from app.schemas.productos import ProductoBase
from app.schemas.subcategoria import SubCategoria_item



from typing import Union
 


router = APIRouter(prefix="/productos", tags=["products"])


 


IMAGEN = "images/"


@router.post("/create", summary="Create product")
async def create_joya(
    db: Session = Depends(get_db),
    producto: ProductoBase = None):






    try:
        datos = producto.dict()

        producto_data = datos["producto"]
        detalle_data = datos["detalle"]
        imagen_data = datos["imagen"]

        new_product = ProductosModel(**producto_data)

        db.add(new_product)
        db.flush()  # Flush to get the new product ID


        new_detalle = ProductoVariante(
            producto_id=new_product.id,
            medida=detalle_data["medida"],
            unidad=detalle_data["unidad"],
            precio=detalle_data["precio"],
            precio_compra=detalle_data["precio_compra"],
            activo=detalle_data["activo"]
        )

        db.add(new_detalle)
        db.commit()  # Commit to save the product and get the ID for the image

        
        new_image = ImagenProducto(
            producto_id=new_product.id,
            url=imagen_data["url"]

        )


        # with open(f"{IMAGEN}{imagen_data['url']}", "rb") as image_file:
        #     image_content = image_file.read()
        #     # Aquí puedes guardar el contenido de la imagen en tu base de datos o sistema de archivos



        db.add(new_image)
        db.commit()
        
       
        

        


        

        print(datos)

        

    except Exception as e:
        return {"error": str(e)}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    

    return {"message": "Producto creado exitosamente", "data": datos}

 
    
 
 






    
    
@router.post("/update/{product_id}", summary="Update| product")
def update_product(
    db: Session = Depends(get_db),):


    return {"message": "Producto actualizado exitosamente"} 
    

    
    
@router.post("/delete/{product_id}", summary="Delete product")
def delete_product(
    db: Session = Depends(get_db),):


    return {"message": "Producto eliminado exitosamente"} 
    






@router.get("/", summary="List products with image")
def list_products(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)):



    try:
        products = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                ProductosModel.descripcion,
                ImagenProducto.url,
                MaterialsModel.nombre.label("material_nombre"),
                MaterialsModel.id.label("material_id"),
                ProductoVariante.medida,
                ProductoVariante.unidad,
                ProductoVariante.precio,
                ProductoVariante.precio_compra,
                CategoriesModel.nombre.label("categoria_nombre"),
                CategoriesModel.id.label("categoria_id")),
                Subcategoria.nombre.label("subcategoria_nombre")
                
                
            .join(Subcategoria)
            .join(ImagenProducto)
            .join(MaterialsModel)
            .join(ProductoVariante)
            .join(CategoriesModel).where(ProductosModel.activo == 1)            
            .all()
        )

        data = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria_id": p.categoria_id,
                "categoria": p.categoria_nombre,                
                "subcategoria": p.subcategoria_nombre,
                "material_id": p.material_id,
                "material": p.material_nombre,
                "medida": p.medida,
                "unidad": p.unidad,
                "precio_compra": p.precio_compra,
                "precio_venta": p.precio,
                "imagen": p.url,
            }
            for p in products
        ]

        return {"data": data}

    except Exception as e:
        return {"error": str(e)}

