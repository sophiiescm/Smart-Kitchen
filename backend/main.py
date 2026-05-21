from typing import Annotated, Optional
import time
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

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

app = FastAPI(title="SmartKitchen API", version="0.1.0")


@app.on_event("startup")
def startup():
    print("Warte kurz auf die Datenbank...")
    time.sleep(5) 
    
    print("Erstelle Datenbanktabellen...")
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
    except Exception as e:
        print(f"Fehler beim Anlegen des Testnutzers: {e}")
    finally:
        db.close()


# CORS-Middleware für die Frontend-Kommunikation
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


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Authentifizierung
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Neuen Benutzer anlegen."""
    existing = db.query(User).filter(
        or_(User.username == data.username, User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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
    """Login-Endpoint für den JWT-Token."""
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
    """Profil des eingeloggten Benutzers anzeigen."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden",
        )
    return user


# ---------------------------------------------------------------------------
# Rezept- und Bewertungs-Logik
# ---------------------------------------------------------------------------

@app.post("/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(
    data: RecipeCreate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Neues Rezept anlegen inklusive strukturierter Zutaten und Schritte."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

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
    db.commit()
    db.refresh(new_recipe)

    for ing in data.ingredients:
        db_ingredient = RecipeIngredient(
            recipe_id=new_recipe.id,
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit
        )
        db.add(db_ingredient)

    for step in data.steps:
        db_step = RecipeStep(
            recipe_id=new_recipe.id,
            step_number=step.step_number,
            instruction=step.instruction
        )
        db.add(db_step)

    db.commit()
    db.refresh(new_recipe)
    return new_recipe

@app.get("/recipes/search", response_model=list[RecipeResponse])
def search_recipes(
    title: Optional[str] = None,
    difficulty: Optional[str] = None,
    max_time: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """🌐 Filter-Suche nach bestimmten Kriterien (Titel, Schwierigkeit, Zeit)."""
    query = db.query(Recipe)

    if title:
        query = query.filter(Recipe.title.ilike(f"%{title}%"))
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if max_time:
        query = query.filter(Recipe.prep_time_minutes <= max_time)

    return query.all()


@app.post("/ratings", response_model=RatingResponse, status_code=201)
def rate_recipe_general(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_username: Annotated[str, Depends(get_current_user)] = None
):
    """Bewertung über den allgemeinen /ratings Endpoint abgeben oder aktualisieren."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
        
    recipe = db.query(Recipe).filter(Recipe.id == data.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
        
    existing_rating = db.query(RecipeRating).filter(
        RecipeRating.recipe_id == data.recipe_id,
        RecipeRating.user_id == user.id
    ).first()
    
    if existing_rating:
        existing_rating.rating = data.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
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
def search_and_get_recipes(q: Optional[str] = None, db: Session = Depends(get_db)):
    """🌐 Alle Rezepte abrufen oder nach Suchbegriff 'q' filtern (inkl. Live-Sterneberechnung)."""
    query = db.query(
        Recipe,
        func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average_rating"),
        func.count(RecipeRating.id).label("rating_count")
    ).outerjoin(RecipeRating, Recipe.id == RecipeRating.recipe_id)

    if q:
        search_term = f"%{q}%"
        query = query.outerjoin(RecipeIngredient, Recipe.id == RecipeIngredient.recipe_id)
        query = query.filter(
            or_(
                Recipe.title.ilike(search_term),
                Recipe.description.ilike(search_term),
                RecipeIngredient.name.ilike(search_term)
            )
        )

    query = query.group_by(Recipe.id)
    results = query.all()

    recipes_out = []
    for recipe, avg, count in results:
        # Konvertiert das DB-Modell sicher inklusive aller Unterlisten (Zutaten/Schritte)
        recipe_data = RecipeResponse.model_validate(recipe)
        recipe_data.average_rating = round(avg, 1)
        recipe_data.rating_count = count
        recipes_out.append(recipe_data)

    return recipes_out


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_single_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """🌐 Einzelnes Rezept anzeigen (inklusive Live-Sterneberechnung und allen Unterlisten!)."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    
    # Statistiken für dieses spezifische Rezept holen
    rating_stats = db.query(
        func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
        func.count(RecipeRating.id).label("count")
    ).filter(RecipeRating.recipe_id == recipe_id).first()
    
    # Sicher in Pydantic mappen, um Untertabellen nicht zu verlieren
    recipe_data = RecipeResponse.model_validate(recipe)
    recipe_data.average_rating = round(rating_stats.average, 1)
    recipe_data.rating_count = rating_stats.count
    
    return recipe_data


@app.delete("/recipes/{recipe_id}", status_code=200)
def delete_recipe(
    recipe_id: int,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Rezept löschen (nur für den Ersteller erlaubt)."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    user = db.query(User).filter(User.username == current_username).first()
    
    if recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Du bist nicht berechtigt, dieses Rezept zu löschen."
        )

    db.delete(recipe)
    db.commit()
    return {"detail": "Rezept erfolgreich gelöscht"}


@app.post("/recipes/{recipe_id}/ratings", response_model=RatingResponse, status_code=201)
def rate_recipe_by_id(
    recipe_id: int, 
    rating_data: RatingCreate, 
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Rezept direkt über seine ID bewerten."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden.")
    
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden.")

    existing_rating = db.query(RecipeRating).filter(
        RecipeRating.recipe_id == recipe_id, 
        RecipeRating.user_id == user.id
    ).first()

    if existing_rating:
        existing_rating.rating = rating_data.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        new_rating = RecipeRating(
            recipe_id=recipe_id,
            user_id=user.id,
            rating=rating_data.rating
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating