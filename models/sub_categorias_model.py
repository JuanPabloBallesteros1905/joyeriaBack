



from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, Numeric, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from app.database.database import Base

class Subcategoria(Base):
    __tablename__ = "subcategorias"

    id = Column(Integer, primary_key=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    activa = Column(Boolean, default=True)

    categoria = relationship("CategoriesModel", back_populates="subcategorias")
    productos = relationship("ProductosModel", back_populates="subcategoria")
