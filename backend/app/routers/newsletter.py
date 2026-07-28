"""
Розсилка новин одним натисканням з адмінки — щоб замовниці не треба було
самій заходити в Resend Dashboard і розбиратись з незнайомим інтерфейсом.

Технічно це обгортка над Resend Broadcast API: створюємо Broadcast на той
самий Audience, куди й так автоматично потрапляють підписники з форми на
сайті, і одразу відправляємо (параметр "send": True — один запит замість
двох окремих "створити" + "надіслати").
"""
import resend
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import models
from ..auth import get_current_admin
from ..config import FROM_EMAIL, RESEND_API_KEY, RESEND_AUDIENCE_ID

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
        <a href="{{{{RESEND_UNSUBSCRIBE_URL}}}}" style="color: #8A8A8A;">Unsubscribe</a>
      </div>
    </div>
    """


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
        result = resend.Broadcasts.create(
            {
                "audience_id": RESEND_AUDIENCE_ID,
                "from": FROM_EMAIL,
                "subject": payload.subject,
                "html": _build_html(payload.body),
                "name": f"Newsletter: {payload.subject}",
                "send": True,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Не вдалось надіслати розсилку через Resend: {e}")

    return {"status": "sent", "broadcast_id": result.get("id") if isinstance(result, dict) else None}
