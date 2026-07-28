import resend
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin
from ..config import RESEND_API_KEY, RESEND_AUDIENCE_ID
from ..database import get_db

router = APIRouter(prefix="/api/subscribers", tags=["subscribers"])


@router.post("", response_model=schemas.SubscriberOut, status_code=status.HTTP_201_CREATED)
def subscribe(payload: schemas.SubscriberCreate, db: Session = Depends(get_db)):
    """Публічний ендпоінт для форми підписки. Зберігає email у БД і, якщо
    Resend налаштований (є ключ і Audience ID), одразу додає контакт туди —
    щоб замовниця могла розсилати новини через Resend Broadcasts/нашу кнопку
    в адмінці. Якщо синхронізація з Resend не вдалась — підписку це все одно
    не ламає, просто тихо логуємо помилку."""
    existing = db.query(models.Subscriber).filter(models.Subscriber.email == payload.email).first()
    if existing:
        # Не показуємо помилку користувачу за повторну підписку — просто повертаємо існуючий запис.
        return existing

    subscriber = models.Subscriber(email=payload.email)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    if RESEND_API_KEY and RESEND_AUDIENCE_ID:
        try:
            resend.api_key = RESEND_API_KEY
            resend.Contacts.create(
                {
                    "audience_id": RESEND_AUDIENCE_ID,
                    "email": subscriber.email,
                    "unsubscribed": False,
                }
            )
        except Exception as e:
            print(f"[resend] не вдалось додати {subscriber.email} в Audience: {e}")

    return subscriber


@router.get("", response_model=list[schemas.SubscriberOut])
def list_subscribers(
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """Захищений ендпоінт — тільки для замовниці, щоб пізніше експортувати базу."""
    return db.query(models.Subscriber).order_by(models.Subscriber.created_at.desc()).all()
