"""
Власна статистика відвідувань сайту — повністю на нашому сервері, у нашій
БД, без жодного стороннього сервісу (Vercel, Google Analytics тощо).

Дизайн навмисно простий: записуємо лише шлях сторінки й час — без cookies,
без IP-адрес, без будь-яких ідентифікаторів відвідувача. Через це можемо
рахувати перегляди сторінок (page views), але НЕ унікальних відвідувачів —
для цього знадобився б якийсь спосіб відрізняти одну людину від іншої
(cookie чи схоже), а це свідомо не додано (менше персональних даних —
менше клопоту з приватністю, і сайт і так ніде цим не користується).
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..analytics_models import PageView
from ..auth import get_current_admin
from ..database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

PERIOD_TO_DAYS = {
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}


class TrackRequest(BaseModel):
    path: str


@router.post("/track")
def track_page_view(payload: TrackRequest, db: Session = Depends(get_db)):
    """Публічний ендпоінт — викликається одним маленьким скриптом з кожної
    публічної сторінки сайту при завантаженні. Ніколи не повинен ламати
    сторінку відвідувачу, навіть якщо запис у БД не вдався з якоїсь причини."""
    try:
        path = (payload.path or "/").strip()[:255]
        db.add(PageView(path=path))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[analytics] не вдалось записати перегляд: {e}")
    return {"status": "ok"}


@router.get("/summary")
def analytics_summary(
    period: str = "week",
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    if period not in PERIOD_TO_DAYS:
        raise HTTPException(status_code=400, detail="period має бути одним з: day, week, month, year")

    since = datetime.utcnow() - timedelta(days=PERIOD_TO_DAYS[period])

    rows = (
        db.query(
            func.date(PageView.created_at).label("day"),
            func.count(PageView.id).label("pageviews"),
        )
        .filter(PageView.created_at >= since)
        .group_by(func.date(PageView.created_at))
        .order_by(func.date(PageView.created_at))
        .all()
    )

    daily = [{"date": str(r.day), "pageviews": r.pageviews} for r in rows]
    total_pageviews = sum(r["pageviews"] for r in daily)

    return {
        "period": period,
        "total_pageviews": total_pageviews,
        "daily": daily,
    }
