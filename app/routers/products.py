import json
import os
import shutil
from fastapi import APIRouter,  File, Form, UploadFile, Depends, Header, HTTPException
from fastapi import status
from jose import JWTError
from app.utils.token import decode_token
from typing import List, Optional
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.deps import get_db
from app.models.productos_model import ProductosModel
from app.models.materials_model import MaterialsModel
from app.models.imgenes_productos_model import ImagenProducto
from app.models.productos_v2_model import ProductoVariante
from app.models.categorias_model import CategoriesModel
from app.models.sub_categorias_model import Subcategoria
from app.models.imgenes_productos_model import ImagenProducto
import uuid
router = APIRouter(prefix="/productos", tags=["products"])





@router.get("/category/{category_id}", summary="Get products by category")

def get_products_by_category(
    db: Session = Depends(get_db),
    category_id: int = None,
    
    
    
    ):
    try:


        product = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                CategoriesModel.nombre.label("categoria_nombre"),
                ImagenProducto.url,
                ProductoVariante.precio

            ).join(ProductoVariante, ProductoVariante.producto_id == ProductosModel.id) 
            
            .join(ImagenProducto, ImagenProducto.producto_id == ProductosModel.id)
            
            .join(CategoriesModel, CategoriesModel.id == ProductosModel.categoria_id)
            
            .where(ProductosModel.categoria_id == category_id).all()

        )

        data = []

        for p in product:
            data.append({
                "id": p.id,
                "name": p.nombre, 
                "category": p.categoria_nombre, 
                "image": p.url,
                "price": p.precio
                    
                })


        


        
        

        
        
        
 


        


        
        

        return {"data": data}

    except Exception as e:
        return {"error": str(e)}







@router.get("/{product_id}", summary="Get product by id")
def get_product_by_id(
    db: Session = Depends(get_db),
    product_id: int = None,
    authorization: Optional[str] = Header(None)
):
    try:
        # 1. Obtener los datos del producto (SIN el JOIN de imágenes)
        product = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                ProductosModel.descripcion,
                ProductosModel.peso,
                MaterialsModel.nombre.label("material_nombre"),
                MaterialsModel.id.label("material_id"),
                ProductoVariante.medida,
                ProductoVariante.unidad,
                ProductoVariante.precio,
                ProductoVariante.precio_compra,
                CategoriesModel.nombre.label("categoria_nombre"),
                CategoriesModel.id.label("categoria_id"),
                Subcategoria.nombre.label("subcategoria_nombre"),
                Subcategoria.id.label("subcategoria_id"),
            )
            .join(MaterialsModel, MaterialsModel.id == ProductosModel.material_id)
            .join(ProductoVariante, ProductoVariante.producto_id == ProductosModel.id)
            .join(Subcategoria, Subcategoria.id == ProductosModel.subcategoria_id)
            .join(CategoriesModel, CategoriesModel.id == ProductosModel.categoria_id)
            .where(ProductosModel.id == product_id)
            .first()  # Usamos first() porque esperamos un solo producto
        )

        if not product:
            return {"error": "Producto no encontrado"}

        # 2. Obtener TODAS las imágenes del producto
        imagenes = (
            db.query(ImagenProducto.url)
            .where(ImagenProducto.producto_id == product_id)
            .all()
        )

        # Convertir a lista de URLs
        imagenes_list = [img.url for img in imagenes]

        # 3. Construir la respuesta
        data = {
            "id": product.id,
            "nombre": product.nombre,
            "descripcion": product.descripcion,
            "categoria_id": product.categoria_id,
            "categoria": product.categoria_nombre,
            "subcategoria_id": product.subcategoria_id,
            "subcategoria": product.subcategoria_nombre,
            "material_id": product.material_id,
            "material": product.material_nombre,
            "medida": product.medida,
            "unidad": product.unidad,
            "peso": product.peso,
            "precio_compra": product.precio_compra,
            "precio_venta": product.precio,
            "imagenes": imagenes_list,  # Array con todas las URLs
            "imagen_principal": imagenes_list[0] if imagenes_list else None  # Primera imagen como principal
        }

        return {"data": data}

    except Exception as e:
        return {"error": str(e)}

    
@router.post("/delete/{product_id}", summary="Delete product")
def delete_product(
    db: Session = Depends(get_db),
    product_id: int = None,
    authorization: Optional[str] = Header(None)):

    product = db.query(ProductosModel).filter(ProductosModel.id == product_id).first()
    detalle = db.query(ProductoVariante).filter(ProductoVariante.producto_id == product_id).first()
    imagen = db.query(ImagenProducto).filter(ImagenProducto.producto_id == product_id).first()


    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if not detalle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detalle del producto no encontrado")
    if not imagen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen del producto no encontrada")

    db.delete(product)
    db.delete(detalle)
    db.delete(imagen)
    db.commit()

 


 


    return {"message": "Producto eliminado exitosamente"} 
    
