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


@router.get("", response_model=list[schemas.SubscriberWithStatus])
def list_subscribers(
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """Захищений ендпоінт — тільки для замовниці, щоб пізніше експортувати базу.

    Якщо Resend налаштований — додатково підтягує ЖИВИЙ статус відписки
    для кожного email напряму з Resend Audience (не з нашої БД — там цього
    поля просто немає, і це навмисно, див. коментар у schemas.py). Якщо
    Resend недоступний чи сталась помилка — просто показуємо список без
    статусу відписки (усі як unsubscribed=False), нічого не ламаємо."""
    subscribers = db.query(models.Subscriber).order_by(models.Subscriber.created_at.desc()).all()

    unsubscribed_emails = set()
    if RESEND_API_KEY and RESEND_AUDIENCE_ID:
        try:
            resend.api_key = RESEND_API_KEY
            cursor_after = None
            while True:
                params = {"limit": 100}
                if cursor_after:
                    params["after"] = cursor_after
                page = resend.Contacts.list(audience_id=RESEND_AUDIENCE_ID, params=params)
                data = page.get("data", []) if isinstance(page, dict) else getattr(page, "data", [])
                for contact in data:
                    email = contact.get("email") if isinstance(contact, dict) else getattr(contact, "email", None)
                    unsub = (
                        contact.get("unsubscribed")
                        if isinstance(contact, dict)
                        else getattr(contact, "unsubscribed", False)
                    )
                    if email and unsub:
                        unsubscribed_emails.add(email.lower())
                has_more = page.get("has_more") if isinstance(page, dict) else getattr(page, "has_more", False)
                if not has_more or not data:
                    break
                last = data[-1]
                cursor_after = last.get("id") if isinstance(last, dict) else getattr(last, "id", None)
                if not cursor_after:
                    break
        except Exception as e:
            print(f"[resend] не вдалось отримати живий статус контактів: {e}")

    return [
        schemas.SubscriberWithStatus(
            id=s.id,
            email=s.email,
            created_at=s.created_at,
            unsubscribed=s.email.lower() in unsubscribed_emails,
        )
        for s in subscribers
    ]
