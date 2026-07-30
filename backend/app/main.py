from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import ALLOWED_ORIGINS
from .database import Base, engine
from .limiter import limiter
from .migrations import run_auto_migrations
from .routers import auth_router, newsletter, patterns, subscribers

app = FastAPI(title="DinaStyleKnits API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Базові security-заголовки. Не заміна повноцінного аудиту, але
    закриває найпростіші типові дірки (clickjacking, MIME-сніфінг тощо)."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # /docs, /redoc, /openapi.json — це єдині місця, де застосунок сам віддає
    # HTML, що виконується в браузері (Swagger/Redoc UI, довантажують свій
    # JS/CSS з CDN). Суворий CSP нижче їх ламав (біла сторінка) — тому для
    # решти API (яка віддає лише JSON/зображення) лишаємо суворо, а для
    # документації — не застосовуємо CSP взагалі.
    docs_paths = ("/docs", "/redoc", "/openapi.json")
    if not request.url.path.startswith(docs_paths):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

    return response


def _run_startup_tasks():
    """Створює таблиці, яких ще немає, і дотягує колонки, яких бракує в уже
    існуючих таблицях (легкі авто-міграції, без Alembic).

    ⚠️ Це НАВМИСНО викликається одразу тут, на рівні імпорту модуля, а не
    тільки через @app.on_event("startup") нижче. Причина: на хостингу
    cPanel/Passenger застосунок запускається через passenger_wsgi.py, який
    обгортає наш ASGI-застосунок бібліотекою a2wsgi для сумісності з
    WSGI. Перевірка показала, що a2wsgi обробляє лише окремі HTTP-запити
    і не запускає ASGI lifespan-подію (startup/shutdown) — тобто
    @app.on_event("startup") міг узагалі ніколи не виконуватись у
    продакшені. Виклик тут гарантує, що міграції реально відбудуться
    (модуль imports виконуються завжди, незалежно від сервера), навіть
    якщо lifespan-подія на конкретному хостингу не підтримується.
    Залишаємо той самий виклик і в @app.on_event("startup") нижче —
    для звичайних ASGI-серверів (uvicorn/Render) це просто означає, що
    міграції запускаються (безпечно, ідемпотентно) двічі поспіль."""
    Base.metadata.create_all(bind=engine)
    run_auto_migrations()

    if ALLOWED_ORIGINS == ["*"]:
        print(
            "[SECURITY WARNING] ALLOWED_ORIGINS = '*' — CORS відкритий для будь-якого "
            "сайту. Звузьте до реального домену фронтенду в Environment Variables."
        )


_run_startup_tasks()


@app.on_event("startup")
def on_startup():
    _run_startup_tasks()


# Роздача зображень товарів: /static/images/<filename>.jpg
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(patterns.router)
app.include_router(subscribers.router)
app.include_router(auth_router.router)
app.include_router(newsletter.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "allowed_origins": ALLOWED_ORIGINS}
