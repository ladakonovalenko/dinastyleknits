import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin
from ..database import get_db

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


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
