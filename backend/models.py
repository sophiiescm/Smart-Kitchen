from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Basisklasse für das SQLAlchemy ORM
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    # Passwort-Hash wird später von Person 2 befüllt
    hashed_password = Column(String(255), nullable=False)

    # Beziehungen zu Rezepten und Bewertungen
    recipes = relationship("Recipe", back_populates="owner")
    ratings = relationship("Rating", back_populates="user")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    # Zutaten als Text (z.B. kommagetrennt)
    ingredients = Column(Text, nullable=False)
    
    # Fremdschlüssel: Welcher User hat das Rezept erstellt?
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="recipes")
    ratings = relationship("Rating", back_populates="recipe")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    stars = Column(Integer, nullable=False) # 1 bis 5 Sterne
    
    # Fremdschlüssel für die Verknüpfung
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    user = relationship("User", back_populates="ratings")
    recipe = relationship("Recipe", back_populates="ratings")