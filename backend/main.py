from typing import Annotated
import time
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

from database import Base, SessionLocal, engine, get_db
from models import User, Recipe, RecipeIngredient, RecipeStep, RecipeRating
from schemas import Token, UserCreate, UserResponse, RecipeCreate, RecipeResponse, RatingCreate, RatingResponse

app = FastAPI(title="Mein Projekt", version="0.1.0")


@app.on_event("startup")
  def startup():
      print("Warte kurz auf die Datenbank...")
      time.sleep(5) 
      
      import models
      print("Erstelle Datenbanktabellen...")
      models.Base.metadata.create_all(bind=engine)
      
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
      except Exception as e:
          print(f"Fehler beim Anlegen des Testnutzers: {e}")
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
# ---------------------------------------------------------------------------
# REZEPT-LOGIK (Phase 2 - Implementiert und abgesichert von Person 2)
# ---------------------------------------------------------------------------

@app.post("/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(
    data: RecipeCreate,
    current_username: Annotated[str, Depends(get_current_user)],  # 🔒 Abgesichert durch Person 2
    db: Session = Depends(get_db)
):
    """Neues Rezept anlegen inklusive strukturierter Zutaten und Schritte."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    # 1. Haupt-Rezept anlegen
    new_recipe = Recipe(
        title=data.title,
        description=data.description,
        prep_time_minutes=data.prep_time_minutes,
        servings=data.servings,
        difficulty=data.difficulty,
        is_public=data.is_public,
        user_id=user.id
    )
    db.add(new_recipe)
    db.commit()  # Generiert die neue recipe.id
    db.refresh(new_recipe)

    # 2. Zutaten aus der Pydantic-Liste in die DB schreiben (Person 1 Models)
    for ing in data.ingredients:
        db_ingredient = RecipeIngredient(
            recipe_id=new_recipe.id,
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit
        )
        db.add(db_ingredient)

    # 3. Schritte aus der Pydantic-Liste in die DB schreiben (Person 1 Models)
    for step in data.steps:
        db_step = RecipeStep(
            recipe_id=new_recipe.id,
            step_number=step.step_number,
            instruction=step.instruction
        )
        db.add(db_step)

    db.commit()
    db.refresh(new_recipe)  # Lädt das Rezept mitsamt den neuen Beziehungen neu
    return new_recipe

@app.post("/ratings", response_model=RatingResponse, status_code=201)
def rate_recipe(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_username: Annotated[str, Depends(get_current_user)] = None  # 🔒 Konsistent abgesichert
):
    """Erstellt eine Bewertung (1-5 Sterne) für ein Rezept oder aktualisiert sie."""
    # 1. Den aktuell eingeloggten User aus der DB laden
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
        
    # 2. Prüfen, ob das Rezept existiert
    recipe = db.query(Recipe).filter(Recipe.id == data.recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Rezept nicht gefunden"
        )
        
    # 3. Prüfen, ob dieser User das Rezept bereits bewertet hat
    existing_rating = db.query(RecipeRating).filter(
        RecipeRating.recipe_id == data.recipe_id,
        RecipeRating.user_id == user.id
    ).first()
    
    if existing_rating:
        # Falls ja: Bewertung updaten
        existing_rating.rating = data.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Falls nein: Neue Bewertung speichern
        new_rating = RecipeRating(
            recipe_id=data.recipe_id,
            user_id=user.id,
            rating=data.rating
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating

@app.get("/recipes", response_model=list[RecipeResponse])
def get_all_recipes(db: Session = Depends(get_db)):
    """🌐 Öffentlich zugänglich: Alle Rezepte abrufen."""
    return db.query(Recipe).all()


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_single_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """🌐 Öffentlich zugänglich: Einzelnes Rezept anhand der ID anzeigen."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    return recipe


@app.delete("/recipes/{recipe_id}", status_code=200)
def delete_recipe(
    recipe_id: int,
    current_username: Annotated[str, Depends(get_current_user)],  # 🔒 Abgesichert!
    db: Session = Depends(get_db)
):
    """Rezept löschen. Prüft vorher, ob das Rezept wirklich dem User gehört."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    user = db.query(User).filter(User.username == current_username).first()
    
    # 🔒 Security Check: Gehört das Rezept dem anfragenden User?
    if recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Du bist nicht berechtigt, dieses Rezept zu löschen."
        )

    db.delete(recipe)
    db.commit()
    return {"detail": "Rezept erfolgreich gelöscht"}