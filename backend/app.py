import json
import secrets
import random
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from models import (
    RecipeCreate, RecipeResponse,
    WeekPlanCreate, WeekPlanResponse,
    DayPlan, GroceryList, GroceryItem, Macros,
    UserProfile, UserProfileResponse,
    MealSlot, SavedMealPlan,
    SignUpRequest, VerifyEmailRequest, LoginRequest, LoginResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from database import engine, get_db, Base
from db_models import RecipeDB, IngredientDB, MealPlanDB, UserProfileDB, UserDB

# Create all tables on startup (if they don't exist)
Base.metadata.create_all(bind=engine)

# Create a FastAPI application
app = FastAPI(title="Dietyto API", description="Eat for longevity. Plan your week with Dietyto.")

# Allow the frontend to talk to the backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Authentication helpers
# ──────────────────────────────────────────────

def get_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> UserDB:
    """
    Dependency that extracts the logged-in user from the request.

    HOW IT WORKS:
    The frontend sends a header like: Authorization: Bearer abc123
    We take "abc123", look it up in the users table, and return the user.
    If the token is missing or invalid → 401 Unauthorized.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in")

    token = authorization.split(" ", 1)[1]
    user = db.query(UserDB).filter(UserDB.auth_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def generate_code() -> str:
    """Generate a random 6-digit verification code."""
    return str(random.randint(100000, 999999))


# ──────────────────────────────────────────────
# Auth endpoints: signup, verify, login, reset
# ──────────────────────────────────────────────

@app.post("/auth/signup")
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    """
    Create a new account.

    Steps:
    1. Check if username/email already taken
    2. Hash the password (NEVER store plain text!)
    3. Generate a 6-digit verification code
    4. Save user to database
    5. Print code to console (in production you'd email it)
    """
    if db.query(UserDB).filter(UserDB.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(UserDB).filter(UserDB.email == req.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    code = generate_code()
    user = UserDB(
        username=req.username,
        email=req.email.lower(),
        password_hash=bcrypt.hash(req.password),
        verify_code=code,
    )
    db.add(user)
    db.commit()

    # In real app: send email. For now: print to server console.
    print(f"\n{'='*50}")
    print(f"  EMAIL VERIFICATION CODE for {req.email}")
    print(f"  Code: {code}")
    print(f"{'='*50}\n")

    return {"message": "Account created! Check your email for verification code.", "dev_code": code}


@app.post("/auth/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify email with the 6-digit code."""
    user = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if user.email_verified:
        return {"message": "Email already verified. You can log in."}
    if user.verify_code != req.code:
        raise HTTPException(status_code=400, detail="Incorrect verification code")

    user.email_verified = True
    user.verify_code = None
    db.commit()
    return {"message": "Email verified! You can now log in."}


@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Log in and receive a token.

    The token is like a wristband at a festival — show it to get access.
    The frontend stores it and sends it with every request.
    """
    user = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    if not user or not bcrypt.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Check your inbox for the code.")

    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    user.auth_token = token
    db.commit()

    return LoginResponse(token=token, username=user.username, message="Welcome back!")


@app.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send a password reset code."""
    user = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    if not user:
        # Don't reveal if email exists — security best practice
        return {"message": "If that email exists, a reset code has been sent."}

    code = generate_code()
    user.reset_code = code
    db.commit()

    print(f"\n{'='*50}")
    print(f"  PASSWORD RESET CODE for {req.email}")
    print(f"  Code: {code}")
    print(f"{'='*50}\n")

    return {"message": "If that email exists, a reset code has been sent.", "dev_code": code}


@app.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with the code."""
    user = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    if not user or user.reset_code != req.code:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    user.password_hash = bcrypt.hash(req.new_password)
    user.reset_code = None
    user.auth_token = None   # Log out all sessions for safety
    db.commit()
    return {"message": "Password reset! You can now log in with your new password."}


@app.get("/auth/me")
def get_me(user: UserDB = Depends(get_current_user)):
    """Returns the currently logged-in user's info."""
    return {"username": user.username, "email": user.email}


# ──────────────────────────────────────────────
# Helper: load recipe from DB and convert to dict
# ──────────────────────────────────────────────

def get_recipe_dict(db: Session, recipe_id: int) -> dict | None:
    recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if not recipe:
        return None
    return recipe.to_dict()


def get_all_recipes(db: Session) -> list[dict]:
    recipes = db.query(RecipeDB).all()
    return [r.to_dict() for r in recipes]


# ──────────────────────────────────────────────
# GET endpoints
# ──────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Welcome to Dietyto — eat for longevity!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/recipes", response_model=list[RecipeResponse])
def get_recipes(
    meal_type: str | None = None,
    category: str | None = None,
    exclude_allergens: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Get all recipes from the DATABASE — optionally filter.

    New concept: Depends(get_db)
    This tells FastAPI: "before running this function, call get_db()
    to get a database session, and pass it as the 'db' parameter."
    After the function finishes, the session is automatically closed.
    """
    query = db.query(RecipeDB)

    if meal_type:
        query = query.filter(RecipeDB.meal_type == meal_type)
    if category:
        query = query.filter(RecipeDB.category == category)

    results = [r.to_dict() for r in query.all()]

    if exclude_allergens:
        excluded = [a.strip().lower() for a in exclude_allergens.split(",")]
        results = [
            r for r in results
            if not any(a.lower() in excluded for a in r.get("allergens", []))
        ]

    return results


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a single recipe by ID from the database."""
    recipe = get_recipe_dict(db, recipe_id)
    if not recipe:
        return {"error": "Recipe not found"}
    return recipe


# ──────────────────────────────────────────────
# POST endpoints
# ──────────────────────────────────────────────

@app.post("/recipes", response_model=RecipeResponse)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """
    Create a new recipe and save it to the DATABASE.
    Now it persists — restart the server and it's still there!
    """
    db_recipe = RecipeDB(
        name=recipe.name,
        description=recipe.description,
        category=recipe.category,
        meal_type=recipe.meal_type,
        servings=recipe.servings,
        prep_time_min=recipe.prep_time_min,
        calories=recipe.calories,
        protein_g=recipe.macros.protein_g,
        carbs_g=recipe.macros.carbs_g,
        fat_g=recipe.macros.fat_g,
        fiber_g=recipe.macros.fiber_g,
        nutrients_json=json.dumps(recipe.nutrients.model_dump(exclude_none=True)),
        instructions_json=json.dumps(recipe.instructions),
        health_benefits_json=json.dumps(recipe.health_benefits),
        allergens_json=json.dumps(recipe.allergens),
    )

    for ing in recipe.ingredients:
        db_recipe.ingredients.append(
            IngredientDB(name=ing.name, amount=ing.amount, unit=ing.unit)
        )

    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.to_dict()


@app.post("/meal-plan/grocery-list", response_model=GroceryList)
def generate_grocery_list(week_plan: WeekPlanCreate, db: Session = Depends(get_db)):
    """Send a week plan, get a combined grocery list from the database."""

    TO_ML = {"ml": 1, "tbsp": 15, "tsp": 5, "cups": 240}
    TO_G = {"g": 1, "kg": 1000}

    def normalize(amount: float, unit: str) -> tuple[float, str]:
        unit_lower = unit.lower()
        if unit_lower in TO_ML:
            return amount * TO_ML[unit_lower], "ml"
        if unit_lower in TO_G:
            return amount * TO_G[unit_lower], "g"
        return amount, unit_lower

    def friendly_unit(amount: float, unit: str) -> tuple[float, str]:
        if unit == "ml" and amount >= 1000:
            return round(amount / 1000, 2), "L"
        if unit == "g" and amount >= 1000:
            return round(amount / 1000, 2), "kg"
        return round(amount, 1), unit

    recipe_ids = []
    for day in week_plan.days:
        recipe_ids.extend([day.breakfast_id, day.lunch_id, day.dinner_id])
        if day.snack_id:
            recipe_ids.append(day.snack_id)

    grocery: dict[str, dict] = {}

    for rid in recipe_ids:
        recipe = get_recipe_dict(db, rid)
        if not recipe:
            continue

        servings = recipe.get("servings", 1)

        for ing in recipe["ingredients"]:
            per_serving = ing["amount"] / servings
            normalized_amount, base_unit = normalize(per_serving, ing["unit"])
            key = ing["name"].lower()

            if key in grocery:
                if grocery[key]["unit"] == base_unit:
                    grocery[key]["total_amount"] += normalized_amount
                else:
                    alt_key = f"{key} ({base_unit})"
                    if alt_key in grocery:
                        grocery[alt_key]["total_amount"] += normalized_amount
                    else:
                        grocery[alt_key] = {
                            "name": ing["name"],
                            "total_amount": normalized_amount,
                            "unit": base_unit,
                        }
            else:
                grocery[key] = {
                    "name": ing["name"],
                    "total_amount": normalized_amount,
                    "unit": base_unit,
                }

    items = []
    for item in grocery.values():
        amount, unit = friendly_unit(item["total_amount"], item["unit"])
        items.append({"name": item["name"], "total_amount": amount, "unit": unit})

    items.sort(key=lambda x: x["name"])
    return GroceryList(items=items)


@app.post("/meal-plan/summary", response_model=WeekPlanResponse)
def get_meal_plan_summary(week_plan: WeekPlanCreate, db: Session = Depends(get_db)):
    """Get total calories, macros, and allergen warnings for a week plan."""
    total_cal = 0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    total_fiber = 0.0

    for day in week_plan.days:
        day_ids = [day.breakfast_id, day.lunch_id, day.dinner_id]
        if day.snack_id:
            day_ids.append(day.snack_id)

        for rid in day_ids:
            recipe = get_recipe_dict(db, rid)
            if not recipe:
                continue
            total_cal += recipe["calories"]
            total_protein += recipe["macros"]["protein_g"]
            total_carbs += recipe["macros"]["carbs_g"]
            total_fat += recipe["macros"]["fat_g"]
            total_fiber += recipe["macros"]["fiber_g"]

    allergen_warnings = []
    if week_plan.exclude_allergens:
        excluded = [a.lower() for a in week_plan.exclude_allergens]
        for day in week_plan.days:
            day_meals = [
                ("breakfast", day.breakfast_id),
                ("lunch", day.lunch_id),
                ("dinner", day.dinner_id),
            ]
            if day.snack_id:
                day_meals.append(("snack", day.snack_id))

            for meal_name, rid in day_meals:
                recipe = get_recipe_dict(db, rid)
                if not recipe:
                    continue
                found = [a for a in recipe.get("allergens", []) if a.lower() in excluded]
                if found:
                    allergen_warnings.append(
                        f"{day.day.capitalize()} {meal_name} ({recipe['name']}) contains: {', '.join(found)}"
                    )

    return WeekPlanResponse(
        days=week_plan.days,
        total_calories=total_cal,
        total_macros=Macros(
            protein_g=total_protein,
            carbs_g=total_carbs,
            fat_g=total_fat,
            fiber_g=total_fiber,
        ),
        allergen_warnings=allergen_warnings,
    )


# ──────────────────────────────────────────────
# Meal Plan save/load
# ──────────────────────────────────────────────

@app.get("/meal-plan/saved", response_model=SavedMealPlan)
def load_meal_plan(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Load the saved meal plan for the logged-in user."""
    rows = db.query(MealPlanDB).filter(MealPlanDB.user_id == user.id).all()
    slots = [MealSlot(day=r.day, meal=r.meal, recipe_id=r.recipe_id) for r in rows]
    return SavedMealPlan(slots=slots)


@app.put("/meal-plan/saved")
def save_meal_plan(plan: SavedMealPlan, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Save (replace) the entire meal plan for the logged-in user.
    """
    db.query(MealPlanDB).filter(MealPlanDB.user_id == user.id).delete()
    for slot in plan.slots:
        db.add(MealPlanDB(user_id=user.id, day=slot.day, meal=slot.meal, recipe_id=slot.recipe_id))
    db.commit()
    return {"message": "Meal plan saved", "slots": len(plan.slots)}


# ──────────────────────────────────────────────
# User Profile & Calorie Calculator
# ──────────────────────────────────────────────

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

IF_LABELS = {
    "none": "No fasting",
    "16_8": "16:8 (8h eating window)",
    "18_6": "18:6 (6h eating window)",
    "20_4": "20:4 (4h eating window)",
}


def calculate_calories(profile: UserProfile) -> dict:
    """
    Mifflin-St Jeor equation for BMR then multiply by activity level.

    Male:   BMR = 10 × weight(kg) + 6.25 × height(cm) – 5 × age + 5
    Female: BMR = 10 × weight(kg) + 6.25 × height(cm) – 5 × age – 161
    """
    if profile.gender == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161

    factor = ACTIVITY_FACTORS.get(profile.activity_level, 1.55)
    daily_cal = int(bmr * factor)

    # Macro split: 30% protein, 40% carbs, 30% fat
    protein_g = int((daily_cal * 0.30) / 4)   # 4 cal per gram protein
    carbs_g = int((daily_cal * 0.40) / 4)     # 4 cal per gram carbs
    fat_g = int((daily_cal * 0.30) / 9)       # 9 cal per gram fat

    return {
        "daily_calories": daily_cal,
        "protein_target_g": protein_g,
        "carbs_target_g": carbs_g,
        "fat_target_g": fat_g,
    }


@app.get("/profile", response_model=UserProfileResponse)
def get_profile(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Load user profile (creates default if none exists)."""
    row = db.query(UserProfileDB).filter(UserProfileDB.user_id == user.id).first()
    if not row:
        row = UserProfileDB(user_id=user.id)
        db.add(row)
        db.commit()
        db.refresh(row)

    profile = UserProfile(
        gender=row.gender,
        age=row.age,
        weight_kg=row.weight_kg,
        height_cm=row.height_cm,
        activity_level=row.activity_level,
        intermittent_fasting=row.intermittent_fasting,
        exclude_allergens=json.loads(row.exclude_allergens) if row.exclude_allergens else [],
    )
    targets = calculate_calories(profile)
    return UserProfileResponse(**profile.model_dump(), **targets)


@app.put("/profile", response_model=UserProfileResponse)
def update_profile(profile: UserProfile, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile and recalculate targets."""
    row = db.query(UserProfileDB).filter(UserProfileDB.user_id == user.id).first()
    if not row:
        row = UserProfileDB(user_id=user.id)
        db.add(row)

    row.gender = profile.gender
    row.age = profile.age
    row.weight_kg = profile.weight_kg
    row.height_cm = profile.height_cm
    row.activity_level = profile.activity_level
    row.intermittent_fasting = profile.intermittent_fasting
    row.exclude_allergens = json.dumps(profile.exclude_allergens)
    db.commit()

    targets = calculate_calories(profile)
    return UserProfileResponse(**profile.model_dump(), **targets)


# This lets you run the file directly with: python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
