import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv() #Lädt die Variablen aus der .env Datei

DATABASE_URL = os.getenv("DATABASE_URL")

# Falls DATABASE_URL leer ist (z.B. lokal ohne Docker), 
# ist ein Fallback auf eine lokale SQLite oder MySQL sinnvoll
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:geheimespasswort@localhost:3306/myapp"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: liefert eine DB-Session und schließt sie danach."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
