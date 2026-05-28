from typing import Annotated, Optional
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

from database import Base, SessionLocal, engine, get_db, wait_for_db
from models import (
    User, Recipe, RecipeIngredient, RecipeStep, RecipeRating, Tag,
    recipe_favorites, ShoppingListItem,
)
from categorize import categorize_ingredient
from schemas import (
    Token,
    UserCreate,
    UserResponse,
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RatingCreate,
    RatingResponse,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListItemResponse,
    AddFromRecipeRequest,
)

app = FastAPI(title="SmartKitchen API", version="0.1.0")


@app.on_event("startup")
def startup():
    print("Warte auf Datenbank-Verbindung...")
    wait_for_db(retries=30, delay=2.0)   # bis zu 60s warten

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
        image_url=data.image_url,
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
    favorite_ids: set[int] = set()
    return [_enrich_recipe(r, db, favorite_ids) for r in results]


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
    db: Session = Depends(get_db),
    current_username: Annotated[Optional[str], Depends(get_current_user_optional)] = None,
):
    """🌐 Öffentliche Rezepte abrufen und optional filtern.

    Eingeloggte Nutzer sehen zusätzlich ihre eigenen privaten Rezepte.
    """
    # Basis-Filter: öffentliche Rezepte ODER (eingeloggt) eigene private Rezepte
    if current_username:
        owner = db.query(User).filter(User.username == current_username).first()
        if owner:
            query = db.query(Recipe).filter(
                or_(Recipe.is_public.is_(True), Recipe.user_id == owner.id)
            )
        else:
            query = db.query(Recipe).filter(Recipe.is_public.is_(True))
    else:
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
    favorite_ids = _get_user_favorite_recipe_ids(db, current_username)
    return [_enrich_recipe(r, db, favorite_ids) for r in recipes]


def _get_user_favorite_recipe_ids(db: Session, username: Optional[str]) -> set[int]:
    """Liefert die Menge der Rezept-IDs, die der angegebene User favorisiert hat.
    Bei anonymen Zugriffen ist die Menge leer."""
    if not username:
        return set()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return set()
    rows = db.execute(
        recipe_favorites.select().where(recipe_favorites.c.user_id == user.id)
    ).fetchall()
    return {row.recipe_id for row in rows}


def _enrich_recipe(recipe: Recipe, db: Session, favorite_ids: set[int]) -> RecipeResponse:
    """Wandelt ein Recipe-ORM-Objekt in eine RecipeResponse um und ergänzt
    Bewertungs-Metadaten sowie den Favoriten-Status."""
    rating_stats = db.query(
        func.coalesce(func.avg(RecipeRating.rating), 0.0).label("average"),
        func.count(RecipeRating.id).label("count")
    ).filter(RecipeRating.recipe_id == recipe.id).first()

    recipe_data = RecipeResponse.model_validate(recipe)
    recipe_data.average_rating = round(rating_stats.average, 1)
    recipe_data.rating_count = rating_stats.count
    recipe_data.is_favorited = recipe.id in favorite_ids
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


# WICHTIG: spezielle /recipes/... Routen MÜSSEN vor /recipes/{recipe_id} stehen,
# sonst versucht FastAPI z.B. "mine" oder "favorites" in int zu konvertieren.


@app.get("/recipes/favorites", response_model=list[RecipeResponse])
def get_favorite_recipes(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """❤ Favoriten-Liste des eingeloggten Users."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    favorite_ids = _get_user_favorite_recipe_ids(db, current_username)
    recipes = db.query(Recipe).filter(Recipe.id.in_(favorite_ids)).all() if favorite_ids else []
    # Private Rezepte anderer User filtern (Sicherheit, falls jemand mal ein
    # öffentliches Rezept favorisiert hat das später auf privat gesetzt wurde)
    visible = [r for r in recipes if r.is_public or r.user_id == user.id]
    return [_enrich_recipe(r, db, favorite_ids) for r in visible]


@app.post("/recipes/{recipe_id}/favorite", status_code=201)
def add_favorite(
    recipe_id: int,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """❤ Rezept zu den Favoriten hinzufügen."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    if not recipe.is_public and recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privates Rezept kann nicht favorisiert werden.",
        )

    # Existiert schon? Dann idempotent ignorieren.
    existing = db.execute(
        recipe_favorites.select()
        .where(recipe_favorites.c.user_id == user.id)
        .where(recipe_favorites.c.recipe_id == recipe.id)
    ).first()
    if not existing:
        db.execute(
            recipe_favorites.insert().values(user_id=user.id, recipe_id=recipe.id)
        )
        db.commit()

    return {"detail": "Zu Favoriten hinzugefügt", "recipe_id": recipe_id, "is_favorited": True}


