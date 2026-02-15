from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import materials as materials_router
from app.routers import categories as categories_router
from app.routers import products as products_router
from app.routers import auth as auth_router
from app.routers import sub_categorias as sub_categorias_router



app = FastAPI(title="Joyeria API (refactored)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "API Joyeria funcionando (refactored)"}


app.include_router(materials_router.router)
app.include_router(categories_router.router)
app.include_router(products_router.router)
app.include_router(auth_router.router)
app.include_router(sub_categorias_router.router)




