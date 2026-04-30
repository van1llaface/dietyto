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
    HouseholdCreate, HouseholdJoin, HouseholdResponse, HouseholdMember,
)
from database import engine, get_db, Base
from datetime import datetime, timezone, timedelta
from db_models import RecipeDB, IngredientDB, MealPlanDB, UserProfileDB, UserDB, HouseholdDB, WeightLogDB, MealRatingDB

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

    # Check token expiration (7 days)
    if user.token_created_at:
        try:
            created = datetime.fromisoformat(user.token_created_at)
            if (datetime.now(timezone.utc) - created) > timedelta(days=7):
                user.auth_token = None
                user.token_created_at = None
                db.commit()
                raise HTTPException(status_code=401, detail="Token expired, please log in again")
        except (ValueError, TypeError):
            pass

    return user


def require_admin(
    user: UserDB = Depends(get_current_user),
) -> UserDB:
    """Dependency that ensures the user is an admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def generate_code() -> str:
    """Generate a random 6-digit verification code (cryptographically secure)."""
    return str(secrets.randbelow(900000) + 100000)


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

    # In production: send code via email only. Console log for dev.
    return {"message": "Account created! Check your email for verification code."}


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
    # Allow login with username or email
    identifier = req.email.strip()
    user = db.query(UserDB).filter(
        (UserDB.email == identifier.lower()) | (UserDB.username == identifier)
    ).first()
    if not user or not bcrypt.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username/email or password")

    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Check your inbox for the code.")

    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    user.auth_token = token
    user.token_created_at = datetime.now(timezone.utc).isoformat()
    db.commit()

    return LoginResponse(token=token, username=user.username, role=user.role, message="Welcome back!")


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

    return {"message": "If that email exists, a reset code has been sent."}


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
    data = {"username": user.username, "email": user.email, "role": user.role, "household_id": user.household_id}
    return data


# ──────────────────────────────────────────────
# Household endpoints (couples feature)
# ──────────────────────────────────────────────

def _household_response(household: HouseholdDB) -> HouseholdResponse:
    """Convert a HouseholdDB row to the API response."""
    members = [HouseholdMember(id=m.id, username=m.username) for m in household.members]
    return HouseholdResponse(id=household.id, invite_code=household.invite_code, members=members)


@app.post("/household", response_model=HouseholdResponse)
def create_household(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new household. The current user becomes the first member."""
    if user.household_id:
        raise HTTPException(400, "You are already in a household. Leave first.")
    invite_code = secrets.token_urlsafe(4).upper()[:6]
    # Ensure uniqueness
    while db.query(HouseholdDB).filter(HouseholdDB.invite_code == invite_code).first():
        invite_code = secrets.token_urlsafe(4).upper()[:6]
    household = HouseholdDB(invite_code=invite_code)
    db.add(household)
    db.flush()
    user.household_id = household.id
    db.commit()
    db.refresh(household)
    return _household_response(household)


