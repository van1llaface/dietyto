"""
db_models.py — Database table definitions using SQLAlchemy.

WHY SEPARATE FROM models.py?
----------------------------
- models.py (Pydantic) = data VALIDATION (what goes in/out of the API)
- db_models.py (SQLAlchemy) = data STORAGE (how it's saved in the database)

They look similar but serve different purposes:
- Pydantic: "Is this data valid?"
- SQLAlchemy: "How do I store this in a table?"

KEY CONCEPT — Relational Database:
Instead of one big recipe dict with nested ingredients, we split into TABLES:
- recipes table: name, category, calories, etc.
- ingredients table: each row is one ingredient, linked to a recipe
- recipe_allergens table: links recipes to their allergens

Why? Because databases work with flat rows, not nested objects.
The "link" between tables is called a FOREIGN KEY.
"""

import json
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
from datetime import datetime, timezone


class HouseholdDB(Base):
    """
    A household — two people who cook and eat together.
    One person creates it, the other joins with the invite code.
    """
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invite_code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    members = relationship("UserDB", back_populates="household")


class UserDB(Base):
    """
    The 'users' table — stores accounts.

    KEY SECURITY CONCEPTS:
    - password_hash: we NEVER store the actual password. Instead we store
      a "hash" — a scrambled version. When the user logs in, we hash what
      they typed and compare the hashes. Even if someone steals the database,
      they can't reverse the hash back to the password.
    - email_verified: must be True before the user can log in.
    - verify_code: a 6-digit code sent to their email (printed to console
      during local development).
    - auth_token: a random string that acts like a "key card" — the frontend
      sends it with every request to prove the user is logged in.

    NEW CONCEPT — Mapped[]:
    Instead of Column(String), we write: name: Mapped[str] = mapped_column(String)
    This tells both SQLAlchemy AND the type checker what type each field is.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verify_code: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    reset_code: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    auth_token: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True, default=None)
    token_created_at: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    role: Mapped[str] = mapped_column(String, default="user")  # "admin" or "user"
    household_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("households.id"), nullable=True, default=None)

    household = relationship("HouseholdDB", back_populates="members")
    profile = relationship("UserProfileDB", back_populates="user", uselist=False, cascade="all, delete-orphan")
    meal_plans = relationship("MealPlanDB", back_populates="user", cascade="all, delete-orphan")


class MealPlanDB(Base):
    """
    Stores a saved meal plan — one row per day-meal slot.
    Now linked to a user.
    """
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    day: Mapped[str] = mapped_column(String, nullable=False)
    meal: Mapped[str] = mapped_column(String, nullable=False)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    servings: Mapped[float] = mapped_column(Float, default=1.0)

    user = relationship("UserDB", back_populates="meal_plans")


class UserProfileDB(Base):
    """
    Stores user profile for calorie calculation.
    Now linked to a user.
    """
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    gender: Mapped[str] = mapped_column(String, default="male")
    age: Mapped[int] = mapped_column(Integer, default=30)
    weight_kg: Mapped[float] = mapped_column(Float, default=70)
    target_weight_kg: Mapped[float] = mapped_column(Float, default=70)
    height_cm: Mapped[float] = mapped_column(Float, default=170)
    activity_level: Mapped[str] = mapped_column(String, default="moderate")
    weight_rate: Mapped[str] = mapped_column(String, default="maintain")
    intermittent_fasting: Mapped[str] = mapped_column(String, default="none")
    exclude_allergens: Mapped[str] = mapped_column(Text, default="[]")

    user = relationship("UserDB", back_populates="profile")


class WeightLogDB(Base):
    """Tracks weight over time for progress graphs."""
    __tablename__ = "weight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    user = relationship("UserDB")


class MealRatingDB(Base):
    """Stores user ratings for recipes (1-5 stars). Ratings 1-2 exclude from future plans."""
    __tablename__ = "meal_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    rated_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    user = relationship("UserDB")
    recipe = relationship("RecipeDB")


class RecipeDB(Base):
    """
    The 'recipes' table in the database.

    __tablename__ = the actual table name in SQLite
    Each mapped_column(...) = one column in the table
    """
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, default=1)
    prep_time_min: Mapped[int] = mapped_column(Integer, default=0)
    calories: Mapped[int] = mapped_column(Integer, default=0)

    protein_g: Mapped[float] = mapped_column(Float, default=0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0)
    fat_g: Mapped[float] = mapped_column(Float, default=0)
    fiber_g: Mapped[float] = mapped_column(Float, default=0)

    nutrients_json: Mapped[str] = mapped_column(Text, default="{}")
    instructions_json: Mapped[str] = mapped_column(Text, default="[]")
    health_benefits_json: Mapped[str] = mapped_column(Text, default="[]")
    allergens_json: Mapped[str] = mapped_column(Text, default="[]")

    author: Mapped[str] = mapped_column(String, default="")
    image_url: Mapped[str] = mapped_column(String, default="")

    # Relationship: one recipe has many ingredients
    # This tells SQLAlchemy: "when I load a recipe, also load its ingredients"
    ingredients = relationship("IngredientDB", back_populates="recipe", cascade="all, delete-orphan")

    # Helper methods to convert JSON fields
    @property
    def nutrients(self) -> dict:
        return json.loads(self.nutrients_json) if self.nutrients_json else {}

    @property
    def instructions(self) -> list:
        return json.loads(self.instructions_json) if self.instructions_json else []

    @property
    def health_benefits(self) -> list:
        return json.loads(self.health_benefits_json) if self.health_benefits_json else []

    @property
    def allergens(self) -> list:
        return json.loads(self.allergens_json) if self.allergens_json else []

    def to_dict(self) -> dict:
        """Convert database row to the dict format our API expects."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "meal_type": self.meal_type,
            "servings": self.servings,
            "prep_time_min": self.prep_time_min,
            "calories": self.calories,
            "ingredients": [ing.to_dict() for ing in self.ingredients],
            "instructions": self.instructions,
            "macros": {
                "protein_g": self.protein_g,
                "carbs_g": self.carbs_g,
                "fat_g": self.fat_g,
                "fiber_g": self.fiber_g,
            },
            "nutrients": self.nutrients,
            "health_benefits": self.health_benefits,
            "allergens": self.allergens,
            "author": self.author,
            "image_url": self.image_url,
        }


class IngredientDB(Base):
    """
    The 'ingredients' table.

    Each row is ONE ingredient for ONE recipe.
    The recipe_id column links it back to the recipes table (foreign key).

    Example rows:
    | id | recipe_id | name   | amount | unit |
    |----|-----------|--------|--------|------|
    | 1  | 1         | kale   | 100    | g    |
    | 2  | 1         | quinoa | 150    | g    |
    | 3  | 2         | banana | 1      | pcs  |
    """
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship back to recipe
    recipe = relationship("RecipeDB", back_populates="ingredients")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "amount": self.amount,
            "unit": self.unit,
        }
