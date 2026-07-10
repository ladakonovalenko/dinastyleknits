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
from .routers import auth_router, patterns, subscribers

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
    # API віддає лише JSON/зображення, а не HTML, що виконується в браузері —
    # тому CSP тут навмисно суворий (застосунок сам не рендерить нічий контент).
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


@app.on_event("startup")
def on_startup():
    # Створює таблиці, якщо їх ще немає, і дотягує колонки, яких бракує
    # в уже існуючих таблицях (легкі авто-міграції, без Alembic).
    Base.metadata.create_all(bind=engine)
    run_auto_migrations()

    if ALLOWED_ORIGINS == ["*"]:
        print(
            "[SECURITY WARNING] ALLOWED_ORIGINS = '*' — CORS відкритий для будь-якого "
            "сайту. Звузьте до реального домену фронтенду в Environment Variables на Render."
        )


# Роздача зображень товарів: /static/images/<filename>.jpg
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(patterns.router)
app.include_router(subscribers.router)
app.include_router(auth_router.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