@app.post("/household/join", response_model=HouseholdResponse)
def join_household(req: HouseholdJoin, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Join an existing household with an invite code."""
    if user.household_id:
        raise HTTPException(400, "You are already in a household. Leave first.")
    household = db.query(HouseholdDB).filter(HouseholdDB.invite_code == req.invite_code.upper()).first()
    if not household:
        raise HTTPException(404, "Invalid invite code")
    if len(household.members) >= 2:
        raise HTTPException(400, "Household is full (max 2 members)")
    user.household_id = household.id
    db.commit()
    db.refresh(household)
    return _household_response(household)


@app.get("/household", response_model=HouseholdResponse)
def get_household(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current user's household info."""
    if not user.household_id:
        raise HTTPException(404, "You are not in a household")
    household = db.query(HouseholdDB).filter(HouseholdDB.id == user.household_id).first()
    return _household_response(household)


@app.delete("/household/leave")
def leave_household(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Leave the current household. If last member, household is deleted."""
    if not user.household_id:
        raise HTTPException(400, "You are not in a household")
    household = db.query(HouseholdDB).filter(HouseholdDB.id == user.household_id).first()
    user.household_id = None
    db.flush()
    # If no members left, delete the household
    remaining = db.query(UserDB).filter(UserDB.household_id == household.id).count()
    if remaining == 0:
        db.delete(household)
    db.commit()
    return {"message": "Left household"}


@app.get("/household/partner-profile")
def get_partner_profile(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the partner's profile + calorie targets (for dual planner view)."""
    if not user.household_id:
        raise HTTPException(404, "You are not in a household")
    partner = db.query(UserDB).filter(
        UserDB.household_id == user.household_id,
        UserDB.id != user.id
    ).first()
    if not partner:
        raise HTTPException(404, "No partner in household yet")
    profile_row = db.query(UserProfileDB).filter(UserProfileDB.user_id == partner.id).first()
    if not profile_row:
        raise HTTPException(404, "Partner has not set up their profile yet")
    profile = UserProfile(
        gender=profile_row.gender, age=profile_row.age, weight_kg=profile_row.weight_kg,
        target_weight_kg=profile_row.target_weight_kg, height_cm=profile_row.height_cm,
        activity_level=profile_row.activity_level, weight_rate=profile_row.weight_rate,
        intermittent_fasting=profile_row.intermittent_fasting,
        exclude_allergens=json.loads(profile_row.exclude_allergens) if profile_row.exclude_allergens else [],
    )
    targets = calculate_calories(profile)
    return {
        "username": partner.username,
        "daily_calories": targets["daily_calories"],
        "protein_target_g": targets["protein_target_g"],
        "carbs_target_g": targets["carbs_target_g"],
        "fat_target_g": targets["fat_target_g"],
        "exclude_allergens": profile.exclude_allergens,
    }


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
        query = query.filter(RecipeDB.meal_type.contains(meal_type))
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
def create_recipe(recipe: RecipeCreate, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
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
    import re as _re

    TO_ML = {"ml": 1, "tbsp": 15, "tsp": 5, "cups": 240}
    TO_G = {"g": 1, "kg": 1000}

    # ── Ingredient name normalization ──
    # Strips prep notes like "(cubed)", "(chopped)", "(quartered)" etc.
    # Merges plurals: "carrots"→"carrot", "potatoes"→"potato"
    # Explicit synonyms for names that can't be auto-resolved.
    SYNONYMS = {
        "cooked beet": "beet",
        "young potato with skin": "potato",
        "plum tomatoes": "tomato",
        "plum tomato": "tomato",
        "fresh rosemary sprig": "fresh rosemary",
        "fresh rosemary sprigs": "fresh rosemary",
        "fresh thyme sprigs": "fresh thyme",
        "celery stalks": "celery",
        "celery stalk": "celery",
        "garlic cloves": "garlic",
        "garlic clove": "garlic",
        "sweet potatoes": "sweet potato",
        "date syrup or raw honey": "honey / date syrup",
        "eggs (hard-boiled)": "egg",
    }
    # Last word of ingredient kept plural (these are always plural in recipes)
    KEEP_PLURAL = {
        "oats", "lentils", "beans", "peas", "chickpeas", "seeds", "berries",
        "sprouts", "groats", "nuts", "raisins", "hummus",
    }

    def normalize_name(raw: str) -> str:
        n = raw.lower().strip()
        # Strip parenthetical prep notes: "beets (cubed)" → "beets"
        n = _re.sub(r"\s*\(.*?\)", "", n).strip()
        # Check synonyms first (after stripping parens)
        if n in SYNONYMS:
            return SYNONYMS[n]
        # If the last word is a known always-plural noun, keep as-is
        last_word = n.split()[-1]
        if last_word in KEEP_PLURAL:
            return n
        # Deplural: handle English plural patterns
        if n.endswith("oes"):
            return n[:-2]           # potatoes→potato, tomatoes→tomato
        if n.endswith(("shes", "ches", "xes", "zes")):
            return n[:-2]           # radishes→radish
        if n.endswith("s") and not n.endswith("ss"):
            return n[:-1]           # carrots→carrot, walnuts→walnut
        return n

    def normalize_unit(amount: float, unit: str) -> tuple[float, str]:
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
            normalized_amount, base_unit = normalize_unit(per_serving, ing["unit"])
            key = normalize_name(ing["name"])

            if key in grocery:
                if grocery[key]["unit"] == base_unit:
                    grocery[key]["total_amount"] += normalized_amount
                else:
                    alt_key = f"{key} ({base_unit})"
                    if alt_key in grocery:
                        grocery[alt_key]["total_amount"] += normalized_amount
                    else:
                        grocery[alt_key] = {
                            "name": key,
                            "total_amount": normalized_amount,
                            "unit": base_unit,
                        }
            else:
                grocery[key] = {
                    "name": key,
                    "total_amount": normalized_amount,
                    "unit": base_unit,
                }

    items = []
    for item in grocery.values():
        amount, unit = friendly_unit(item["total_amount"], item["unit"])
        items.append({"name": item["name"], "total_amount": amount, "unit": unit})

    items.sort(key=lambda x: x["name"])
    return GroceryList(items=items)


@app.get("/meal-plan/grocery-list/household", response_model=GroceryList)
def household_grocery_list(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Generate a grocery list from both household members' saved meal plans.
    Combines servings from both people for each recipe.
    """
    import re as _re

    TO_ML = {"ml": 1, "tbsp": 15, "tsp": 5, "cups": 240}
    TO_G = {"g": 1, "kg": 1000}

    SYNONYMS = {
        "cooked beet": "beet", "young potato with skin": "potato",
        "plum tomatoes": "tomato", "plum tomato": "tomato",
        "fresh rosemary sprig": "fresh rosemary", "fresh rosemary sprigs": "fresh rosemary",
        "fresh thyme sprigs": "fresh thyme", "celery stalks": "celery",
        "celery stalk": "celery", "garlic cloves": "garlic", "garlic clove": "garlic",
        "sweet potatoes": "sweet potato", "date syrup or raw honey": "honey / date syrup",
        "eggs (hard-boiled)": "egg",
    }
    KEEP_PLURAL = {"oats", "lentils", "beans", "peas", "chickpeas", "seeds", "berries",
                   "sprouts", "groats", "nuts", "raisins", "hummus"}

    def normalize_name(raw: str) -> str:
        n = raw.lower().strip()
        n = _re.sub(r"\s*\(.*?\)", "", n).strip()
        if n in SYNONYMS: return SYNONYMS[n]
        last_word = n.split()[-1]
        if last_word in KEEP_PLURAL: return n
        if n.endswith("oes"): return n[:-2]
        if n.endswith(("shes", "ches", "xes", "zes")): return n[:-2]
        if n.endswith("s") and not n.endswith("ss"): return n[:-1]
        return n

    def normalize_unit(amount, unit):
        u = unit.lower()
        if u in TO_ML: return amount * TO_ML[u], "ml"
        if u in TO_G: return amount * TO_G[u], "g"
        return amount, u

    def friendly_unit(amount, unit):
        if unit == "ml" and amount >= 1000: return round(amount / 1000, 2), "L"
        if unit == "g" and amount >= 1000: return round(amount / 1000, 2), "kg"
        return round(amount, 1), unit

    # Gather all user IDs to include
    user_ids = [user.id]
    if user.household_id:
        partner = db.query(UserDB).filter(
            UserDB.household_id == user.household_id, UserDB.id != user.id
        ).first()
        if partner:
            user_ids.append(partner.id)

    # Load all meal plan rows for all members
    all_rows = db.query(MealPlanDB).filter(MealPlanDB.user_id.in_(user_ids)).all()

    grocery: dict[str, dict] = {}

    for row in all_rows:
        recipe = get_recipe_dict(db, row.recipe_id)
        if not recipe:
            continue
        servings_base = recipe.get("servings", 1)
        user_servings = row.servings

        for ing in recipe["ingredients"]:
            per_serving = ing["amount"] / servings_base
            total_amount = per_serving * user_servings
            normalized_amount, base_unit = normalize_unit(total_amount, ing["unit"])
            key = normalize_name(ing["name"])

            if key in grocery:
                if grocery[key]["unit"] == base_unit:
                    grocery[key]["total_amount"] += normalized_amount
                else:
                    alt_key = f"{key} ({base_unit})"
                    if alt_key in grocery:
                        grocery[alt_key]["total_amount"] += normalized_amount
                    else:
                        grocery[alt_key] = {"name": key, "total_amount": normalized_amount, "unit": base_unit}
            else:
                grocery[key] = {"name": key, "total_amount": normalized_amount, "unit": base_unit}

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
    """Load the saved meal plan for the logged-in user (with partner servings if in household)."""
    rows = db.query(MealPlanDB).filter(MealPlanDB.user_id == user.id).all()
    slots = []
    # If in a household, also load partner's servings for same slots
    partner_map = {}
    if user.household_id:
        partner = db.query(UserDB).filter(
            UserDB.household_id == user.household_id, UserDB.id != user.id
        ).first()
        if partner:
            partner_rows = db.query(MealPlanDB).filter(MealPlanDB.user_id == partner.id).all()
            for r in partner_rows:
                partner_map[(r.day, r.meal)] = r.servings

    for r in rows:
        ps = partner_map.get((r.day, r.meal))
        slots.append(MealSlot(day=r.day, meal=r.meal, recipe_id=r.recipe_id, servings=r.servings, partner_servings=ps))
    return SavedMealPlan(slots=slots)


@app.put("/meal-plan/saved")
def save_meal_plan(plan: SavedMealPlan, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Save (replace) the entire meal plan for the logged-in user.
    If in a household, also saves partner's servings (same recipes, partner's portions).
    """
    db.query(MealPlanDB).filter(MealPlanDB.user_id == user.id).delete()
    for slot in plan.slots:
        db.add(MealPlanDB(user_id=user.id, day=slot.day, meal=slot.meal, recipe_id=slot.recipe_id, servings=slot.servings))

    # If household + partner servings provided, save partner's plan too (same recipes)
    if user.household_id and any(s.partner_servings is not None for s in plan.slots):
        partner = db.query(UserDB).filter(
            UserDB.household_id == user.household_id, UserDB.id != user.id
        ).first()
        if partner:
            db.query(MealPlanDB).filter(MealPlanDB.user_id == partner.id).delete()
            for slot in plan.slots:
                ps = slot.partner_servings if slot.partner_servings is not None else slot.servings
                db.add(MealPlanDB(user_id=partner.id, day=slot.day, meal=slot.meal, recipe_id=slot.recipe_id, servings=ps))

    db.commit()
    return {"message": "Meal plan saved", "slots": len(plan.slots)}


# ──────────────────────────────────────────────
# Auto-generate week plan based on user's targets
# ──────────────────────────────────────────────

import random

@app.post("/meal-plan/generate", response_model=SavedMealPlan)
def generate_meal_plan(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Auto-generate a 7-day meal plan that fits the user's calorie & macro targets.
    If in a household, also calculates partner's servings for the same recipes.

    Algorithm:
    1. Load user profile → calculate daily calorie/macro targets.
    2. Load all recipes, filter out excluded allergens.
    3. For each day, pick breakfast + lunch + dinner (+ snack if needed)
       that best match the daily targets, with variety across the week.
    4. If household, calculate partner servings for the same recipe picks.
    """
    # 1. Load profile & targets
    row = db.query(UserProfileDB).filter(UserProfileDB.user_id == user.id).first()
    if not row:
        row = UserProfileDB(user_id=user.id)
        db.add(row)
        db.commit()
        db.refresh(row)

    profile = UserProfile(
        gender=row.gender, age=row.age, weight_kg=row.weight_kg,
        target_weight_kg=row.target_weight_kg, height_cm=row.height_cm,
        activity_level=row.activity_level, weight_rate=row.weight_rate,
        intermittent_fasting=row.intermittent_fasting,
        exclude_allergens=json.loads(row.exclude_allergens) if row.exclude_allergens else [],
    )
    targets = calculate_calories(profile)
    daily_cal = targets["daily_calories"]
    target_protein = targets["protein_target_g"]
    target_carbs = targets["carbs_target_g"]
    target_fat = targets["fat_target_g"]

    # 1b. Load partner profile if in household
    partner_targets = None
    if user.household_id:
        partner = db.query(UserDB).filter(
            UserDB.household_id == user.household_id, UserDB.id != user.id
        ).first()
        if partner:
            p_row = db.query(UserProfileDB).filter(UserProfileDB.user_id == partner.id).first()
            if p_row:
                p_profile = UserProfile(
                    gender=p_row.gender, age=p_row.age, weight_kg=p_row.weight_kg,
                    target_weight_kg=p_row.target_weight_kg, height_cm=p_row.height_cm,
                    activity_level=p_row.activity_level, weight_rate=p_row.weight_rate,
                    intermittent_fasting=p_row.intermittent_fasting,
                    exclude_allergens=json.loads(p_row.exclude_allergens) if p_row.exclude_allergens else [],
                )
                partner_targets = calculate_calories(p_profile)

    # 2. Load recipes, exclude allergens (combine both people's allergens for filtering)
    all_recipes = [r.to_dict() for r in db.query(RecipeDB).all()]
    excluded = [a.lower() for a in profile.exclude_allergens]
    if excluded:
        all_recipes = [
            r for r in all_recipes
            if not any(a.lower() in excluded for a in r.get("allergens", []))
        ]

    # Exclude recipes rated 1-2 stars by this user
    low_rated = {r.recipe_id for r in db.query(MealRatingDB).filter(
        MealRatingDB.user_id == user.id, MealRatingDB.rating <= 2
    ).all()}
    if low_rated:
        all_recipes = [r for r in all_recipes if r["id"] not in low_rated]

    # Group by meal type (meal_type can be comma-separated like "breakfast,lunch")
    by_type = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for r in all_recipes:
        mt = r["meal_type"]
        for t in mt.split(","):
            t = t.strip()
            if t in by_type:
                by_type[t].append(r)

    # If a meal type has no recipes, allow any recipe for that slot
    for mt in ["breakfast", "lunch", "dinner"]:
        if not by_type[mt]:
            by_type[mt] = all_recipes

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    meals_order = ["breakfast", "lunch", "dinner", "snack"]

    # Calorie distribution across meals (% of daily target)
    MEAL_SHARE = {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snack": 0.10}

    def round_servings(s):
        """Round to nearest 0.5, min 0.5"""
        return max(0.5, round(s * 2) / 2)

    # 3. For each day, pick recipes then calculate servings to hit targets
    slots = []
    usage_count = {}

    for day in days:
        best_combo = None
        best_score = float("inf")

        for _ in range(200):
            combo = {}
            for meal in ["breakfast", "lunch", "dinner"]:
                pool = by_type[meal]
                if not pool:
                    continue
                weights = [1.0 / (1 + usage_count.get(r["id"], 0)) for r in pool]
                total_w = sum(weights)
                weights = [w / total_w for w in weights]
                combo[meal] = random.choices(pool, weights=weights, k=1)[0]

            # Always try to include a snack
            if by_type["snack"]:
                snack_weights = [1.0 / (1 + usage_count.get(r["id"], 0)) for r in by_type["snack"]]
                total_sw = sum(snack_weights)
                snack_weights = [w / total_sw for w in snack_weights]
                combo["snack"] = random.choices(by_type["snack"], weights=snack_weights, k=1)[0]

            # Calculate servings per meal to hit calorie share
            combo_servings = {}
            total_cal = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            for meal in combo:
                meal_target_cal = daily_cal * MEAL_SHARE[meal]
                recipe_cal = combo[meal]["calories"]
                if recipe_cal > 0:
                    s = round_servings(meal_target_cal / recipe_cal)
                else:
                    s = 1.0
                combo_servings[meal] = s
                total_cal += recipe_cal * s
                total_protein += combo[meal]["macros"]["protein_g"] * s
                total_carbs += combo[meal]["macros"]["carbs_g"] * s
                total_fat += combo[meal]["macros"]["fat_g"] * s

            # Score
            cal_diff = abs(total_cal - daily_cal) / max(daily_cal, 1)
            protein_diff = abs(total_protein - target_protein) / max(target_protein, 1)
            carbs_diff = abs(total_carbs - target_carbs) / max(target_carbs, 1)
            fat_diff = abs(total_fat - target_fat) / max(target_fat, 1)

            score = cal_diff * 0.50 + protein_diff * 0.25 + carbs_diff * 0.15 + fat_diff * 0.10

            repeat_penalty = sum(usage_count.get(combo[m]["id"], 0) * 0.05 for m in combo)
            score += repeat_penalty

            if score < best_score:
                best_score = score
                best_combo = combo
                best_servings = combo_servings

        if best_combo:
            for meal in meals_order:
                if meal in best_combo:
                    rid = best_combo[meal]["id"]
                    s = best_servings.get(meal, 1.0)
                    # Calculate partner servings for same recipe
                    ps = None
                    if partner_targets:
                        p_daily = partner_targets["daily_calories"]
                        p_meal_cal = p_daily * MEAL_SHARE[meal]
                        recipe_cal = best_combo[meal]["calories"]
                        if recipe_cal > 0:
                            ps = round_servings(p_meal_cal / recipe_cal)
                        else:
                            ps = 1.0
                    slots.append(MealSlot(day=day, meal=meal, recipe_id=rid, servings=s, partner_servings=ps))
                    usage_count[rid] = usage_count.get(rid, 0) + 1

    return SavedMealPlan(slots=slots)


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
    "12_12": "12:12 (12h eating window)",
    "14_10": "14:10 (10h eating window)",
    "16_8": "16:8 (8h eating window)",
    "18_6": "18:6 (6h eating window)",
    "20_4": "20:4 (4h eating window)",
}


# Calorie adjustment per kg/week: 1 kg body fat ≈ 7700 cal
# 0.25 kg/week = 275 cal/day, 0.5 kg/week = 550 cal/day
RATE_ADJUSTMENTS = {
    "lose_0.5": -550,
    "lose_0.25": -275,
    "maintain": 0,
    "gain_0.25": 275,
    "gain_0.5": 550,
}


def calculate_calories(profile: UserProfile) -> dict:
    """
    Mifflin-St Jeor equation for BMR then multiply by activity level.
    Then adjust based on weight rate:
      - lose_0.5:  −550 cal/day (~0.5 kg loss/week)
      - lose_0.25: −275 cal/day (~0.25 kg loss/week)
      - maintain:  no change
      - gain_0.25: +275 cal/day (~0.25 kg gain/week)
      - gain_0.5:  +550 cal/day (~0.5 kg gain/week)

    Male:   BMR = 10 × weight(kg) + 6.25 × height(cm) – 5 × age + 5
    Female: BMR = 10 × weight(kg) + 6.25 × height(cm) – 5 × age – 161
    """
    if profile.gender == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161

    factor = ACTIVITY_FACTORS.get(profile.activity_level, 1.55)
    maintenance_cal = int(bmr * factor)

    # Apply rate adjustment
    adjustment = RATE_ADJUSTMENTS.get(profile.weight_rate, 0)
    daily_cal = max(1200, maintenance_cal + adjustment)  # never go below 1200

    # Calculate weeks to reach target weight
    weight_diff = abs(profile.target_weight_kg - profile.weight_kg)
    weeks_to_goal = None
    if profile.weight_rate != "maintain" and weight_diff > 0:
        rate_kg = 0.5 if "0.5" in profile.weight_rate else 0.25
        weeks_to_goal = int(weight_diff / rate_kg) if rate_kg > 0 else None

    # ── Longevity macro split (age-dependent) ──
    # Protein: 1.4 g/kg baseline for muscle maintenance & satiety.
    #   65 and over: bumped to 1.6 g/kg to prevent sarcopenia.
    # Remaining calories split: ~55-60% carbs (complex), ~25-35% fat (healthy)

    if profile.age >= 65:
        # Elderly: prioritize muscle maintenance
        protein_g = int(profile.weight_kg * 1.6)
    else:
        protein_g = int(profile.weight_kg * 1.4)

    protein_cal = protein_g * 4
    remaining_cal = daily_cal - protein_cal

    # Remaining split: ~60% carbs, ~40% fat (of remaining calories)
    carbs_g = int((remaining_cal * 0.60) / 4)
    fat_g = int((remaining_cal * 0.40) / 9)

    return {
        "daily_calories": daily_cal,
        "maintenance_calories": maintenance_cal,
        "calorie_adjustment": adjustment,
        "weeks_to_goal": weeks_to_goal,
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
        target_weight_kg=row.target_weight_kg,
        height_cm=row.height_cm,
        activity_level=row.activity_level,
        weight_rate=row.weight_rate,
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

    # Log weight if it changed (or first time)
    old_weight = row.weight_kg if row.weight_kg else None
    if old_weight != profile.weight_kg:
        # Only log if last entry is older than 1 day (avoid spam)
        last_log = db.query(WeightLogDB).filter(
            WeightLogDB.user_id == user.id
        ).order_by(WeightLogDB.recorded_at.desc()).first()
        should_log = True
        if last_log:
            try:
                last_dt = datetime.fromisoformat(last_log.recorded_at)
                if (datetime.now(timezone.utc) - last_dt) < timedelta(hours=12):
                    # Update existing entry instead of creating new
                    last_log.weight_kg = profile.weight_kg
                    should_log = False
            except (ValueError, TypeError):
                pass
        if should_log:
            db.add(WeightLogDB(user_id=user.id, weight_kg=profile.weight_kg))

    row.gender = profile.gender
    row.age = profile.age
    row.weight_kg = profile.weight_kg
    row.target_weight_kg = profile.target_weight_kg
    row.height_cm = profile.height_cm
    row.activity_level = profile.activity_level
    row.weight_rate = profile.weight_rate
    row.intermittent_fasting = profile.intermittent_fasting
    row.exclude_allergens = json.dumps(profile.exclude_allergens)
    db.commit()

    targets = calculate_calories(profile)
    return UserProfileResponse(**profile.model_dump(), **targets)


@app.get("/profile/weight-history")
def get_weight_history(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get weight log entries for the current user."""
    logs = db.query(WeightLogDB).filter(
        WeightLogDB.user_id == user.id
    ).order_by(WeightLogDB.recorded_at.asc()).all()
    return [{"weight_kg": l.weight_kg, "recorded_at": l.recorded_at} for l in logs]


# ──────────────────────────────────────────────
# Meal Ratings
# ──────────────────────────────────────────────

@app.post("/ratings")
def rate_meal(data: dict, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Rate a recipe 1-5 stars. Updates existing rating if already rated."""
    recipe_id = data.get("recipe_id")
    rating = data.get("rating")
    if not recipe_id or not rating or rating < 1 or rating > 5:
        raise HTTPException(400, "recipe_id and rating (1-5) required")
    existing = db.query(MealRatingDB).filter(
        MealRatingDB.user_id == user.id, MealRatingDB.recipe_id == recipe_id
    ).first()
    if existing:
        existing.rating = rating
        existing.rated_at = datetime.now(timezone.utc).isoformat()
    else:
        db.add(MealRatingDB(user_id=user.id, recipe_id=recipe_id, rating=rating))
    db.commit()
    return {"ok": True, "recipe_id": recipe_id, "rating": rating}


@app.get("/ratings")
def get_ratings(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all ratings for the current user."""
    ratings = db.query(MealRatingDB).filter(MealRatingDB.user_id == user.id).all()
    return [{"recipe_id": r.recipe_id, "rating": r.rating} for r in ratings]


@app.get("/ratings/aggregate")
def get_aggregate_ratings(db: Session = Depends(get_db)):
    """Get average rating and vote count per recipe (all users)."""
    from sqlalchemy import func
    results = db.query(
        MealRatingDB.recipe_id,
        func.avg(MealRatingDB.rating).label("avg"),
        func.count(MealRatingDB.id).label("count")
    ).group_by(MealRatingDB.recipe_id).all()
    return [{"recipe_id": r.recipe_id, "avg": round(r.avg, 1), "count": r.count} for r in results]


# ──────────────────────────────────────────────
# Admin endpoints
# ──────────────────────────────────────────────

@app.get("/admin/users")
def admin_list_users(admin: UserDB = Depends(require_admin), db: Session = Depends(get_db)):
    """List all users (admin only)."""
    users = db.query(UserDB).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "email_verified": u.email_verified,
        }
        for u in users
    ]


@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, admin: UserDB = Depends(require_admin), db: Session = Depends(get_db)):
    """Delete a user (admin only). Cannot delete yourself."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted"}


@app.put("/admin/users/{user_id}/role")
def admin_change_role(user_id: int, role: str, admin: UserDB = Depends(require_admin), db: Session = Depends(get_db)):
    """Change a user's role (admin only)."""
    if role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'user'")
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    return {"message": f"{user.username} is now {role}"}


@app.post("/admin/recipes", response_model=RecipeResponse)
def admin_create_recipe(recipe: RecipeCreate, admin: UserDB = Depends(require_admin), db: Session = Depends(get_db)):
    """Create a recipe (admin only)."""
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


@app.put("/admin/recipes/{recipe_id}", response_model=RecipeResponse)
def admin_update_recipe(recipe_id: int, recipe: RecipeCreate, admin: UserDB = Depends(require_admin), db: Session = Depends(get_db)):
    """Update a recipe (admin only)."""
    db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_recipe.name = recipe.name
    db_recipe.description = recipe.description
    db_recipe.category = recipe.category
    db_recipe.meal_type = recipe.meal_type
    db_recipe.servings = recipe.servings
    db_recipe.prep_time_min = recipe.prep_time_min
    db_recipe.calories = recipe.calories
    db_recipe.protein_g = recipe.macros.protein_g
    db_recipe.carbs_g = recipe.macros.carbs_g
    db_recipe.fat_g = recipe.macros.fat_g
    db_recipe.fiber_g = recipe.macros.fiber_g
    db_recipe.nutrients_json = json.dumps(recipe.nutrients.model_dump(exclude_none=True))
    db_recipe.instructions_json = json.dumps(recipe.instructions)
    db_recipe.health_benefits_json = json.dumps(recipe.health_benefits)
    db_recipe.allergens_json = json.dumps(recipe.allergens)

    # Replace ingredients
    for old_ing in db_recipe.ingredients:
        db.delete(old_ing)
    for ing in recipe.ingredients:
        db_recipe.ingredients.append(
            IngredientDB(name=ing.name, amount=ing.amount, unit=ing.unit)
        )
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.to_dict()


@app.delete("/admin/recipes/{recipe_id}")
def admin_delete_recipe(recipe_id: int, admin: UserDB = Depends(require_admin), db: Session = Depends(get_db)):
    """Delete a recipe (admin only)."""
    db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"message": f"Recipe '{db_recipe.name}' deleted"}


# This lets you run the file directly with: python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
