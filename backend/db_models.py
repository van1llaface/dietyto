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
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


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
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    verify_code = Column(String, nullable=True)          # 6-digit email verification code
    reset_code = Column(String, nullable=True)           # 6-digit password reset code
    auth_token = Column(String, nullable=True, index=True)  # session token

    # Relationship: one user has one profile
    profile = relationship("UserProfileDB", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # Relationship: one user has many meal plan slots
    meal_plans = relationship("MealPlanDB", back_populates="user", cascade="all, delete-orphan")


class MealPlanDB(Base):
    """
    Stores a saved meal plan — one row per day-meal slot.
    Now linked to a user.
    """
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day = Column(String, nullable=False)
    meal = Column(String, nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)

    user = relationship("UserDB", back_populates="meal_plans")


class UserProfileDB(Base):
    """
    Stores user profile for calorie calculation.
    Now linked to a user.
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    gender = Column(String, default="male")
    age = Column(Integer, default=30)
    weight_kg = Column(Float, default=70)
    height_cm = Column(Float, default=170)
    activity_level = Column(String, default="moderate")
    intermittent_fasting = Column(String, default="none")
    exclude_allergens = Column(Text, default="[]")

    user = relationship("UserDB", back_populates="profile")


class RecipeDB(Base):
    """
    The 'recipes' table in the database.

    __tablename__ = the actual table name in SQLite
    Each Column(...) = one column in the table
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    servings = Column(Integer, default=1)
    prep_time_min = Column(Integer, default=0)
    calories = Column(Integer, default=0)

    # Macros stored directly on recipe (simpler than separate table)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    fiber_g = Column(Float, default=0)

    # Nutrients stored as JSON string (flexible, no extra table needed)
    # We'll convert to/from dict in Python
    nutrients_json = Column(Text, default="{}")

    # Instructions stored as JSON array string
    instructions_json = Column(Text, default="[]")

    # Health benefits stored as JSON array string
    health_benefits_json = Column(Text, default="[]")

    # Allergens stored as JSON array string
    allergens_json = Column(Text, default="[]")

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

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    # Relationship back to recipe
    recipe = relationship("RecipeDB", back_populates="ingredients")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "amount": self.amount,
            "unit": self.unit,
        }
