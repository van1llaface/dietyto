"""
seed.py — Fills the database with your initial recipes.

Run this ONCE to populate the database:
    python seed.py

After running, you'll see longevity.db appear in the backend folder.
That file IS your database. Your recipes are now permanent.
"""

import json
from database import engine, SessionLocal, Base
from db_models import RecipeDB, IngredientDB

# The same recipes from app.py, now as seed data
RECIPES = [
    {
        "name": "Longevity Salad",
        "description": "Nutrient-dense salad with omega-3s and antioxidants.",
        "category": "anti-inflammatory",
        "meal_type": "lunch",
        "servings": 1,
        "prep_time_min": 15,
        "calories": 420,
        "protein_g": 14, "carbs_g": 45, "fat_g": 24, "fiber_g": 10,
        "nutrients": {"vitamin_c_mg": 80, "omega_3_g": 2.5, "magnesium_mg": 120, "potassium_mg": 800, "iron_mg": 4.0},
        "instructions": [
            "Wash and chop kale, massage with olive oil for 2 min.",
            "Cook quinoa according to package (or use pre-cooked).",
            "Dice avocado and halve cherry tomatoes.",
            "Combine kale, quinoa, avocado, and tomatoes in a bowl.",
            "Top with walnuts and drizzle with lemon juice.",
        ],
        "health_benefits": ["reduces inflammation", "supports heart health", "rich in fiber"],
        "allergens": [],
        "ingredients": [
            {"name": "kale", "amount": 100, "unit": "g"},
            {"name": "quinoa (cooked)", "amount": 150, "unit": "g"},
            {"name": "avocado", "amount": 80, "unit": "g"},
            {"name": "walnuts", "amount": 30, "unit": "g"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
            {"name": "cherry tomatoes", "amount": 80, "unit": "g"},
        ],
    },
    {
        "name": "Blueberry Smoothie Bowl",
        "description": "Brain-boosting smoothie bowl with antioxidants and healthy fats.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast",
        "servings": 1,
        "prep_time_min": 5,
        "calories": 310,
        "protein_g": 8, "carbs_g": 52, "fat_g": 8, "fiber_g": 12,
        "nutrients": {"vitamin_c_mg": 25, "omega_3_g": 2.0, "magnesium_mg": 80, "potassium_mg": 500, "iron_mg": 2.5},
        "instructions": [
            "Add blueberries, banana, spinach, and almond milk to blender.",
            "Blend until smooth.",
            "Pour into bowl, top with flaxseed and chia seeds.",
        ],
        "health_benefits": ["improves memory", "fights free radicals", "supports gut health"],
        "allergens": [],
        "ingredients": [
            {"name": "blueberries (frozen)", "amount": 150, "unit": "g"},
            {"name": "banana", "amount": 1, "unit": "pcs"},
            {"name": "spinach", "amount": 30, "unit": "g"},
            {"name": "almond milk", "amount": 200, "unit": "ml"},
            {"name": "flaxseed (ground)", "amount": 1, "unit": "tbsp"},
            {"name": "chia seeds", "amount": 1, "unit": "tbsp"},
        ],
    },
    {
        "name": "Grilled Salmon with Roasted Vegetables",
        "description": "Omega-3 rich salmon with colorful roasted vegetables.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 1,
        "prep_time_min": 30,
        "calories": 520,
        "protein_g": 42, "carbs_g": 35, "fat_g": 18, "fiber_g": 8,
        "nutrients": {"vitamin_c_mg": 150, "vitamin_d_mcg": 15, "vitamin_b12_mcg": 4.5, "omega_3_g": 3.5, "magnesium_mg": 60, "potassium_mg": 900, "iron_mg": 2.0},
        "instructions": [
            "Preheat oven to 200°C (400°F).",
            "Dice sweet potato and bell pepper, toss with olive oil.",
            "Spread vegetables on baking sheet, roast for 15 min.",
            "Add broccoli florets, roast another 10 min.",
            "Season salmon with garlic, lemon, salt, and pepper.",
            "Grill or pan-sear salmon for 4 min each side.",
            "Plate salmon over roasted vegetables.",
        ],
        "health_benefits": ["rich in omega-3", "supports brain health", "strengthens bones"],
        "allergens": [],
        "ingredients": [
            {"name": "salmon fillet", "amount": 200, "unit": "g"},
            {"name": "broccoli", "amount": 150, "unit": "g"},
            {"name": "sweet potato", "amount": 150, "unit": "g"},
            {"name": "red bell pepper", "amount": 100, "unit": "g"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "garlic cloves", "amount": 2, "unit": "pcs"},
            {"name": "lemon", "amount": 0.5, "unit": "pcs"},
        ],
    },
    {
        "name": "Overnight Oats with Nuts and Berries",
        "description": "Prep the night before — grab and go breakfast for busy mornings.",
        "category": "gut-friendly",
        "meal_type": "breakfast",
        "servings": 1,
        "prep_time_min": 5,
        "calories": 380,
        "protein_g": 12, "carbs_g": 55, "fat_g": 12, "fiber_g": 9,
        "nutrients": {"vitamin_c_mg": 15, "magnesium_mg": 100, "iron_mg": 3.5, "calcium_mg": 200},
        "instructions": [
            "Mix oats, almond milk, and chia seeds in a jar.",
            "Refrigerate overnight (or at least 4 hours).",
            "Top with berries, almonds, and a drizzle of honey.",
        ],
        "health_benefits": ["supports gut microbiome", "sustained energy", "lowers cholesterol"],
        "allergens": ["gluten"],
        "ingredients": [
            {"name": "rolled oats", "amount": 80, "unit": "g"},
            {"name": "almond milk", "amount": 200, "unit": "ml"},
            {"name": "chia seeds", "amount": 1, "unit": "tbsp"},
            {"name": "mixed berries", "amount": 80, "unit": "g"},
            {"name": "almonds", "amount": 20, "unit": "g"},
            {"name": "honey", "amount": 1, "unit": "tsp"},
        ],
    },
    {
        "name": "Lentil & Turmeric Soup",
        "description": "Warming anti-inflammatory soup packed with protein and fiber.",
        "category": "anti-inflammatory",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 35,
        "calories": 340,
        "protein_g": 20, "carbs_g": 42, "fat_g": 10, "fiber_g": 14,
        "nutrients": {"iron_mg": 6.0, "magnesium_mg": 70, "potassium_mg": 600, "zinc_mg": 3.0},
        "instructions": [
            "Dice onion and mince garlic.",
            "Heat olive oil in pot, sauté onion until soft (5 min).",
            "Add garlic, turmeric, and cumin — stir 1 min.",
            "Add lentils and vegetable broth, bring to boil.",
            "Simmer 20 min until lentils are soft.",
            "Stir in coconut milk, blend partially for creamy texture.",
        ],
        "health_benefits": ["anti-inflammatory", "high plant protein", "supports digestion"],
        "allergens": [],
        "ingredients": [
            {"name": "red lentils", "amount": 200, "unit": "g"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic cloves", "amount": 3, "unit": "pcs"},
            {"name": "turmeric (ground)", "amount": 1, "unit": "tsp"},
            {"name": "cumin (ground)", "amount": 0.5, "unit": "tsp"},
            {"name": "coconut milk", "amount": 200, "unit": "ml"},
            {"name": "vegetable broth", "amount": 500, "unit": "ml"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
        ],
    },
    {
        "name": "Mediterranean Chickpea Bowl",
        "description": "A filling grain bowl inspired by Blue Zone diets.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 1,
        "prep_time_min": 20,
        "calories": 450,
        "protein_g": 18, "carbs_g": 58, "fat_g": 16, "fiber_g": 11,
        "nutrients": {"vitamin_c_mg": 30, "calcium_mg": 180, "iron_mg": 4.5, "magnesium_mg": 90, "potassium_mg": 650},
        "instructions": [
            "Dice cucumber, halve tomatoes, thinly slice red onion.",
            "Combine chickpeas and vegetables in a bowl.",
            "Crumble feta on top.",
            "Serve over brown rice.",
            "Drizzle with olive oil and lemon juice.",
        ],
        "health_benefits": ["Blue Zone inspired", "high fiber", "lowers blood pressure"],
        "allergens": ["lactose"],
        "ingredients": [
            {"name": "chickpeas (cooked)", "amount": 200, "unit": "g"},
            {"name": "cucumber", "amount": 100, "unit": "g"},
            {"name": "cherry tomatoes", "amount": 100, "unit": "g"},
            {"name": "red onion", "amount": 30, "unit": "g"},
            {"name": "feta cheese", "amount": 40, "unit": "g"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "brown rice (cooked)", "amount": 150, "unit": "g"},
            {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
        ],
    },
    {
        "name": "Green Tea Energy Balls",
        "description": "No-bake snack with matcha, dates, and nuts.",
        "category": "antioxidant-rich",
        "meal_type": "snack",
        "servings": 4,
        "prep_time_min": 10,
        "calories": 160,
        "protein_g": 5, "carbs_g": 22, "fat_g": 7, "fiber_g": 3,
        "nutrients": {"magnesium_mg": 40, "iron_mg": 1.5, "calcium_mg": 50},
        "instructions": [
            "Add all ingredients to a food processor.",
            "Blend until mixture sticks together.",
            "Roll into small balls (makes ~8).",
            "Refrigerate for 30 min before serving.",
        ],
        "health_benefits": ["sustained energy", "rich in antioxidants", "no added sugar"],
        "allergens": ["gluten"],
        "ingredients": [
            {"name": "dates (pitted)", "amount": 100, "unit": "g"},
            {"name": "almonds", "amount": 60, "unit": "g"},
            {"name": "rolled oats", "amount": 40, "unit": "g"},
            {"name": "matcha powder", "amount": 1, "unit": "tsp"},
            {"name": "coconut flakes", "amount": 20, "unit": "g"},
        ],
    },
]


def seed():
    # Create all tables (if they don't exist yet)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if data already exists
    existing = db.query(RecipeDB).count()
    if existing > 0:
        print(f"Database already has {existing} recipes. Skipping seed.")
        db.close()
        return

    # Insert each recipe
    for recipe_data in RECIPES:
        ingredients_data = recipe_data.pop("ingredients")

        recipe = RecipeDB(
            name=recipe_data["name"],
            description=recipe_data["description"],
            category=recipe_data["category"],
            meal_type=recipe_data["meal_type"],
            servings=recipe_data["servings"],
            prep_time_min=recipe_data["prep_time_min"],
            calories=recipe_data["calories"],
            protein_g=recipe_data["protein_g"],
            carbs_g=recipe_data["carbs_g"],
            fat_g=recipe_data["fat_g"],
            fiber_g=recipe_data["fiber_g"],
            nutrients_json=json.dumps(recipe_data["nutrients"]),
            instructions_json=json.dumps(recipe_data["instructions"]),
            health_benefits_json=json.dumps(recipe_data["health_benefits"]),
            allergens_json=json.dumps(recipe_data["allergens"]),
        )

        # Add ingredients
        for ing in ingredients_data:
            recipe.ingredients.append(
                IngredientDB(name=ing["name"], amount=ing["amount"], unit=ing["unit"])
            )

        db.add(recipe)

    db.commit()
    print(f"Seeded {len(RECIPES)} recipes into the database!")
    db.close()


if __name__ == "__main__":
    seed()
