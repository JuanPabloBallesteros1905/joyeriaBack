from fastapi import FastAPI, Depends, Request
from sqlalchemy import DateTime
from fastapi import HTTPException
from starlette import status
import bcrypt
from app.database.database import get_db
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.models.materials_model import MaterialsModel
from app.models.categorias_model import CategoriesModel
from app.models.productos_model import ProductosModel
from app.models.imgenes_productos_model import ImagenProducto
from pydantic import BaseModel
from fastapi import FastAPI
from app.models.usuarios_model import UsuariosModel


app = FastAPI()




 

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




 

@app.get("/")
def root():
    return {"status": "API Joyeria funcionando"}


@app.get("/materials")
def get_categories(db: Session = Depends(get_db)):

    materials = db.query(MaterialsModel).all()
    return {"data": materials}
 

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):

    categories = db.query(CategoriesModel).where(CategoriesModel.activa == 1).all()

    return {"data": categories}










@app.get("/productos")
def getAllProducts(db: Session = Depends(get_db)):
    try:
        products = (
            db.query(
                ProductosModel.id,
                ProductosModel.nombre,
                ProductosModel.descripcion,
                ProductosModel.precio,
                ImagenProducto.url
            )
            .join(ImagenProducto, ProductosModel.id == ImagenProducto.producto_id)
            .all()
        )

        data = [
            {  
                "id": p.id, 
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": float(p.precio),
                "imagen": p.url
            }
            for p in products
        ]

        return {"data": data}

    except Exception as e:
        print(f"Error retrieving products: {e}")
        return {"error": str(e)}







 
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    activo: int

    


    


@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user_db = db.query(UsuariosModel).filter(UsuariosModel.email == credentials.email).first()

    

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )

    if not bcrypt.checkpw(
        credentials.password.encode("utf-8"), 
        user_db.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    return user_db










class UserData(BaseModel):
    nombre: str
    email: str
    password_hash: str
    rol : str





@app.post("/singup/", response_model=UserData)
async def singup(db : Session = Depends(get_db), user: UserData = None):
 
    datos = user.dict()

    # aqui haré el encriptado de la contraseña


    
    

    salt = bcrypt.gensalt()

    pass_encrypted = bcrypt.hashpw(datos["password_hash"].encode("utf-8"), salt)

    datos["password_hash"] = pass_encrypted.decode("utf-8")








    

    new_user2 = UsuariosModel(**datos)



 


    

    
    
    db.add(new_user2)
    db.commit()
    db.refresh(new_user2)

    return new_user2
    