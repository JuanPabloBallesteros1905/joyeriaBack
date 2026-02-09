from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.materials_model import MaterialsModel

router = APIRouter(prefix="/materials", tags=["materials"])





@router.get("/", summary="List materials")
def list_materials(db: Session = Depends(get_db)):
    materials = db.query(MaterialsModel).all()
    return {"data": materials}

