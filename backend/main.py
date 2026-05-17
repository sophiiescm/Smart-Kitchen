from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import (
    DUMMY_HASH,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import Base, engine, get_db
from models import User
from schemas import Token, UserRegister, UserResponse

# Tabellen anlegen (falls noch nicht vorhanden)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mein Projekt", version="0.1.0")

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
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Neuen Benutzer anlegen. Passwort wird als Argon2-Hash gespeichert."""
    # TODO: Implementiert diese Funktion
    # 1. Prüft, ob username oder email bereits existieren (→ 400)
    existing_user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Benutzername oder E-Mail bereits registriert"
        )
    # 2. Passwort hashen mit get_password_hash()
    hashed_pwd = get_password_hash(data.password)
    # 3. User-Objekt anlegen, in DB speichern, zurückgeben
    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_pwd
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
    # TODO: Implementiert diese Funktion
    # 1. Benutzer anhand von form_data.username in der DB suchen
    user = db.query(User).filter(User.username == form_data.username).first()
    # 2. Passwort mit verify_password() prüfen (Timing-Schutz: DUMMY_HASH nutzen)
    target_hash = user.hashed_password if user else DUMMY_HASH
    if not user or not verify_password(form_data.password, target_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 3. Bei Fehler: 401 zurückgeben (generische Meldung!)

    # 3. Token erzeugen
    access_token = create_access_token(username=user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/my-profile", response_model=UserResponse)
def get_profile(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Gibt das Profil des eingeloggten Benutzers zurück (geschützter Endpoint)."""
    # TODO: Implementiert diese Funktion
    # Hinweis: current_username kommt bereits validiert aus dem JWT (via Depends)
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
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
