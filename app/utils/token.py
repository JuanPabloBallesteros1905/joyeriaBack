from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime, timedelta, timezone
import os
import time
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

token_expire_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(token_expire_str) if token_expire_str else 30
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

TOKEN_BLACKLIST: dict[str, float] = {}


def _clean_expired_blacklist():
    now = time.time()
    expired = [t for t, exp in TOKEN_BLACKLIST.items() if exp < now]
    for t in expired:
        del TOKEN_BLACKLIST[t]


def revoke_token(token: str, expires_at: datetime):
    _clean_expired_blacklist()
    TOKEN_BLACKLIST[token] = expires_at.timestamp()


def is_token_revoked(token: str) -> bool:
    _clean_expired_blacklist()
    return token in TOKEN_BLACKLIST


def create_token(data: dict, expires_delta: timedelta):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise Exception("Error creating token " + str(e)) from e


def decode_token(token: str):
    if is_token_revoked(token):
        raise JWTError("Token has been revoked")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError("Invalid token") from e
