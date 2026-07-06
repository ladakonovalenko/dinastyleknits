from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

# check_same_thread потрібен лише для SQLite (не заважає Postgres, бо там ігнорується
# через connect_args, який ми додаємо умовно нижче).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency для FastAPI-роутів: видає сесію і гарантовано закриває її."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
