from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin
from ..database import get_db

router = APIRouter(prefix="/api/subscribers", tags=["subscribers"])


@router.post("", response_model=schemas.SubscriberOut, status_code=status.HTTP_201_CREATED)
def subscribe(payload: schemas.SubscriberCreate, db: Session = Depends(get_db)):
    """Публічний ендпоінт для форми підписки. Поки просто зберігає email у БД —
    без інтеграції з сервісом розсилок (додасться пізніше, коли буде потрібно)."""
    existing = db.query(models.Subscriber).filter(models.Subscriber.email == payload.email).first()
    if existing:
        # Не показуємо помилку користувачу за повторну підписку — просто повертаємо існуючий запис.
        return existing

    subscriber = models.Subscriber(email=payload.email)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


@router.get("", response_model=list[schemas.SubscriberOut])
def list_subscribers(
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """Захищений ендпоінт — тільки для замовниці, щоб пізніше експортувати базу."""
    return db.query(models.Subscriber).order_by(models.Subscriber.created_at.desc()).all()
