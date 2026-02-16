
from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.categories import Categorie_item

from app.deps import get_db
from app.models.categorias_model import CategoriesModel
from typing import Optional

from app.utils.token import decode_token
from fastapi import status


router = APIRouter(prefix="/categories", tags=["categories"])


#revisar como funcionan los router porque no deberian comunicarse con la base de datos 







#Update
@router.post("/update/{id}", summary="Update category")
def update_category(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    id: int = None,
    categorie: Categorie_item = None):




    
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







    datos = categorie.dict()


    db.query(CategoriesModel).filter(CategoriesModel.id == id).update(datos)
    db.commit()

    return {
        "data": "Categoría actualizada exitosamente"
    }

    
#Create
@router.post("/create", summary="Create category")
def create_category(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    categorie: Categorie_item = None

    ):


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




    datos = categorie.dict()

    new_categorie = CategoriesModel(**datos)
    






    db.add(new_categorie)
    db.commit()
    db.refresh(new_categorie)




    return {
        "data": "Categoría creada exitosamente"
    }


#Delate
@router.post("/delete/{id}", summary="Delete category")
def remove_category(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
   
    id: int = None
    ):


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

     

    item = db.query(CategoriesModel).filter(CategoriesModel.id == id).first();
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    db.delete(item)
    db.commit()

    return {
        "data": "Categoría eliminada exitosamente"
    }

#Get
@router.get("/", summary="List active categories")
def list_categories(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)):

   
    

    
    categories = db.query(CategoriesModel).where(
        CategoriesModel.activa == 1
    ).all()

    return {"data": categories}








