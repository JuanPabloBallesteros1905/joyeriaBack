from fastapi import FastAPI, Depends, Request




# from database.database import get_db
from app.database.database import get_db
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.models.materials_model import MaterialsModel
from app.models.categorias_model import CategoriesModel
from app.models.productos_model import ProductosModel
from app.models.imgenes_productos_model import ImagenProducto



from fastapi import FastAPI


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





