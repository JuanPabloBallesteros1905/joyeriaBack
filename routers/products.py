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
from app.schemas.productos import Produto_item
 


router = APIRouter(prefix="/productos", tags=["products"])



    #{
    #    "nombre": "aasd",
     #   "imagen": "asda",
      #  "descripcion": "asdasd",
       # "categoria_id": 1,
        #"subcategoria_id": 1,
       # "material_id": 1,
       # "peso": "asdad",
       # "tipo_medida": "asda",
       # "dimensiones": "asda",
       # "precio_compra": "234234",
       # "precio_venta": "23424"
    #}
    
@router.post("/create", summary="Delete product")
async def create_joya(
 
    db: Session = Depends(get_db),
    file: UploadFile = File(...)):


    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_extension = Path(file.filename).suffix.lower()
        
    if file_extension not in allowed_extensions:
        raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {allowed_extensions}"
            )
            
    
       # Validar tamaño (ejemplo: máximo 5MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=400,
                detail="El archivo es demasiado grande. Máximo 5MB"
            )
        
        # Crear nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Devolver la URL del archivo
        file_url = f"/uploads/{safe_filename}"
        
        return JSONResponse({
            "filename": safe_filename,
            "url": file_url,
            "message": "Imagen subida exitosamente"
        })
        

     
 




    
    return {"data": "En construcción"}







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
                CategoriesModel.id.label("categoria_id"))
            .join(ImagenProducto)
            .join(MaterialsModel).
            join(ProductoVariante).
            join(CategoriesModel)
            
            .all()
        )

        data = [
            {
                

                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria_id": p.categoria_id,
                "categoria": p.categoria_nombre,                
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

