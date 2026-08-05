"""
Власна статистика відвідувань сайту — повністю на нашому сервері, у нашій
БД, без жодного стороннього сервісу (Vercel, Google Analytics тощо).

Рахуємо і перегляди сторінок (page views), і унікальних відвідувачів —
але не через cookies, а через ОДНОСТОРОННІЙ ХЕШ IP-адреси відвідувача
разом з поточною датою. Це означає:
  - Той самий відвідувач у той самий день завжди дає той самий хеш —
    можна порахувати, скільки різних людей заходило за день.
  - Наступного дня хеш для тієї самої людини буде вже ІНШИЙ — неможливо
    відстежити одну людину протягом кількох днів чи тижнів.
  - Із самого хешу неможливо відновити реальну IP-адресу назад.
  - Реальна IP-адреса ніде не зберігається — рахується хеш і одразу
    забувається.

Чесне обмеження: через щоденну ротацію хешу, "унікальні відвідувачі за
тиждень/місяць" — це сума унікальних-за-кожен-день, а не дедуплікація
однієї людини протягом усього періоду (людина, що заходила в понеділок і
у вівторок, порахується як 2 різні відвідувачі). Це свідомий компроміс
заради приватності.
"""
import hashlib
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..analytics_models import PageView, PatternClick
from ..auth import get_current_admin
from ..config import JWT_SECRET
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


class PatternClickRequest(BaseModel):
    slug: str


def _get_client_ip(request: Request) -> str:
    """Сайт працює за проксі (Apache/Passenger на cPanel), тому пряма IP
    з'єднання може бути внутрішньою адресою проксі, а не реальною IP
    відвідувача. Спершу перевіряємо стандартний заголовок X-Forwarded-For
    (перше значення в ньому — реальний клієнт), і лише як запасний варіант
    беремо IP самого з'єднання."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _hash_visitor(ip: str) -> str:
    """Односторонній хеш IP + сьогоднішня дата + секрет застосунку (щоб
    хеш не можна було просто підібрати перебором відомих IP). Реальна IP
    ніде не зберігається — лише цей хеш."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    raw = f"{ip}|{today}|{JWT_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()


@router.post("/track")
def track_page_view(payload: TrackRequest, request: Request, db: Session = Depends(get_db)):
    """Публічний ендпоінт — викликається одним маленьким скриптом з кожної
    публічної сторінки сайту при завантаженні. Ніколи не повинен ламати
    сторінку відвідувачу, навіть якщо запис у БД не вдався з якоїсь причини."""
    try:
        path = (payload.path or "/").strip()[:255]
        visitor_hash = _hash_visitor(_get_client_ip(request))
        db.add(PageView(path=path, visitor_hash=visitor_hash))
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
            func.count(func.distinct(PageView.visitor_hash)).label("visitors"),
        )
        .filter(PageView.created_at >= since)
        .group_by(func.date(PageView.created_at))
        .order_by(func.date(PageView.created_at))
        .all()
    )

    daily = [{"date": str(r.day), "pageviews": r.pageviews, "visitors": r.visitors} for r in rows]
    total_pageviews = sum(r["pageviews"] for r in daily)
    total_visitors = sum(r["visitors"] for r in daily)

    return {
        "period": period,
        "total_pageviews": total_pageviews,
        "total_visitors": total_visitors,
        "daily": daily,
    }


@router.post("/pattern-click")
def track_pattern_click(payload: PatternClickRequest, db: Session = Depends(get_db)):
    """Публічний ендпоінт — викликається при кліку на картку товару (перехід
    на Etsy). Ніколи не повинен заважати самому переходу відвідувача,
    навіть якщо запис у БД не вдався з якоїсь причини."""
    try:
        slug = (payload.slug or "").strip()[:255]
        if slug:
            db.add(PatternClick(pattern_slug=slug))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"[analytics] не вдалось записати клік по товару: {e}")
    return {"status": "ok"}


@router.get("/pattern-clicks")
def pattern_click_summary(
    period: str = "week",
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    if period not in PERIOD_TO_DAYS:
        raise HTTPException(status_code=400, detail="period має бути одним з: day, week, month, year")

    since = datetime.utcnow() - timedelta(days=PERIOD_TO_DAYS[period])

    rows = (
        db.query(
            PatternClick.pattern_slug,
            func.count(PatternClick.id).label("clicks"),
        )
        .filter(PatternClick.created_at >= since)
        .group_by(PatternClick.pattern_slug)
        .order_by(func.count(PatternClick.id).desc())
        .all()
    )

    # Підтягуємо назви товарів там, де можливо (товар міг бути й видалений
    # пізніше — тоді просто покажемо його slug замість назви).
    patterns_by_slug = {p.slug: p for p in db.query(models.Pattern).all()}

    results = []
    for slug, clicks in rows:
        pattern = patterns_by_slug.get(slug)
        results.append(
            {
                "slug": slug,
                "title": pattern.title if pattern else slug,
                "clicks": clicks,
            }
        )

    return {"period": period, "patterns": results}
