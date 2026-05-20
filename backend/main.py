from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth import (
    DUMMY_HASH,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import Base, SessionLocal, engine, get_db, wait_for_db
from models import User
from schemas import Token, UserCreate, UserResponse

app = FastAPI(title="Mein Projekt", version="0.1.0")


@app.on_event("startup")
def startup():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "testuser").first():
            db.add(
                User(
                    username="testuser",
                    email="testuser@example.com",
                    password_hash=get_password_hash("test1234"),
                )
            )
            db.commit()
            print("Testbenutzer 'testuser' wurde angelegt.")
    finally:
        db.close()

# CORS: Erlaube Frontend-Hosts während der Entwicklung.
# Falls das Frontend auf einem anderen Port läuft, hier ergänzen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Authentifizierung
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Neuen Benutzer anlegen. Passwort wird als Argon2-Hash gespeichert."""
    existing = db.query(User).filter(
        or_(User.username == data.username, User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nutzername oder E-Mail bereits vergeben",
        )

    hashed_pwd = get_password_hash(data.password)
    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hashed_pwd,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    OAuth2 Password Flow: Empfängt username + password als Formular-Daten.
    Gibt einen JWT zurück.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    target_hash = user.password_hash if user else DUMMY_HASH
    if not user or not verify_password(form_data.password, target_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/my-profile", response_model=UserResponse)
def get_profile(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Gibt das Profil des eingeloggten Benutzers zurück (geschützter Endpoint)."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden",
        )
    return user


# ---------------------------------------------------------------------------
# TODO: Eure eigenen Endpoints hier einfügen
# ---------------------------------------------------------------------------

# Beispiel:
# @app.get("/items")
# def get_items(db: Session = Depends(get_db)):
#     return db.query(Item).all()
#
# @app.post("/items", status_code=201)
# def create_item(data: ItemCreate, db: Session = Depends(get_db)):
#     item = Item(**data.model_dump())
#     db.add(item)
#     db.commit()
#     db.refresh(item)
#     return item
