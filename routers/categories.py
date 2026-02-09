from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.categorias_model import CategoriesModel

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", summary="List active categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(CategoriesModel).where(CategoriesModel.activa == 1).all()
    return {"data": categories}

