import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Prefer an explicit DATABASE_URL (provided by docker-compose). Fall back to
# individual MYSQL_* variables for local runs.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") or os.getenv("MYSQL_ROOT_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "testdb")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def wait_for_db(retries: int = 20, delay: float = 1.0) -> None:
    """Warte, bis die Datenbank erreichbar ist."""
    import time

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with engine.connect():
                return
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(
        f"Could not connect to database after {retries} attempts"
    ) from last_error


def get_db():
    """Dependency: liefert eine DB-Session und schließt sie danach."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
