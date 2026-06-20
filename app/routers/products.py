import json
import os
import uuid
from typing import List

from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException
from fastapi import status
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.deps import get_db, require_role
from app.models.productos_model import ProductosModel
from app.models.materials_model import MaterialsModel
from app.models.imgenes_productos_model import ImagenProducto
from app.models.productos_v2_model import ProductoVariante
from app.models.categorias_model import CategoriesModel
from app.models.sub_categorias_model import Subcategoria

router = APIRouter(prefix="/productos", tags=["products"])

UPLOAD_FOLDER = "uploads"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_image(upload: UploadFile):
    if upload.content_type and upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {upload.content_type}. Usa JPEG, PNG, WebP o GIF.",
        )


@router.get("/category/{category_id}", summary="Get products by category")
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    try:
        product = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                CategoriesModel.nombre.label("categoria_nombre"),
                func.min(ImagenProducto.url).label("image"),
                func.min(ProductoVariante.precio).label("price"),
            )
            .join(ProductoVariante, ProductoVariante.producto_id == ProductosModel.id)
            .join(ImagenProducto, ImagenProducto.producto_id == ProductosModel.id)
            .join(CategoriesModel, CategoriesModel.id == ProductosModel.categoria_id)
            .where(ProductosModel.categoria_id == category_id)
            .group_by(ProductosModel.id, ProductosModel.nombre, CategoriesModel.nombre)
            .all()
        )

        seen = set()
        data = []
        for p in product:
            if p.id in seen:
                continue
            seen.add(p.id)
            data.append({
                "id": p.id,
                "name": p.nombre,
                "category": p.categoria_nombre,
                "image": p.image,
                "price": p.price,
            })

        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@router.get("/{product_id}", summary="Get product by id")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    try:
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
            .first()
        )

        if not product:
            return {"error": "Producto no encontrado"}

        imagenes = (
            db.query(ImagenProducto.url)
            .where(ImagenProducto.producto_id == product_id)
            .all()
        )
        imagenes_list = [img.url for img in imagenes]

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
            "imagenes": imagenes_list,
            "imagen_principal": imagenes_list[0] if imagenes_list else None,
        }

        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@router.post("/delete/{product_id}", summary="Delete product")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    product = db.query(ProductosModel).filter(ProductosModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    db.delete(product)
    db.commit()

    return {"message": "Producto eliminado exitosamente"}


@router.post("/create", summary="Create product")
async def create_joya(
    producto: str = Form(...),
    imagenes: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    try:
        datos = json.loads(producto)

        producto_data = datos["producto"]
        detalle_data = datos["detalle"]

        new_product = ProductosModel(**producto_data)
        db.add(new_product)
        db.flush()

        new_detalle = ProductoVariante(
            producto_id=new_product.id,
            medida=detalle_data["medida"],
            unidad=detalle_data["unidad"],
            precio=detalle_data["precio"],
            precio_compra=detalle_data["precio_compra"],
            activo=detalle_data["activo"],
        )
        db.add(new_detalle)

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        for imagen in imagenes:
            _validate_image(imagen)

            filename = f"{uuid.uuid4()}.webp"
            file_location = f"{UPLOAD_FOLDER}/{filename}"

            img = Image.open(imagen.file)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            max_width = 1200
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(float(img.height) * float(ratio))
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            img.save(file_location, "WEBP", quality=80, optimize=True)

            new_image = ImagenProducto(producto_id=new_product.id, url=file_location)
            db.add(new_image)

        db.commit()

        return {"message": "Producto creado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update/{product_id}", summary="Update product")
def update_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    return {"message": "Producto actualizado exitosamente"}


@router.get("/", summary="List products with images")
def list_products(db: Session = Depends(get_db)):
    try:
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

        if not products:
            return {"data": []}

        product_ids = [p.id for p in products]
        all_images = (
            db.query(ImagenProducto.producto_id, ImagenProducto.url)
            .where(ImagenProducto.producto_id.in_(product_ids))
            .all()
        )

        images_map: dict[int, list[str]] = {}
        for img in all_images:
            if img.producto_id not in images_map:
                images_map[img.producto_id] = []
            images_map[img.producto_id].append(img.url)

        data = []
        for p in products:
            imagenes_list = images_map.get(p.id, [])
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
                "imagenes": imagenes_list,
                "imagen_principal": imagenes_list[0] if imagenes_list else None,
            })

        return {"data": data}
    except Exception as e:
        return {"error": str(e)}
