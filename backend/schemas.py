from pydantic import BaseModel


# --- Auth-Schemas ---

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

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


class Token(BaseModel):
    access_token: str
    token_type: str


# TODO: Fügt hier eure eigenen Schemas hinzu
# class ItemCreate(BaseModel):
#     name: str
#     price: int
#
# class ItemResponse(BaseModel):
#     id: int
#     name: str
#     price: int
#     model_config = {"from_attributes": True}
