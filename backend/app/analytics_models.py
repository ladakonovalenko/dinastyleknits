"""
Окрема модель для власної статистики відвідувань — навмисно в окремому
файлі, не в основному models.py, щоб тримати цю функціональність повністю
ізольованою від решти проєкту.

Таблиця створюється одразу тут, на рівні імпорту модуля (не через
@app.on_event("startup") — та подія ненадійно спрацьовує на поточному
хостингу, це вже спричиняло серйозні проблеми раніше). create_all() з
параметром tables=[...] торкається ЛИШЕ цієї однієї нової таблиці —
жодного ризику для вже існуючих таблиць (Pattern, Subscriber, AdminUser).

visitor_hash НЕ зберігає саму IP-адресу — лише її односторонній хеш разом
із поточною датою (див. hash_visitor() у routers/analytics.py). Реальну
IP-адресу з цього хешу відновити неможливо.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, inspect, text

from .database import Base, engine


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    visitor_hash = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class PatternClick(Base):
    """Клік по картці товару (перехід на Etsy). Зберігаємо лише slug
    товару й час — жодних даних про відвідувача."""

    __tablename__ = "pattern_clicks"

    id = Column(Integer, primary_key=True, index=True)
    pattern_slug = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


try:
    Base.metadata.create_all(bind=engine, tables=[PageView.__table__, PatternClick.__table__])

    # Якщо таблиця вже існувала з попередньої версії (без visitor_hash) —
    # create_all() її не чіпає (він тільки СТВОРЮЄ таблиці, яких немає, і
    # ніколи не змінює вже існуючі). Тому тут окремо, безпечно, дотягуємо
    # саме цю одну колонку, якщо її бракує — той самий перевірений підхід,
    # що вже використовується в основних міграціях проєкту.
    inspector = inspect(engine)
    if "page_views" in inspector.get_table_names():
        existing_columns = {c["name"] for c in inspector.get_columns("page_views")}
        if "visitor_hash" not in existing_columns:
            try:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE page_views ADD COLUMN visitor_hash VARCHAR"))
                print("[analytics] додано колонку page_views.visitor_hash")
            except Exception as e:
                # Найімовірніша причина — інший процес щойно додав цю саму
                # колонку одночасно (кілька воркерів стартують паралельно).
                print(f"[analytics] пропущено visitor_hash: {e}")
except Exception as e:
    print(f"[analytics] не вдалось створити/оновити таблиці page_views/pattern_clicks: {e}")
