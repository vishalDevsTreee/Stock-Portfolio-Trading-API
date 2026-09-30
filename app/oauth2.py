from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')
#secret key
#algorithm
#expiration time


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode =data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt= jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token_access(token: str, credentials_exception):
    try:
        payload= jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
                      raise credentials_exception
        token_data=schemas.TokenData(id=id)
    except JWTError:
           raise credentials_exception

    return token_data

def get_current_user(token: str= Depends(oauth_scheme), 
                     db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_token_access(token, credentials_exception)
    user =db.query(models.User).filter(models.User.id == token.id).first()

    return user

    