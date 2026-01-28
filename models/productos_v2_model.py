

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, Numeric, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from app.database.database import Base







class ProductoVariante(Base):
    __tablename__ = "productos_v2"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    medida = Column(Float, nullable=False)
    unidad = Column(String(20), nullable=False)
    precio = Column(Numeric(10, 2))
    precio_compra = Column(Numeric(10, 2))
    activo = Column(Boolean, default=True)

    producto = relationship("ProductosModel", back_populates="variantes")
