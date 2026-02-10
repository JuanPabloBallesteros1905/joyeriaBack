from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi import status
from jose import JWTError
from app.utils.token import decode_token
from typing import Optional
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.productos_model import ProductosModel
from app.models.imgenes_productos_model import ImagenProducto

router = APIRouter(prefix="/productos", tags=["products"])


@router.get("/", summary="List products with image")
def list_products(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)):


    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header requerido"
        )

    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Debe ser 'Bearer <token>'"
        )

    
    token = authorization.split(" ")[1]

    
    try:
        payload = decode_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error validando el token"
        )






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

