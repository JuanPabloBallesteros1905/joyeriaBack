





from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
                        
token_expire_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(token_expire_str) if token_expire_str else 30
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Valor por defecto si no es un número válido



def create_token(data: dict, expires_delta: timedelta):

    try:
        to_encode = data.copy()
        expite = datetime.now( timezone.utc ) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) )
        to_encode.update({"exp": expite})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        raise Exception("Error creating token " + str(e)) from e





def decode_token(token: str):

    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError("Invalid token") from e 


      