@app.delete("/recipes/{recipe_id}/favorite", status_code=200)
def remove_favorite(
    recipe_id: int,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """💔 Rezept aus den Favoriten entfernen."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    db.execute(
        recipe_favorites.delete()
        .where(recipe_favorites.c.user_id == user.id)
        .where(recipe_favorites.c.recipe_id == recipe_id)
    )
    db.commit()
    return {"detail": "Aus Favoriten entfernt", "recipe_id": recipe_id, "is_favorited": False}



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
    favorite_ids = _get_user_favorite_recipe_ids(db, current_username)
    return [_enrich_recipe(r, db, favorite_ids) for r in recipes]


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

    favorite_ids = _get_user_favorite_recipe_ids(db, current_username)
    return _enrich_recipe(recipe, db, favorite_ids)


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
    if data.image_url is not None:
        recipe.image_url = data.image_url
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

    favorite_ids = _get_user_favorite_recipe_ids(db, current_username)
    return _enrich_recipe(recipe, db, favorite_ids)


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


# ---------------------------------------------------------------------------
# Einkaufsliste
# ---------------------------------------------------------------------------

def _normalize_name(name: str) -> str:
    """Normalisiert Zutatennamen für Aggregation:
    trimmen, lowercase, doppelte Leerzeichen weg.
    'Mehl Type 405' und 'mehl type 405' werden so identisch behandelt.
    """
    return " ".join(name.strip().lower().split())


def _normalize_unit(unit: Optional[str]) -> Optional[str]:
    """Lowercase + trim, oder None wenn leer."""
    if not unit:
        return None
    u = unit.strip().lower()
    return u if u else None


def _add_or_aggregate_item(
    db: Session,
    user_id: int,
    name: str,
    amount: Optional[float],
    unit: Optional[str],
    recipe_id: Optional[int] = None,
) -> ShoppingListItem:
    """Sucht ein passendes UNGEHAKTES Item des Users und addiert die Menge
    auf, oder legt ein neues Item an.

    Match-Kriterien: gleicher (normalisierter) Name UND gleiche (normalisierte)
    Einheit. Unterschiedliche Einheiten ergeben getrennte Items, damit wir
    keine Birnen mit Äpfeln verrechnen (z.B. '500 g Mehl' + '1 kg Mehl').
    """
    norm_name = _normalize_name(name)
    norm_unit = _normalize_unit(unit)
    category = categorize_ingredient(name)

    candidates = (
        db.query(ShoppingListItem)
        .filter(
            ShoppingListItem.user_id == user_id,
            ShoppingListItem.is_checked.is_(False),
        )
        .all()
    )

    for candidate in candidates:
        if _normalize_name(candidate.name) != norm_name:
            continue
        if _normalize_unit(candidate.unit) != norm_unit:
            continue
        # Match! Mengen aggregieren — None wird als 0 behandelt.
        if amount is not None or candidate.amount is not None:
            candidate.amount = (candidate.amount or 0.0) + (amount or 0.0)
        # Kategorie bei Bedarf nachziehen
        if not candidate.category:
            candidate.category = category
        db.commit()
        db.refresh(candidate)
        return candidate

    # Kein Match → neues Item
    new_item = ShoppingListItem(
        user_id=user_id,
        name=name.strip(),
        amount=amount,
        unit=norm_unit,
        category=category,
        is_checked=False,
        recipe_id=recipe_id,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.get("/shopping-list", response_model=list[ShoppingListItemResponse])
def get_shopping_list(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Komplette Einkaufsliste des eingeloggten Users.

    Sortiert: ungehakte zuerst (gruppiert nach Kategorie), abgehakte ans Ende.
    """
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    items = (
        db.query(ShoppingListItem)
        .filter(ShoppingListItem.user_id == user.id)
        .order_by(
            ShoppingListItem.is_checked.asc(),
            ShoppingListItem.category.asc(),
            ShoppingListItem.created_at.asc(),
        )
        .all()
    )
    return items


@app.post("/shopping-list/items", response_model=ShoppingListItemResponse, status_code=201)
def add_manual_item(
    data: ShoppingListItemCreate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Manuelles Item hinzufügen (z.B. 'Spülmittel'). Mit Aggregation."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein")

    return _add_or_aggregate_item(
        db, user.id, data.name, data.amount, data.unit, recipe_id=None
    )


@app.post("/shopping-list/from-recipe/{recipe_id}", response_model=list[ShoppingListItemResponse])
def add_from_recipe(
    recipe_id: int,
    req: AddFromRecipeRequest,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Alle Zutaten eines Rezepts auf die Einkaufsliste übernehmen, mit
    optionalem Skalierungsfaktor (z.B. 2.0 für doppelte Portionen)."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    if not recipe.is_public and recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privates Rezept anderer User kann nicht übernommen werden.",
        )

    added: list[ShoppingListItem] = []
    for ing in recipe.ingredients:
        scaled_amount = ing.amount * req.scale if ing.amount is not None else None
        item = _add_or_aggregate_item(
            db, user.id, ing.name, scaled_amount, ing.unit, recipe_id=recipe.id
        )
        added.append(item)
    return added


@app.patch("/shopping-list/items/{item_id}", response_model=ShoppingListItemResponse)
def update_item(
    item_id: int,
    data: ShoppingListItemUpdate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Item ändern — typisch fürs Abhaken (is_checked) oder Mengen-Korrektur."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == item_id,
        ShoppingListItem.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item nicht gefunden")

    if data.name is not None:
        item.name = data.name.strip()
        item.category = categorize_ingredient(item.name)
    if data.amount is not None:
        item.amount = data.amount
    if data.unit is not None:
        item.unit = _normalize_unit(data.unit)
    if data.is_checked is not None:
        item.is_checked = data.is_checked

    db.commit()
    db.refresh(item)
    return item


@app.delete("/shopping-list/items/{item_id}", status_code=200)
def delete_item(
    item_id: int,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Einzelnes Item löschen."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == item_id,
        ShoppingListItem.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item nicht gefunden")
    db.delete(item)
    db.commit()
    return {"detail": "Item gelöscht"}


@app.delete("/shopping-list/checked", status_code=200)
def clear_checked(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Alle abgehakten Items löschen — typisch nach dem Einkauf."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    deleted = db.query(ShoppingListItem).filter(
        ShoppingListItem.user_id == user.id,
        ShoppingListItem.is_checked.is_(True),
    ).delete()
    db.commit()
    return {"detail": "Abgehakte Items gelöscht", "deleted": deleted}


@app.delete("/shopping-list", status_code=200)
def clear_all(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Komplette Einkaufsliste leeren."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    deleted = db.query(ShoppingListItem).filter(
        ShoppingListItem.user_id == user.id
    ).delete()
    db.commit()
    return {"detail": "Liste geleert", "deleted": deleted}