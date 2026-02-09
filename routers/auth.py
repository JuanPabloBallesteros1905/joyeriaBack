from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.usuarios_model import UsuariosModel
from app.schemas.auth import LoginRequest, LoginResponse, UserCreate, UserOut
from app.utils.security import verify_password, get_password_hash

router = APIRouter(prefix="", tags=["auth"])





@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user_db = db.query(UsuariosModel).filter(UsuariosModel.email == credentials.email).first()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")

    if not verify_password(credentials.password, user_db.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    return LoginResponse(
        id=user_db.id,
        email=user_db.email,
        nombre=user_db.nombre,
        rol=user_db.rol,
        activo=user_db.activo
    )


@router.post("/singup/", response_model=UserOut)
def singup(user: UserCreate, db: Session = Depends(get_db)):
    datos = user.dict()
    datos["password_hash"] = get_password_hash(datos.pop("password"))

    new_user = UsuariosModel(**datos)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(
        id=new_user.id,
        nombre=new_user.nombre,
        email=new_user.email,
        rol=new_user.rol,
        activo=new_user.activo
    )

