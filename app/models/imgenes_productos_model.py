from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, Numeric, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


from app.database.database import Base

class ImagenProducto(Base):
    __tablename__ = "imagenes_producto"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    url = Column(String(255), nullable=False)

    producto = relationship("ProductosModel", back_populates="imagenes")
