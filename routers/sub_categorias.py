
from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.sub_categorias_model import Subcategoria
from app.models.categorias_model import CategoriesModel
from app.deps import get_db
from typing import Optional
from fastapi import status
from app.utils.token import decode_token
from app.schemas.subcategoria import SubCategoria_item 





router = APIRouter(prefix="/subcategorias", tags=["subcategorias"])



@router.post("/delete/{id}", summary="Delete subcategoria")
def remove_subcategoria(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    id: int = None):



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






    item = db.query(Subcategoria).filter(Subcategoria.id == id).first();
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


@router.post("/create", summary="Create subcategoria")
def create_subcategoria(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    subcategoria: SubCategoria_item = None):




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



    datos = subcategoria.dict()

    new_subcategoria = Subcategoria(**datos)


    


    db.add(new_subcategoria)
    db.commit()
    db.refresh(new_subcategoria)

    return {
        "data": "Categoría creada exitosamente"
    }

@router.post("/update/{id}", summary="Update subcategoria")

def update_subcategoria(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    id: int = None,
    subcategoria: SubCategoria_item = None):



    
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






    datos = subcategoria.dict()


    db.query(Subcategoria).filter(Subcategoria.id == id).update(datos)
    db.commit()

    return {
        "data": "Categoría actualizada exitosamente"
    }


@router.get("/", summary="List subcategorias")
def list_subcategories(db: Session = Depends(get_db),authorization: Optional[str] = Header(None)):



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
                detail="Token inválido o expirado"
            )

        print("Decoded token payload:", payload)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error validando el token"
        )



    


    subCategorias = (
        db.query(
            Subcategoria.id,
            Subcategoria.nombre,
            Subcategoria.descripcion,
            Subcategoria.categoria_id,
            Subcategoria.activa,
            CategoriesModel.nombre.label("categoria_nombre") 
            
            
        ).join(CategoriesModel).all()
    )


    data = [
        {
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "categoria_id": p.categoria_id,
            "activa": p.activa, 
            "categoria_label": p.categoria_nombre 



            
            

            

            
        }

        for p in subCategorias
        
    ]






    


    



    return {"data": data}
   


    

