from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, Numeric, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


from app.database.database import Base






# class ProductosModel(Base):
#     __tablename__ = "productos"

#     id = Column(Integer, primary_key=True, index=True)
#     nombre = Column(String, unique=True, index=True)
#     descripcion = Column(String, index=True)
#     categoria_id = Column(Integer, index=True)
    

class ProductosModel(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(255))

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    subcategoria_id = Column(Integer, ForeignKey("subcategorias.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiales.id"), nullable=False)

    peso = Column(Float)
    precio = Column(Numeric(10, 2))
    activo = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, server_default=func.now())

    categoria = relationship("CategoriesModel", back_populates="productos")
    subcategoria = relationship("Subcategoria", back_populates="productos")
    material = relationship("MaterialsModel", back_populates="productos")

    variantes = relationship(
        "ProductoVariante",
        back_populates="producto",
        cascade="all, delete-orphan"
    )

    imagenes = relationship(
        "ImagenProducto",
        back_populates="producto",
        cascade="all, delete-orphan"
    )


    

