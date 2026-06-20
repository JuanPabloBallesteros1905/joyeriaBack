from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.models.sub_categorias_model import Subcategoria
from app.models.categorias_model import CategoriesModel
from app.deps import get_db, require_role
from app.schemas.subcategoria import SubCategoria_item

router = APIRouter(prefix="/subcategorias", tags=["subcategorias"])


@router.post("/delete/{id}", summary="Delete subcategoria")
def remove_subcategoria(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    item = db.query(Subcategoria).filter(Subcategoria.id == id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategoria no encontrada")

    db.delete(item)
    db.commit()

    return {"data": "Subcategoria eliminada exitosamente"}


@router.post("/create", summary="Create subcategoria")
def create_subcategoria(
    subcategoria: SubCategoria_item,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    new_subcategoria = Subcategoria(**subcategoria.dict())
    db.add(new_subcategoria)
    db.commit()
    db.refresh(new_subcategoria)

    return {"data": "Subcategoria creada exitosamente"}


@router.post("/update/{id}", summary="Update subcategoria")
def update_subcategoria(
    id: int,
    subcategoria: SubCategoria_item,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    db.query(Subcategoria).filter(Subcategoria.id == id).update(subcategoria.dict())
    db.commit()

    return {"data": "Subcategoria actualizada exitosamente"}


@router.get("/", summary="List subcategorias")
def list_subcategories(db: Session = Depends(get_db)):
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
            "categoria_label": p.categoria_nombre,
        }
        for p in subCategorias
    ]

    return {"data": data}
