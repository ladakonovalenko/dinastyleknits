from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import create_access_token, get_current_admin, verify_password
from ..database import get_db
from ..limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.email == payload.email).first()
    if admin is None or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль",
        )
    token = create_access_token(admin.email)
    return schemas.TokenResponse(access_token=token)


@router.get("/me")
def me(admin: models.AdminUser = Depends(get_current_admin)):
    """Перевірка валідності токена — фронтенд адмінки викликає це при завантаженні."""
    return {"email": admin.email}
