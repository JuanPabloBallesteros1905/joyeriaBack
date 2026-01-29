




import enum
from app.database.database import Base
from sqlalchemy import (Column,Integer, String)


class Roles(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"


class UsuariosModel(Base):
    __tablename__ = "usuarios"


    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False, default=Roles.ADMIN)
    activo = Column(Integer, default=True)  
    fecha_creacion = Column(String(50), nullable=False)