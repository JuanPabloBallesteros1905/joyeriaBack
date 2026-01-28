from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, Numeric, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


from app.database.database import Base


# class categoriesModel (Base):
#     __tablename__ = "categorias"

#     id = (Column(Integer, primary_key=True, index=True))
#     nombre = Column(String, unique=True, index=True)
#     descripcion = Column(String, index=True)
#     activa = Column(Boolean, index=True)



class CategoriesModel(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    activa = Column(Boolean, default=True)

    subcategorias = relationship("Subcategoria", back_populates="categoria")
    productos = relationship("ProductosModel", back_populates="categoria")
