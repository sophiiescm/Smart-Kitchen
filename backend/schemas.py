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
    is_public: bool = False

class RecipeCreate(RecipeBase):
    # Beim Erstellen schickt das Frontend direkt Listen für Zutaten und Schritte mit
    ingredients: List[IngredientCreate] = []
    steps: List[StepCreate] = []

class RecipeResponse(RecipeBase):
    id: int
    user_id: int
    created_at: datetime
    
    # Beim Abrufen liefert das Backend die fertigen Listen direkt mit aus
    ingredients: List[IngredientResponse] = []
    steps: List[StepResponse] = []
    
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
# AUTH SCHEMAS (Neu eingefügt für Phase 1)
# ==========================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
