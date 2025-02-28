from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt as pyjwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

# 🔹 Configuração do hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔹 Configuração do JWT
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 🔐 Função que gera hash da senha
def hash_password(password: str):
    return pwd_context.hash(password)   

# 🔐 Função que verifica a senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  

# 🔑 Função que gera o token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🔒 Configuração do esquema OAuth2 para autenticação por token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 🔍 Função para validar usuário autenticado
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """ Decodifica o token JWT e retorna o usuário autenticado """
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user  # Retorna o usuário autenticado

    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    except pyjwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
