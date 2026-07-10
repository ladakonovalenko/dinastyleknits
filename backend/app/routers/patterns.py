import re
import unicodedata
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin
from ..database import get_db

router = APIRouter(prefix="/api/patterns", tags=["patterns"])

ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}  # реальний формат файлу (Pillow), не Content-Type від клієнта
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB — достатньо з запасом для фото 1024x1024


def slugify(title: str) -> str:
    value = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[\s_-]+", "-", value)


# ---------- Публічні ендпоінти (без авторизації) ----------

@router.get("", response_model=list[schemas.PatternOut])
def list_patterns(only_new: bool = False, db: Session = Depends(get_db)):
    """Список усіх патернів для сітки на головній. only_new=true — для сторінки New releases."""
    query = db.query(models.Pattern)
    if only_new:
        query = query.filter(models.Pattern.is_new.is_(True))
    return query.order_by(models.Pattern.sort_order, models.Pattern.created_at.desc()).all()


@router.get("/{slug}", response_model=schemas.PatternOut)
def get_pattern(slug: str, db: Session = Depends(get_db)):
    """Дані для повної сторінки товару /patterns/{slug}."""
    pattern = db.query(models.Pattern).filter(models.Pattern.slug == slug).first()
    if pattern is None:
        raise HTTPException(status_code=404, detail="Патерн не знайдено")
    return pattern


@router.get("/{slug}/image")
def get_pattern_image(slug: str, db: Session = Depends(get_db)):
    """Віддає фото, завантажене через адмінку (зберігається в БД, а не на
    диску — безкоштовний план Render не має постійного диска, тож файл,
    записаний під час роботи застосунку, зникав би при кожному засинанні)."""
    pattern = db.query(models.Pattern).filter(models.Pattern.slug == slug).first()
    if pattern is None or not pattern.image_data:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    return Response(content=pattern.image_data, media_type=pattern.image_content_type or "image/jpeg")


# ---------- Адмінські ендпоінти (потрібен JWT) ----------

@router.post("", response_model=schemas.PatternOut, status_code=status.HTTP_201_CREATED)
def create_pattern(
    payload: schemas.PatternCreate,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    slug = payload.slug or slugify(payload.title)
    if db.query(models.Pattern).filter(models.Pattern.slug == slug).first():
        raise HTTPException(status_code=400, detail="Патерн з таким slug вже існує")

    pattern = models.Pattern(**payload.model_dump(exclude={"slug"}), slug=slug)
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern


@router.put("/{slug}", response_model=schemas.PatternOut)
def update_pattern(
    slug: str,
    payload: schemas.PatternUpdate,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    pattern = db.query(models.Pattern).filter(models.Pattern.slug == slug).first()
    if pattern is None:
        raise HTTPException(status_code=404, detail="Патерн не знайдено")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pattern, field, value)

    db.commit()
    db.refresh(pattern)
    return pattern


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pattern(
    slug: str,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    pattern = db.query(models.Pattern).filter(models.Pattern.slug == slug).first()
    if pattern is None:
        raise HTTPException(status_code=404, detail="Патерн не знайдено")
    db.delete(pattern)
    db.commit()


@router.post("/{slug}/image", response_model=schemas.PatternOut)
async def upload_pattern_image(
    slug: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """Завантаження/заміна фото товару. Викликається окремим запитом одразу
    після створення патерну (спочатку створюємо запис із текстовими полями,
    потім прикріплюємо до нього фото) — так адмінка може показати помилку
    саме на етапі, де вона сталась."""
    pattern = db.query(models.Pattern).filter(models.Pattern.slug == slug).first()
    if pattern is None:
        raise HTTPException(status_code=404, detail="Патерн не знайдено")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Файл завеликий (максимум 5MB)")

    # Не довіряємо Content-Type від клієнта (його легко підмінити) —
    # відкриваємо файл через Pillow і перевіряємо, що це справді коректне
    # зображення дозволеного формату. verify() перевіряє цілісність файлу,
    # але "закриває" об'єкт — тому формат читаємо окремим повторним open().
    try:
        Image.open(BytesIO(content)).verify()
        detected_format = Image.open(BytesIO(content)).format
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Файл пошкоджений або не є зображенням")

    if detected_format not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail="Дозволені формати: JPEG, PNG, WebP")

    content_type_map = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
    pattern.image_data = content
    pattern.image_content_type = content_type_map[detected_format]
    db.commit()
    db.refresh(pattern)
    return pattern
