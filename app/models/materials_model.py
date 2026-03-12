from sqlalchemy import Boolean, Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship, declarative_base
 


class MaterialsModel(Base):
    __tablename__ = "materiales"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    activo = Column(Boolean, default=True)
    productos = relationship("ProductosModel", back_populates="material")
