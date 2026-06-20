from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routers import materials as materials_router
from app.routers import categories as categories_router
from app.routers import products as products_router
from app.routers import auth as auth_router
from app.routers import sub_categorias as sub_categorias_router
from app.routers import logout as logout_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Joyeria API (refactored)")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:4000",
    "http://localhost:4000",
    "https://admin.joyeriaitaliana.com",
    "https://joyeriaitaliana.com",
    "https://www.joyeriaitaliana.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def root(request: Request):
    return {"status": "API Joyeria funcionando (refactored)"}


app.include_router(materials_router.router)
app.include_router(categories_router.router)
app.include_router(products_router.router)
app.include_router(auth_router.router)
app.include_router(sub_categorias_router.router)
app.include_router(logout_router.router)
