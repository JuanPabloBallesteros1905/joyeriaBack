from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.productos_model import ProductosModel
from app.models.imgenes_productos_model import ImagenProducto

router = APIRouter(prefix="/productos", tags=["products"])


@router.get("/", summary="List products with image")
def list_products(db: Session = Depends(get_db)):
    try:
        products = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                ProductosModel.descripcion,
                ProductosModel.precio,
                ImagenProducto.url
            )
            .join(ImagenProducto, ProductosModel.id == ImagenProducto.producto_id)
            .all()
        )

        data = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": float(p.precio) if p.precio is not None else None,
                "imagen": p.url
            }
            for p in products
        ]

        return {"data": data}

    except Exception as e:
        return {"error": str(e)}

