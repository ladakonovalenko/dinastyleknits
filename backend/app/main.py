from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import ALLOWED_ORIGINS
from .database import Base, engine
from .migrations import run_auto_migrations
from .routers import auth_router, patterns, subscribers

app = FastAPI(title="DinaStyleKnits API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Створює таблиці, якщо їх ще немає, і дотягує колонки, яких бракує
    # в уже існуючих таблицях (легкі авто-міграції, без Alembic).
    Base.metadata.create_all(bind=engine)
    run_auto_migrations()


# Роздача зображень товарів: /static/images/<filename>.jpg
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(patterns.router)
app.include_router(subscribers.router)
app.include_router(auth_router.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
