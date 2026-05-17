from pydantic import BaseModel
from typing import Optional

# ==========================================
# USER SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    # Das, was der User beim Registrieren mitschickt
    username: str
    password: str

class UserResponse(BaseModel):
    # Das, was das Backend nach außen zurückgibt (ohne Passwort!)
    id: int
    username: str

    # Wichtig: Erlaubt das automatische Lesen aus den SQLAlchemy-Modellen
    model_config = {"from_attributes": True}

# ==========================================
# RECIPE SCHEMAS
# ==========================================
class RecipeCreate(BaseModel):
    # Das, was beim Erstellen eines Rezepts gesendet wird
    title: str
    description: Optional[str] = None
    ingredients: str

class RecipeResponse(BaseModel):
    # Das, was beim Abrufen eines Rezepts zurückkommt
    id: int
    title: str
    description: Optional[str]
    ingredients: str
    owner_id: int

    model_config = {"from_attributes": True}

# ==========================================
# RATING SCHEMAS
# ==========================================
class RatingCreate(BaseModel):
    stars: int
    recipe_id: int

class RatingResponse(BaseModel):
    id: int
    stars: int
    user_id: int
    recipe_id: int

    model_config = {"from_attributes": True}