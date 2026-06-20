from fastapi import APIRouter, Depends, HTTPException, Request
from starlette import status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.deps import get_db, get_current_user, require_role
from app.models.usuarios_model import UsuariosModel
from app.schemas.auth import LoginRequest, LoginResponse, UserCreate, UserOut
from app.utils.security import verify_password, get_password_hash
from app.utils.token import create_token

router = APIRouter(prefix="", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    user_db = db.query(UsuariosModel).filter(UsuariosModel.email == credentials.email).first()

    if user_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    if not verify_password(credentials.password, user_db.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    dataUser = LoginResponse(
        id=user_db.id,
        email=user_db.email,
        nombre=user_db.nombre,
        rol=user_db.rol,
        activo=user_db.activo,
        token=""
    )

    token = create_token(dataUser.dict(), expires_delta=None)
    dataUser.token = token

    return dataUser


@router.post("/singup/", response_model=UserOut)
@limiter.limit("5/minute")
def singup(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    existing = db.query(UsuariosModel).filter(UsuariosModel.email == user.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya esta registrado")

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
