





from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime, timedelta, timezone



SECRET_KEY = "your_secret"
ALGOTRITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60



def create_token(data: dict, expires_delta: timedelta):

    try:
        to_encode = data.copy()
        expite = datetime.now( timezone.utc ) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) )
        to_encode.update({"exp": expite})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGOTRITHM)

    except Exception as e:
        raise Exception("Error creating token") from e





def decode_token(token: str):

    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGOTRITHM])
        return payload
    except JWTError as e:
        raise JWTError("Invalid token") from e 


      


