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


# ---------- Auth ----------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
