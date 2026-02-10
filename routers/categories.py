
from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.categorias_model import CategoriesModel
from typing import Optional

from app.utils.token import decode_token
from fastapi import status
router = APIRouter(prefix="/categories", tags=["categories"])






@router.get("/", summary="List active categories")
def list_categories(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):

    # ✅ Validar que el header exista
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header requerido"
        )

    # ✅ Validar formato Bearer
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Debe ser 'Bearer <token>'"
        )

    # ✅ Extraer token
    token = authorization.split(" ")[1]

    # ✅ Validar token
    try:
        payload = decode_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )

        print("Decoded token payload:", payload)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error validando el token"
        )

    # ✅ Obtener datos solo si el token es válido
    categories = db.query(CategoriesModel).where(
        CategoriesModel.activa == 1
    ).all()

    return {"data": categories}
