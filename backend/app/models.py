"""
Моделі даних.

Pattern      — картка Digital-товару (в'язальний патерн), що показується
               в сітці на головній і на власній сторінці /patterns/{slug}.
Subscriber   — email-адреси, зібрані через форму підписки (поки без
               інтеграції з розсилками — просто база на майбутнє).
AdminUser    — єдиний акаунт замовниці для входу в адмінку.
Post         — заготовка під блог (буде наповнюватись пізніше,
               посилання на відео з YouTube через video_url).
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, LargeBinary, String, Text

from .database import Base


class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    price = Column(String, nullable=False)  # рядком, бо це просто відображувана ціна ("$5.65")
    image_filename = Column(String, nullable=True)  # ім'я файлу в /static/images (початкові 13 товарів)
    image_data = Column(LargeBinary, nullable=True)  # бінарні дані фото, завантаженого через адмінку
    image_content_type = Column(String, nullable=True)  # напр. "image/jpeg"
    description = Column(Text, nullable=True)
    etsy_url = Column(String, nullable=False)  # посилання "Купити на Etsy"
    is_new = Column(Boolean, default=False)  # для сторінки "New releases"
    sort_order = Column(Integer, default=0)  # ручне сортування в сітці
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def image_url(self):
        """Уніфікований шлях до фото, незалежно від того, звідки воно —
        зі старих статичних файлів (перші 13 товарів) чи з БД (нові товари,
        додані через адмінку). Зберігання в БД обрано свідомо: безкоштовний
        план Render не має постійного диска — файл, завантажений під час
        роботи застосунку, зникав би вже за 15 хв бездіяльності сервісу."""
        if self.image_data:
            return f"/api/patterns/{self.slug}/image"
        if self.image_filename:
            return f"/static/images/{self.image_filename}"
        return None


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Post(Base):
    """Заготовка під блог. Поки не використовується у фронтенді — колонки
    закладені наперед, щоб пізніше не переробляти схему БД."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=True)
    youtube_url = Column(String, nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
