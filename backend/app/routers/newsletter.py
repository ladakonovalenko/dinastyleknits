"""
Розсилка новин одним натисканням з адмінки — щоб замовниці не треба було
самій заходити в Resend Dashboard і розбиратись з незнайомим інтерфейсом.

Технічно це обгортка над Resend Broadcast API: створюємо Broadcast на той
самий Audience, куди й так автоматично потрапляють підписники з форми на
сайті, і одразу відправляємо.

⚠️ Навмисно два ОКРЕМІ виклики (create, потім send), а не один запит з
"send": True — той короткий шлях підтримується лише в resend-python
2.21.0+, а версія, з якою ми зіткнулись у продакшені, її мовчки
ігнорувала (розсилка створювалась, але лишалась чернеткою, і жодної
помилки при цьому не було). Двокроковий варіант — це найстаріший,
базовий спосіб роботи з Broadcasts API, який підтримується практично
будь-якою версією бібліотеки.
"""
import os

import resend
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_admin
from ..config import FROM_EMAIL, RESEND_API_KEY, RESEND_AUDIENCE_ID
from ..database import get_db

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


class NewsletterRequest(BaseModel):
    subject: str
    body: str  # звичайний текст від адмінки; порожній рядок між абзацами розділяє їх


def _build_html(body: str) -> str:
    """Перетворює звичайний текст із textarea в акуратний HTML-лист із базовим
    оформленням у стилі сайту (акцентний колір, назва бренду) — щоб не
    вимагати від замовниці розбиратись з HTML/дизайном листа самостійно."""
    paragraphs = "".join(
        f'<p style="margin: 0 0 16px; line-height: 1.6;">{p.strip()}</p>'
        for p in body.split("\n\n")
        if p.strip()
    )
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto; color: #141414;">
      <div style="background: #0297B1; padding: 24px; text-align: center;">
        <h1 style="color: #ffffff; margin: 0; font-size: 20px;">DinaStyleKnits</h1>
      </div>
      <div style="padding: 24px 24px 8px;">
        {paragraphs}
      </div>
      <div style="padding: 16px 24px; color: #8A8A8A; font-size: 12px; text-align: center;">
        <a href="{{{{{{RESEND_UNSUBSCRIBE_URL}}}}}}" style="color: #8A8A8A;">Unsubscribe</a>
      </div>
    </div>
    """


@router.get("/status")
def newsletter_status(_admin: models.AdminUser = Depends(get_current_admin)):
    """Діагностика: показує, чи бачить ЦЕЙ конкретний запущений процес
    змінні середовища Resend — без розкриття самих значень. Корисно саме
    для cPanel/Passenger, де змінні підхоплюються лише при (пере)старті
    застосунку: якщо їх додали, поки процес уже працював, тут буде видно
    false, доки застосунок не перезапустять.

    matching_env_var_names — назви (НЕ значення) усіх змінних середовища,
    де в назві є підрядок "resend" (без урахування регістру). Якщо тут
    порожній список — змінна з очікуваною назвою взагалі не доходить до
    процесу (типова причина: додана не в той застосунок на хостингу, або
    з друкарською помилкою в назві). Якщо список НЕ порожній, але
    resend_api_key_set/resend_audience_id_set усе одно false — значить,
    назва трохи відрізняється від очікуваної (RESEND_API_KEY / RESEND_AUDIENCE_ID
    рівно так, великими літерами, з підкресленням)."""
    matching_keys = sorted(key for key in os.environ if "resend" in key.lower())
    return {
        "resend_api_key_set": bool(RESEND_API_KEY),
        "resend_audience_id_set": bool(RESEND_AUDIENCE_ID),
        "from_email": FROM_EMAIL,
        "matching_env_var_names": matching_keys,
    }


@router.post("/sync-subscribers")
def sync_subscribers_to_resend(
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """Синхронізація в ОБИДВА боки з Resend Audience:

    1. Кожен підписник з нашої БД, якого ще немає в Resend — додається туди
       (потрібно, бо синхронізація при самій підписці якийсь час мовчки не
       спрацьовувала, поки не замінили ключ Resend на Full access).
    2. Статус відписки тягнеться НАЗАД з Resend у нашу БД — бо коли людина
       натискає "Unsubscribe" в самому листі, це оновлює лише запис у
       Resend; наша власна БД про цю подію ніяк не дізнається сама (немає
       налаштованого вебхука), тому без цього кроку лічильник підписників
       в адмінці ніколи б не зменшувався і розсилка й далі націлювалась
       би на тих самих людей (хоч Resend і сам не надішле відписаним —
       але наші власні дані про це нічого не знали б)."""
    if not RESEND_API_KEY or not RESEND_AUDIENCE_ID:
        raise HTTPException(
            status_code=400,
            detail="Resend ще не налаштований (немає RESEND_API_KEY або RESEND_AUDIENCE_ID)",
        )

    resend.api_key = RESEND_API_KEY
    subscribers = db.query(models.Subscriber).all()

    # --- Крок 1: довантажити в Resend тих, кого там ще немає ---
    pushed = 0
    push_failed = []
    for subscriber in subscribers:
        try:
            resend.Contacts.create(
                {
                    "audience_id": RESEND_AUDIENCE_ID,
                    "email": subscriber.email,
                    "unsubscribed": subscriber.unsubscribed,
                }
            )
            pushed += 1
        except Exception as e:
            push_failed.append({"email": subscriber.email, "error": str(e)})

    # --- Крок 2: забрати з Resend актуальний статус відписки й оновити нашу БД ---
    resend_contacts_by_email = {}
    cursor_after = None
    try:
        while True:
            params = {"limit": 100}
            if cursor_after:
                params["after"] = cursor_after
            page = resend.Contacts.list(audience_id=RESEND_AUDIENCE_ID, params=params)
            data = page.get("data", []) if isinstance(page, dict) else getattr(page, "data", [])
            for contact in data:
                email = contact.get("email") if isinstance(contact, dict) else getattr(contact, "email", None)
                unsub = (
                    contact.get("unsubscribed") if isinstance(contact, dict) else getattr(contact, "unsubscribed", False)
                )
                if email:
                    resend_contacts_by_email[email.lower()] = bool(unsub)
            has_more = page.get("has_more") if isinstance(page, dict) else getattr(page, "has_more", False)
            if not has_more or not data:
                break
            last = data[-1]
            cursor_after = last.get("id") if isinstance(last, dict) else getattr(last, "id", None)
            if not cursor_after:
                break
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Не вдалось отримати список контактів з Resend: {e}")

    updated_unsubscribed = 0
    for subscriber in subscribers:
        resend_status = resend_contacts_by_email.get(subscriber.email.lower())
        if resend_status is not None and resend_status != subscriber.unsubscribed:
            subscriber.unsubscribed = resend_status
            updated_unsubscribed += 1
    db.commit()

    active_count = sum(1 for s in subscribers if not s.unsubscribed)

    return {
        "total_in_db": len(subscribers),
        "pushed_to_resend": pushed,
        "push_failed": push_failed,
        "unsubscribe_status_updated": updated_unsubscribed,
        "active_subscribers": active_count,
    }


@router.post("/send")
def send_newsletter(
    payload: NewsletterRequest,
    _admin: models.AdminUser = Depends(get_current_admin),
):
    if not RESEND_API_KEY or not RESEND_AUDIENCE_ID:
        raise HTTPException(
            status_code=400,
            detail="Resend ще не налаштований (немає RESEND_API_KEY або RESEND_AUDIENCE_ID)",
        )

    resend.api_key = RESEND_API_KEY
    try:
        broadcast = resend.Broadcasts.create(
            {
                "audience_id": RESEND_AUDIENCE_ID,
                "from": FROM_EMAIL,
                "subject": payload.subject,
                "html": _build_html(payload.body),
                "name": f"Newsletter: {payload.subject}",
            }
        )
        broadcast_id = broadcast.get("id") if isinstance(broadcast, dict) else getattr(broadcast, "id", None)
        if not broadcast_id:
            raise HTTPException(
                status_code=502,
                detail="Resend не повернув ID створеної розсилки — не можу її надіслати.",
            )
        resend.Broadcasts.send({"broadcast_id": broadcast_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Не вдалось надіслати розсилку через Resend: {e}")

    return {"status": "sent", "broadcast_id": broadcast_id}
