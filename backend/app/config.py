"""
Конфігурація застосунку. Значення читаються зі змінних середовища (.env),
щоб не хардкодити секрети та легко перемикатись між локальною розробкою й Render.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # локально читає backend/.env; на Render змінні задаються в дашборді

# --- База даних -------------------------------------------------------------
# Локально: SQLite-файл поруч з бекендом.
# На Render: підставте DATABASE_URL з Postgres (напр. postgresql://user:pass@host/db)
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'dinastyleknits.db'}"

# --- Авторизація адмінки ------------------------------------------------------
# Єдиний адмін-акаунт (сама замовниця). Дані для першого входу задаються тут
# і використовуються скриптом seed_data.py для створення акаунта при першому запуску.
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "dina@dinastyleknits.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-on-first-login")

# --- JWT ---------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # токен адмінки живе 7 днів

# --- CORS ----------------------------------------------------------------
# На проді сюди додати реальний домен фронтенду замовниці.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# --- Email (Resend) --------------------------------------------------------
# RESEND_API_KEY / RESEND_AUDIENCE_ID — потрібні, щоб нові підписники
# автоматично потрапляли в Audience у Resend, і щоб працювала розсилка
# новин через адмінку. Якщо не задані — сайт і далі працює нормально,
# просто без розсилки (підписка як і раніше зберігається в БД).
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_AUDIENCE_ID = os.getenv("RESEND_AUDIENCE_ID", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "DinaStyleKnits <onboarding@resend.dev>")
