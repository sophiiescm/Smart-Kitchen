from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Float, DateTime, Table, BigInteger, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# 7. group_recipes (Verknüpfung Rezepte <-> Gruppen) [cite: 39, 40]
group_recipes = Table(
    'group_recipes', Base.metadata,
    Column('group_id', BigInteger, ForeignKey('groups.id'), primary_key=True),
    Column('recipe_id', BigInteger, ForeignKey('recipes.id'), primary_key=True)
)

# 1. users [cite: 2, 3]
class User(Base):
    """Benutzertabelle – hier könnt ihr weitere Felder ergänzen."""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(255),unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Verknüpfungen (Relationships)
    recipes = relationship("Recipe", back_populates="owner")
    ratings = relationship("RecipeRating", back_populates="user")
    owned_groups = relationship("Group", back_populates="owner")

# 2. recipes [cite: 4, 5]
class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    prep_time_minutes = Column(Integer)
    servings = Column(Integer)
    difficulty = Column(String(50)) # ENUM/VARCHAR
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Verknüpfungen (Relationships)
    owner = relationship("User", back_populates="recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    steps = relationship("RecipeStep", back_populates="recipe")
    ratings = relationship("RecipeRating", back_populates="recipe")

# 3. recipe_ingredients [cite: 6, 7]
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipe_id = Column(BigInteger, ForeignKey("recipes.id"))
    name = Column(String(255), nullable=False)
    amount = Column(Float)
    unit = Column(String(50))

    recipe = relationship("Recipe", back_populates="ingredients")

# 4. recipe_steps [cite: 8, 9]
class RecipeStep(Base):
    __tablename__ = "recipe_steps"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipe_id = Column(BigInteger, ForeignKey("recipes.id"))
    step_number = Column(Integer)
    instruction = Column(Text, nullable=False) # z.B. "Den Ofen auf 180°C vorheizen."

    recipe = relationship("Recipe", back_populates="steps")

# 5. recipe_ratings [cite: 10, 11-30]
class RecipeRating(Base):
    __tablename__ = "recipe_ratings"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipe_id = Column(BigInteger, ForeignKey("recipes.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)

    recipe = relationship("Recipe", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

# 6. groups [cite: 35-38]
class Group(Base):
    __tablename__ = "groups"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(BigInteger, ForeignKey("users.id"))

    owner = relationship("User", back_populates="owned_groups")
    recipes = relationship("Recipe", secondary=group_recipes)
