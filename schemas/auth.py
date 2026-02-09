from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    activo: int

class UserCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "admin"

class UserOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: int

