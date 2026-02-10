from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi import status
from app.utils.token import decode_token
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.materials_model import MaterialsModel
from typing import Optional

router = APIRouter(prefix="/materials", tags=["materials"])





@router.get("/", summary="List materials")
def list_materials(
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
    
    token = authorization.split(" ")[1]

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




    materials = db.query(MaterialsModel).all()




    return {"data": materials}

