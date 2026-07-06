"""
Наповнення БД початковими даними:
  1) 13 реальних патернів з Etsy-магазину DinaStyleKnits (назва/ціна/посилання —
     зібрано напряму з https://www.etsy.com/shop/DinaStyleKnits).
  2) Єдиний адмін-акаунт замовниці (email/пароль беруться з config.py / .env).

ВАЖЛИВО ⚠️ Прив'язка "image_filename" до кожного патерна зроблена
best-effort — за візуальною відповідністю фото до назви товару (Etsy не
віддає прямих посилань на мініатюри при звичайному запиті сторінки).
Перед показом замовниці обов'язково звірте з нею, що кожне фото
відповідає правильній назві/ціні — і за потреби поміняйте значення
image_filename нижче або через адмінку.

Запуск: python -m app.seed_data (один раз, за потреби — ідемпотентно,
повторний запуск не задублює записи).
"""
from . import models
from .auth import hash_password
from .config import ADMIN_EMAIL, ADMIN_PASSWORD
from .database import Base, SessionLocal, engine
from .migrations import run_auto_migrations
from .routers.patterns import slugify

PATTERNS = [
    {
        "title": "Easy Knit Poncho Pattern: Beginner Women's Capelet",
        "price": "$5.65",
        "image_filename": "easy-knit-poncho-beginner-capelet.jpg",
        "etsy_url": "https://www.etsy.com/listing/294453691",
        "is_new": False,
    },
    {
        "title": "Easy Knit Shawl Pattern: Triangle Chunky Leaves Design",
        "price": "$5.69",
        "image_filename": "easy-knit-shawl-triangle-chunky-leaves.jpg",
        "etsy_url": "https://www.etsy.com/listing/1038256635",
        "is_new": True,
    },
    {
        "title": "Crochet Cape Capelet Pattern: Easy Poncho Shawl",
        "price": "$5.90",
        "image_filename": "crochet-cape-capelet-easy-poncho-shawl.jpg",
        "etsy_url": "https://www.etsy.com/listing/472046848",
        "is_new": False,
    },
    {
        "title": "Love Latte Poncho Capelet Knitting Pattern: Easy Beginner Shawl",
        "price": "$5.60",
        "image_filename": "love-latte-poncho-capelet-beginner-shawl.jpg",
        "etsy_url": "https://www.etsy.com/listing/246923530",
        "is_new": False,
    },
    {
        "title": "Easy Knitted Ruffled Shawl Pattern: Beginner DIY",
        "price": "$5.68",
        "image_filename": "easy-knitted-ruffled-shawl-beginner-diy.jpg",
        "etsy_url": "https://www.etsy.com/listing/659222676",
        "is_new": False,
    },
    {
        "title": "Easy Fingerless Gloves Knitting Pattern (Striped)",
        "price": "$5.30",
        "image_filename": "easy-fingerless-gloves-striped.jpg",
        "etsy_url": "https://www.etsy.com/listing/561657550",
        "is_new": True,
    },
    {
        "title": "Easy Knit Shawl Pattern: Chunky Triangle Wrap",
        "price": "$5.68",
        "image_filename": "easy-knit-shawl-chunky-triangle-wrap.jpg",
        "etsy_url": "https://www.etsy.com/listing/209239231",
        "is_new": False,
    },
    {
        "title": "Granny Square Crochet Bag Pattern: Daisy Flower Tote",
        "price": "$4.99",
        "image_filename": "granny-square-crochet-bag-daisy-flower-tote.jpg",
        "etsy_url": "https://www.etsy.com/listing/525541097",
        "is_new": False,
    },
    {
        "title": "Easy Knit Triangle Shawl Pattern with Long Sides (Shawlette)",
        "price": "$4.99",
        "image_filename": "easy-knit-triangle-shawl-shawlette.jpg",
        "etsy_url": "https://www.etsy.com/listing/279140232",
        "is_new": False,
    },
    {
        "title": "Easy Knitting Pattern: Women's Mohair Yoke Poncho",
        "price": "$5.99",
        "image_filename": "easy-knitting-mohair-yoke-poncho.jpg",
        "etsy_url": "https://www.etsy.com/listing/267470137",
        "is_new": True,
    },
    {
        "title": "Knitted Triangle Shawl Pattern: Ruffled Lace Border",
        "price": "$5.48",
        "image_filename": "knitted-triangle-shawl-ruffled-lace-border.jpg",
        "etsy_url": "https://www.etsy.com/listing/501241416",
        "is_new": False,
    },
    {
        "title": "Crochet Mesh Cape Pattern, Easy Capelet Poncho Shawl",
        "price": "$5.69",
        "image_filename": "crochet-mesh-cape-easy-capelet-poncho.jpg",
        "etsy_url": "https://www.etsy.com/listing/558361392",
        "is_new": False,
    },
    {
        "title": "Evil Eye Granny Square Crochet Tote Bag Pattern",
        "price": "$4.99",
        "image_filename": "evil-eye-granny-square-crochet-tote-bag.jpg",
        "etsy_url": "https://www.etsy.com/listing/539074989",
        "is_new": False,
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    run_auto_migrations()

    db = SessionLocal()
    try:
        created_count = 0
        for item in PATTERNS:
            slug = slugify(item["title"])
            if db.query(models.Pattern).filter(models.Pattern.slug == slug).first():
                continue  # вже є — не дублюємо (ідемпотентність)
            db.add(models.Pattern(slug=slug, **item))
            created_count += 1
        db.commit()
        print(f"[seed] додано {created_count} нових патернів (з {len(PATTERNS)} у списку)")

        if not db.query(models.AdminUser).filter(models.AdminUser.email == ADMIN_EMAIL).first():
            db.add(models.AdminUser(email=ADMIN_EMAIL, hashed_password=hash_password(ADMIN_PASSWORD)))
            db.commit()
            print(f"[seed] створено адмін-акаунт: {ADMIN_EMAIL} (пароль — див. .env / config.py)")
        else:
            print("[seed] адмін-акаунт вже існує, пропускаю")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