UPLOAD_FOLDER = "uploads"


@router.post("/create", summary="Create product")
async def create_joya(
    db: Session = Depends(get_db),
    producto: str = Form(...),
    imagenes: List[UploadFile] = File(...)
):
    try:
        datos = json.loads(producto)

        producto_data = datos["producto"]
        detalle_data = datos["detalle"]

        # Crear producto (UNA SOLA VEZ)
        new_product = ProductosModel(**producto_data)
        db.add(new_product)
        db.flush()

        # Crear detalle (UNA SOLA VEZ)
        new_detalle = ProductoVariante(
            producto_id=new_product.id,
            medida=detalle_data["medida"],
            unidad=detalle_data["unidad"],
            precio=detalle_data["precio"],
            precio_compra=detalle_data["precio_compra"],
            activo=detalle_data["activo"]
        )
        db.add(new_detalle)

        # Crear carpeta si no existe
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Procesar múltiples imágenes con OPTIMIZACIÓN
        for imagen in imagenes:
            # 1. Generar nombre único con extensión .webp
            filename = f"{uuid.uuid4()}.webp"
            file_location = f"{UPLOAD_FOLDER}/{filename}"

            # 2. Abrir la imagen desde el stream de UploadFile
            img = Image.open(imagen.file)

            # 3. Asegurar modo RGB (WebP no maneja transparencia igual que PNG en todos los casos)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 4. Redimensionar si es muy grande (máximo 1200px de ancho para optimizar carga web)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(float(img.height) * float(ratio))
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # 5. Guardar optimizada (calidad 80 es ideal para equilibrio peso/calidad)
            img.save(file_location, "WEBP", quality=80, optimize=True)

            # Guardar imagen en DB (ASOCIADA AL MISMO PRODUCTO)
            new_image = ImagenProducto(
                producto_id=new_product.id,  # Mismo producto_id para todas
                url=file_location
            )
            db.add(new_image)

        db.commit()  # UN SOLO COMMIT al final

        return {"message": "Producto creado exitosamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
  
@router.post("/update/{product_id}", summary="Update| product")
def update_product(
    db: Session = Depends(get_db),):


    

    

 
    return {"message": "Producto actualizado exitosamente"} 
    




@router.get("/", summary="List products with images")
def list_products(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    try:
        # 1. Obtener productos (SIN el JOIN de imágenes)
        products = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                ProductosModel.descripcion,
                ProductosModel.peso,
                MaterialsModel.nombre.label("material_nombre"),
                MaterialsModel.id.label("material_id"),
                ProductoVariante.medida,
                ProductoVariante.unidad,
                ProductoVariante.precio,
                 
                CategoriesModel.nombre.label("categoria_nombre"),
                CategoriesModel.id.label("categoria_id"),
                Subcategoria.nombre.label("subcategoria_nombre"),
                Subcategoria.id.label("subcategoria_id"),
            )
            .join(MaterialsModel, MaterialsModel.id == ProductosModel.material_id)
            .join(ProductoVariante, ProductoVariante.producto_id == ProductosModel.id)
            .join(Subcategoria, Subcategoria.id == ProductosModel.subcategoria_id)
            .join(CategoriesModel, CategoriesModel.id == ProductosModel.categoria_id)
            .where(ProductosModel.activo == 1)
            .all()
        )

        # 2. Preparar los datos, obteniendo las imágenes por separado
        data = []
        for p in products:
            # Obtener las URLs de las imágenes para este producto
            imagenes = (
                db.query(ImagenProducto.url)
                .where(ImagenProducto.producto_id == p.id)
                .all()
            )
            
            # Convertir el resultado en una lista simple de strings
            imagenes_list = [img.url for img in imagenes]
            
            # Construir el diccionario del producto
            data.append({
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria_id": p.categoria_id,
                "categoria": p.categoria_nombre,                
                "subcategoria_id": p.subcategoria_id,
                "subcategoria": p.subcategoria_nombre,
                "material_id": p.material_id,
                "material": p.material_nombre,
                "medida": p.medida,
                "unidad": p.unidad,
                "peso": p.peso,
                
                "precio_venta": p.precio,
                # Devuelves TODAS las imágenes en un array
                "imagenes": imagenes_list,
                # (Opcional) La primera imagen como principal
                "imagen_principal": imagenes_list[0] if imagenes_list else None
            })

        return {"data": data}

    except Exception as e:
        return {"error": str(e)}