from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.schemas.categories import Categorie_item
from app.deps import get_db, require_role
from app.models.categorias_model import CategoriesModel

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/update/{id}", summary="Update category")
def update_category(
    id: int,
    categorie: Categorie_item,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    db.query(CategoriesModel).filter(CategoriesModel.id == id).update(categorie.dict())
    db.commit()

    return {"data": "Categoria actualizada exitosamente"}


@router.post("/create", summary="Create category")
def create_category(
    categorie: Categorie_item,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    new_categorie = CategoriesModel(**categorie.dict())
    db.add(new_categorie)
    db.commit()
    db.refresh(new_categorie)

    return {"data": "Categoria creada exitosamente"}


@router.post("/delete/{id}", summary="Delete category")
def remove_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    item = db.query(CategoriesModel).filter(CategoriesModel.id == id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")

    db.delete(item)
    db.commit()

    return {"data": "Categoria eliminada exitosamente"}


@router.get("/", summary="List active categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(CategoriesModel).where(CategoriesModel.activa == 1).all()
    return {"data": categories}
