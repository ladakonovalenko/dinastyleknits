"""
Окрема модель для власної статистики відвідувань — навмисно в окремому
файлі, не в основному models.py, щоб тримати цю функціональність повністю
ізольованою від решти проєкту.

Таблиця створюється одразу тут, на рівні імпорту модуля (не через
@app.on_event("startup") — та подія ненадійно спрацьовує на поточному
хостингу, це вже спричиняло серйозні проблеми раніше). create_all() з
параметром tables=[...] торкається ЛИШЕ цієї однієї нової таблиці —
жодного ризику для вже існуючих таблиць (Pattern, Subscriber, AdminUser).
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base, engine


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


try:
    Base.metadata.create_all(bind=engine, tables=[PageView.__table__])
except Exception as e:
    # Найімовірніша причина — інший процес щойно створив цю саму таблицю
    # одночасно (кілька воркерів стартують паралельно). Не критично —
    # просто логуємо й ідемо далі, застосунок все одно має запуститись.
    print(f"[analytics] не вдалось створити таблицю page_views: {e}")
