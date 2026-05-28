from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ==========================================
# ZUTATEN & SCHRITTE SCHEMAS (Neu für Phase 2)
# ==========================================
class IngredientBase(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientResponse(IngredientBase):
    id: int
    recipe_id: int
    model_config = {"from_attributes": True}

class StepBase(BaseModel):
    step_number: int
    instruction: str

class StepCreate(StepBase):
    pass

class StepResponse(StepBase):
    id: int
    recipe_id: int
    model_config = {"from_attributes": True}


# ==========================================
# TAG SCHEMAS
# ==========================================
class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int
    model_config = {"from_attributes": True}


# ==========================================
# USER SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==========================================
# RECIPE SCHEMAS (Komplett überarbeitet)
# ==========================================
class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_public: bool = False

class RecipeCreate(RecipeBase):
    # Beim Erstellen schickt das Frontend direkt Listen für Zutaten und Schritte mit
    ingredients: List[IngredientCreate] = []
    steps: List[StepCreate] = []
    tags: List[str] = []

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_public: Optional[bool] = None
    ingredients: Optional[List[IngredientCreate]] = None
    steps: Optional[List[StepCreate]] = None
    tags: Optional[List[str]] = None

# ==========================================
# RECIPE SCHEMAS 
# ==========================================
class RecipeResponse(RecipeBase):
    id: int
    user_id: int
    created_at: datetime

    # Bewertungs-Metadaten
    average_rating: float = 0.0
    rating_count: int = 0

    # Favoriten-Status: true wenn der aktuelle User dieses Rezept favorisiert hat.
    # Bei anonymen Zugriffen immer false.
    is_favorited: bool = False

    ingredients: List[IngredientResponse] = []
    steps: List[StepResponse] = []
    tags: List[TagResponse] = []

    model_config = {"from_attributes": True}


# ==========================================
# RATING SCHEMAS
# ==========================================
class RatingCreate(BaseModel):
    recipe_id: int
    rating: int = Field(..., ge=1, le=5) # Stellt sicher, dass nur 1 bis 5 Sterne erlaubt sind

class RatingResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    rating: int
    model_config = {"from_attributes": True}


# ==========================================
# GROUP SCHEMAS (Neu für Phase 2)
# ==========================================
class GroupCreate(BaseModel):
    name: str

class GroupResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    model_config = {"from_attributes": True}


# ==========================================
# SHOPPING LIST SCHEMAS
# ==========================================
class ShoppingListItemBase(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None


class ShoppingListItemCreate(ShoppingListItemBase):
    """Manuelles Hinzufügen eines Einkaufslisten-Items."""
    pass


class ShoppingListItemUpdate(BaseModel):
    """Patch — z.B. zum Abhaken oder Mengen ändern."""
    name: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    is_checked: Optional[bool] = None


class ShoppingListItemResponse(ShoppingListItemBase):
    id: int
    user_id: int
    category: Optional[str] = None
    is_checked: bool = False
    recipe_id: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class AddFromRecipeRequest(BaseModel):
    """Skalierungsfaktor: 1.0 = Original, 2.0 = doppelte Portionen, usw."""
    scale: float = Field(default=1.0, gt=0)


# ==========================================
# AUTH SCHEMAS (Neu eingefügt für Phase 1)
# ==========================================
class TokenData(BaseModel):
    username: Optional[str] = None
