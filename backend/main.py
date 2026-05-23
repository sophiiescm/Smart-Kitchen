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
    get_current_user_optional,
    get_password_hash,
    verify_password,
)

from database import Base, SessionLocal, engine, get_db
from models import User, Recipe, RecipeIngredient, RecipeStep, RecipeRating, Tag
from schemas import (
    Token,
    UserCreate,
    UserResponse,
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RatingCreate,
    RatingResponse,
)

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
        category=data.category,
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

    tags = []
    for tag_name in data.tags:
        normalized_name = tag_name.strip()
        if not normalized_name:
            continue
        existing_tag = db.query(Tag).filter(Tag.name == normalized_name).first()
        if existing_tag:
            tags.append(existing_tag)
        else:
            new_tag = Tag(name=normalized_name)
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)
            tags.append(new_tag)

    for tag in tags:
        new_recipe.tags.append(tag)

    db.commit()
    db.refresh(new_recipe)
    return new_recipe

@app.get("/recipes/search", response_model=list[RecipeResponse])
def search_recipes(
    q: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    difficulty: Optional[str] = None,
    max_time: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """🌐 Öffentliche Rezepte suchen und nach Kategorie/Tag filtern."""
    query = db.query(Recipe)
    query = query.filter(Recipe.is_public.is_(True))

    if q:
        search_term = f"%{q}%"
        query = query.outerjoin(RecipeIngredient).filter(
            or_(
                Recipe.title.ilike(search_term),
                Recipe.description.ilike(search_term),
                RecipeIngredient.name.ilike(search_term)
            )
        )
    if category:
        query = query.filter(Recipe.category.ilike(category))
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if max_time:
        query = query.filter(Recipe.prep_time_minutes <= max_time)
    if tag:
        query = query.join(Recipe.tags).filter(Tag.name.ilike(tag))

    results = query.distinct().all()
    recipes_out = []
    for recipe in results:
        rating_stats = db.query(
            func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
            func.count(RecipeRating.id).label("count")
        ).filter(RecipeRating.recipe_id == recipe.id).first()

        recipe_data = RecipeResponse.model_validate(recipe)
        recipe_data.average_rating = round(rating_stats.average, 1)
        recipe_data.rating_count = rating_stats.count
        recipes_out.append(recipe_data)

    return recipes_out


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

    if not recipe.is_public and recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dieses Rezept ist privat und darf nicht bewertet werden.",
        )
        
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
def list_public_recipes(
    q: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    difficulty: Optional[str] = None,
    max_time: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """🌐 Öffentliche Rezepte abrufen und optional filtern."""
    query = db.query(Recipe).filter(Recipe.is_public.is_(True))

    if q:
        search_term = f"%{q}%"
        query = query.outerjoin(RecipeIngredient).filter(
            or_(
                Recipe.title.ilike(search_term),
                Recipe.description.ilike(search_term),
                RecipeIngredient.name.ilike(search_term)
            )
        )
    if category:
        query = query.filter(Recipe.category.ilike(category))
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if max_time:
        query = query.filter(Recipe.prep_time_minutes <= max_time)
    if tag:
        query = query.join(Recipe.tags).filter(Tag.name.ilike(tag))

    recipes = query.distinct().all()
    recipes_out = []
    for recipe in recipes:
        rating_stats = db.query(
            func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
            func.count(RecipeRating.id).label("count")
        ).filter(RecipeRating.recipe_id == recipe.id).first()

        recipe_data = RecipeResponse.model_validate(recipe)
        recipe_data.average_rating = round(rating_stats.average, 1)
        recipe_data.rating_count = rating_stats.count
        recipes_out.append(recipe_data)

    return recipes_out


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_single_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_username: Annotated[Optional[str], Depends(get_current_user_optional)] = None,
):
    """🌐 Einzelnes Rezept anzeigen. Private Rezepte nur für den Besitzer."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    is_owner = False
    if current_username:
        owner = db.query(User).filter(User.username == current_username).first()
        is_owner = owner is not None and owner.id == recipe.user_id

    if not recipe.is_public and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dieses Rezept ist privat und nur für den Besitzer sichtbar.",
        )

    rating_stats = db.query(
        func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
        func.count(RecipeRating.id).label("count")
    ).filter(RecipeRating.recipe_id == recipe_id).first()

    recipe_data = RecipeResponse.model_validate(recipe)
    recipe_data.average_rating = round(rating_stats.average, 1)
    recipe_data.rating_count = rating_stats.count

    return recipe_data


def _build_tag_objects(db: Session, tag_names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    for tag_name in tag_names:
        normalized_name = tag_name.strip()
        if not normalized_name:
            continue
        existing_tag = db.query(Tag).filter(Tag.name == normalized_name).first()
        if existing_tag:
            tags.append(existing_tag)
        else:
            new_tag = Tag(name=normalized_name)
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)
            tags.append(new_tag)
    return tags


@app.get("/recipes/mine", response_model=list[RecipeResponse])
def get_my_recipes(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """🌐 Eigene Rezepte abrufen (inklusive privater Rezepte)."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    recipes = db.query(Recipe).filter(Recipe.user_id == user.id).all()
    recipes_out = []
    for recipe in recipes:
        rating_stats = db.query(
            func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
            func.count(RecipeRating.id).label("count")
        ).filter(RecipeRating.recipe_id == recipe.id).first()

        recipe_data = RecipeResponse.model_validate(recipe)
        recipe_data.average_rating = round(rating_stats.average, 1)
        recipe_data.rating_count = rating_stats.count
        recipes_out.append(recipe_data)

    return recipes_out


@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Rezept aktualisieren. Nur der Eigentümer darf Änderungen vornehmen."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    user = db.query(User).filter(User.username == current_username).first()
    if not user or recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Du bist nicht berechtigt, dieses Rezept zu bearbeiten.",
        )

    if data.title is not None:
        recipe.title = data.title
    if data.description is not None:
        recipe.description = data.description
    if data.prep_time_minutes is not None:
        recipe.prep_time_minutes = data.prep_time_minutes
    if data.servings is not None:
        recipe.servings = data.servings
    if data.difficulty is not None:
        recipe.difficulty = data.difficulty
    if data.category is not None:
        recipe.category = data.category
    if data.is_public is not None:
        recipe.is_public = data.is_public

    if data.ingredients is not None:
        db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe.id).delete()
        for ing in data.ingredients:
            db.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    name=ing.name,
                    amount=ing.amount,
                    unit=ing.unit,
                )
            )

    if data.steps is not None:
        db.query(RecipeStep).filter(RecipeStep.recipe_id == recipe.id).delete()
        for step in data.steps:
            db.add(
                RecipeStep(
                    recipe_id=recipe.id,
                    step_number=step.step_number,
                    instruction=step.instruction,
                )
            )

    if data.tags is not None:
        recipe.tags.clear()
        recipe.tags.extend(_build_tag_objects(db, data.tags))

    db.commit()
    db.refresh(recipe)

    rating_stats = db.query(
        func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
        func.count(RecipeRating.id).label("count")
    ).filter(RecipeRating.recipe_id == recipe.id).first()

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

    if not recipe.is_public and recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dieses Rezept ist privat und darf nicht bewertet werden.",
        )

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