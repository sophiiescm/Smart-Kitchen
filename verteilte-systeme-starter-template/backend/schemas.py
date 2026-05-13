from pydantic import BaseModel, EmailStr, Field, field_validator


# --- Auth-Schemas ---

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr # Prüft automatisch auf @ und gültige Domain
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def password_must_contain_number(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Passwort muss mindestens eine Zahl enthalten')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

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
