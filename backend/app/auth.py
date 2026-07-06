"""
Авторизація для єдиного адмін-акаунта (сама замовниця).

Навмисно просто: без ролей, без refresh-токенів, без реєстрації —
відвідувачам сайту вхід не потрібен (підтверджено замовницею), тож тут
лише перевірка email+пароль і видача JWT для доступу до /api/admin/*.
"""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models
from .config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.AdminUser:
    """Dependency: підключається до захищених роутів як Depends(get_current_admin)."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалідний або прострочений токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise unauthorized
    except JWTError:
        raise unauthorized

    admin = db.query(models.AdminUser).filter(models.AdminUser.email == email).first()
    if admin is None:
        raise unauthorized
    return admin
