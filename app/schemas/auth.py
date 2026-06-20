from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    activo: int
    token: str


class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    rol: str = Field(default="editor", pattern="^(admin|editor)$")


class UserOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: int
