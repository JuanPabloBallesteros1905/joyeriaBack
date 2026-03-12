

import fastapi




router = fastapi.APIRouter(prefix="/logout", tags=["logout"])




router.post("/", summary="Logout user")
def logout_user():

    
    # Aquí podrías implementar la lógica para invalidar el token del usuario
    # Por ejemplo, podrías agregar el token a una lista de tokens revocados en tu base de datos
    return {"message": "Usuario ha sido desconectado exitosamente"}


