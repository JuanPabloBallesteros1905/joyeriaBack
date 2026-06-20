from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.deps import get_current_user, security_scheme
from app.utils.token import revoke_token

router = APIRouter(prefix="/logout", tags=["logout"])


@router.post("/", summary="Logout user")
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: dict = Depends(get_current_user),
):
    exp = current_user.get("exp")
    if exp:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        revoke_token(credentials.credentials, expires_at)

    return {"message": "Sesion cerrada exitosamente"}
