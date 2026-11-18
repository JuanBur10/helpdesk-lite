# Seguridad: hash de contraseñas, token JWT y usuario actual
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
import models

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
TOKEN_MINUTOS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)


# Aquí se crea el token con el id del usuario y la hora en que vence
def create_token(user_id):
    expira = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTOS)
    datos = {"sub": str(user_id), "exp": expira}
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


# Dependencia que protege los endpoints: lee el token y devuelve el usuario
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(datos["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user
