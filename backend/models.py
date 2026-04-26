"""
Models = The shape of your data.

Pydantic models define WHAT your data looks like.
If someone sends data that doesn't match → automatic error.

We build models like LEGO — small pieces that combine:
  Ingredient → Recipe → DayPlan → WeekPlan → GroceryList
"""

from pydantic import BaseModel, field_validator
import re


# ──────────────────────────────────────────────
# Building block: A single ingredient with quantity
# ──────────────────────────────────────────────

class Ingredient(BaseModel):
    """
    One ingredient with its exact quantity.

    Examples:
        {"name": "salmon fillet", "amount": 200, "unit": "g"}
        {"name": "eggs", "amount": 2, "unit": "pcs"}
        {"name": "olive oil", "amount": 1, "unit": "tbsp"}
    """
    name: str
    amount: float
    unit: str           # "g", "ml", "pcs", "tbsp", "tsp", "cups"


# ──────────────────────────────────────────────
# Macronutrients (protein, carbs, fat, fiber)
# ──────────────────────────────────────────────

class Macros(BaseModel):
    """
    Macronutrients — the big ones your body uses for energy.

    All values are per serving, in grams.
    """
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float


# ──────────────────────────────────────────────
# Micronutrients (vitamins, minerals — the longevity ones)
# ──────────────────────────────────────────────

class Nutrients(BaseModel):
    """
    Key micronutrients relevant to longevity.

    All optional — fill in what you know, leave rest as None.
    Values are per serving.
    """
    vitamin_c_mg: float | None = None
    vitamin_d_mcg: float | None = None
    vitamin_b12_mcg: float | None = None
    omega_3_g: float | None = None
    iron_mg: float | None = None
    calcium_mg: float | None = None
    magnesium_mg: float | None = None
    potassium_mg: float | None = None
    zinc_mg: float | None = None


# ──────────────────────────────────────────────
# Recipe — the main model
# ──────────────────────────────────────────────

class Recipe(BaseModel):
    """
    A complete recipe with nutrition info.
    """
    name: str
    description: str
    category: str               # "anti-inflammatory", "heart-healthy", etc.
    meal_type: str              # "breakfast", "lunch", "dinner", "snack"
    servings: int
    prep_time_min: int
    calories: int               # per serving
    ingredients: list[Ingredient]
    instructions: list[str]     # step-by-step
    macros: Macros
    nutrients: Nutrients
    health_benefits: list[str]
    allergens: list[str] = []   # e.g. ["gluten", "dairy", "nuts", "fish", "soy"]


class RecipeCreate(Recipe):
    """What the user sends to create a recipe (no id)."""
    pass


class RecipeResponse(Recipe):
    """What the server returns (includes id)."""
    id: int


# ──────────────────────────────────────────────
# Meal Plan — a week of meals
# ──────────────────────────────────────────────

class DayPlan(BaseModel):
    """
    One day of eating: breakfast, lunch, dinner, and optional snack.
    Each field is a recipe ID.
    """
    day: str                    # "monday", "tuesday", etc.
    breakfast_id: int
    lunch_id: int
    dinner_id: int
    snack_id: int | None = None


class WeekPlanCreate(BaseModel):
    """User sends 7 days of meal assignments."""
    days: list[DayPlan]
    exclude_allergens: list[str] = []  # e.g. ["nuts", "dairy"] — warn if plan contains these


class WeekPlanResponse(BaseModel):
    """Server returns the plan with full recipe details and totals."""
    days: list[DayPlan]
    total_calories: int
    total_macros: Macros
    allergen_warnings: list[str] = []  # e.g. ["Monday dinner contains: fish"]


# ──────────────────────────────────────────────
# Grocery List — generated from a week plan
# ──────────────────────────────────────────────

class GroceryItem(BaseModel):
    """
    One item on the shopping list.
    Quantities are combined across all recipes in the week.

    Example: if 3 recipes use salmon (200g, 150g, 200g),
    the grocery list shows: salmon — 550g
    """
    name: str
    total_amount: float
    unit: str


class GroceryList(BaseModel):
    """The full shopping list for a week."""
    items: list[GroceryItem]


# ──────────────────────────────────────────────
# User Profile — for calorie calculation
# ──────────────────────────────────────────────

class UserProfile(BaseModel):
    """
    User's body stats + preferences for calorie targets.

    Calorie calculation uses the Mifflin-St Jeor equation:
    - Male:   10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161 + 5
    - Female: 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

    Then multiplied by activity factor.
    """
    gender: str = "male"                      # "male" or "female"
    age: int = 30
    weight_kg: float = 70.0
    height_cm: float = 170.0
    activity_level: str = "moderate"           # sedentary, light, moderate, active, very_active
    intermittent_fasting: str = "none"         # none, 16_8, 18_6, 20_4
    exclude_allergens: list[str] = []


class UserProfileResponse(UserProfile):
    """Returned profile includes calculated calorie target."""
    daily_calories: int
    protein_target_g: int
    carbs_target_g: int
    fat_target_g: int


# ──────────────────────────────────────────────
# Saved Meal Plan slot
# ──────────────────────────────────────────────

class MealSlot(BaseModel):
    """One slot in the meal plan (e.g. Monday breakfast = recipe 3)."""
    day: str
    meal: str
    recipe_id: int


class SavedMealPlan(BaseModel):
    """All meal slots for the saved plan."""
    slots: list[MealSlot]


# ──────────────────────────────────────────────
# Authentication models
# ──────────────────────────────────────────────

class SignUpRequest(BaseModel):
    """Data needed to create a new account."""
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v

    @field_validator("email")
    @classmethod
    def email_valid(cls, v):
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class VerifyEmailRequest(BaseModel):
    """6-digit code to verify email after signup."""
    email: str
    code: str


class LoginRequest(BaseModel):
    """Login with email and password."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Returned after successful login."""
    token: str
    username: str
    message: str


class ForgotPasswordRequest(BaseModel):
    """Request a password reset code."""
    email: str


class ResetPasswordRequest(BaseModel):
    """Reset password with the code from email."""
    email: str
    code: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
