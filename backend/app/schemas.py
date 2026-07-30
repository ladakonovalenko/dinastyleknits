from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ---------- Pattern ----------

class PatternBase(BaseModel):
    title: str
    price: str
    image_filename: Optional[str] = None
    description: Optional[str] = None
    etsy_url: str
    is_new: bool = False
    sort_order: int = 0


class PatternCreate(PatternBase):
    slug: Optional[str] = None


class PatternUpdate(BaseModel):
    """Усі поля опційні — дозволяє часткове оновлення (PATCH-стиль через PUT)."""
    title: Optional[str] = None
    price: Optional[str] = None
    image_filename: Optional[str] = None
    description: Optional[str] = None
    etsy_url: Optional[str] = None
    is_new: Optional[bool] = None
    sort_order: Optional[int] = None


class PatternOut(PatternBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------- Subscriber ----------

class SubscriberCreate(BaseModel):
    email: EmailStr


class SubscriberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class SubscriberWithStatus(BaseModel):
    """Те саме, що SubscriberOut, плюс `unsubscribed` — але це поле НЕ
    зберігається в базі даних узагалі. Обчислюється "на льоту" в самому
    ендпоінті, звіряючи email з живим списком контактів у Resend Audience.
    Свідомий вибір: попередня спроба зберігати цей статус окремою колонкою
    в БД призвела до серйозних проблем (авто-міграції ненадійно
    спрацьовують на цьому хостингу) — цей підхід повністю обходить БД,
    тому такого ризику більше немає."""

    id: int
    email: str
    created_at: datetime
    unsubscribed: bool = False


# ---------- Auth ----------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
