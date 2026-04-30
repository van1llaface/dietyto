"""
Seed script: Delete all existing recipes and add 31 Blue Zone longevity recipes.
Run from backend folder: python seed_recipes.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from db_models import RecipeDB, IngredientDB
import json

# Image URLs scraped from elizabethrider.com (verified from actual pages)
RECIPE_IMAGES = {
    "Easy Maple Dijon Salmon": "https://www.elizabethrider.com/wp-content/uploads/2020/07/Easy-Salmon-Recipe-Elizabeth-Rider-2.jpg",
    "Vibrant Spinach Soup": "https://www.elizabethrider.com/wp-content/uploads/2024/01/Spinach-Soup-Recipe-Elizabeth-Rider-2.jpg",
    "Creamy Potato Leek Soup": "https://www.elizabethrider.com/wp-content/uploads/2025/02/Potato-Leek-Soup-Elizabeth-Rider.2025-5-1024x1536.jpg",
    "Loaded Vegetable Soup": "https://www.elizabethrider.com/wp-content/uploads/2022/10/Veggie-Soup-Recipe-in-2-bowls-Elizabeth-Rider-1024x1536.jpg",
    "Mint & Pistachio Quinoa Salad": "https://www.elizabethrider.com/wp-content/uploads/2025/02/Elizabeth-Rider-Mint-Pistachio-Quinoa-Salad-4.jpg",
    "Miso Salmon Curry": "https://www.elizabethrider.com/wp-content/uploads/2022/03/MisoSalmonCurry-7-1078x1536.jpg",
    "White Bean & Kale Soup": "https://www.elizabethrider.com/wp-content/uploads/2024/10/White-Bean-and-Kale-Soup-Whole-Foods-Recipe-by-Elizabeth-Rider.jpg",
    "Red Lentil Soup with Lemon": "https://www.elizabethrider.com/wp-content/uploads/2022/09/red-lentil-soup-recipe-in-bowls-with-spice-and-cilantro-elizabeth-rider-1-1024x1536.jpg",
    "Creamy Cauliflower Soup": "https://www.elizabethrider.com/wp-content/uploads/2015/02/Cauliflower-Soup-Elizabeth-Rider.jpg",
    "Garlic Yogurt Sauce": "https://www.elizabethrider.com/wp-content/uploads/2025/08/Garlic-Yogurt-Sauce-2-1024x1536.jpg",
    "Butternut Squash & Carrot Curry Soup": "https://www.elizabethrider.com/wp-content/uploads/2018/09/Healing-Butternut-Squash-Carrot-Curry-Soup-Elizabeth-Rider.jpg",
    "Three Bean Salad": "https://www.elizabethrider.com/wp-content/uploads/2025/06/Three-Bean-Salad-Elizabeth-Rider.2025-07-1024x1536.jpg",
    "Sheet Pan Salmon with Asparagus": "https://www.elizabethrider.com/wp-content/uploads/2025/02/Easy-Sheet-Pan-Salmon-Elizabeth-Rider.2025-4-1024x1536.jpg",
    "Easy Lentil Soup": "https://www.elizabethrider.com/wp-content/uploads/2020/09/lentil-soup-2.jpg",
    "Black Bean & Sweet Potato Salad": "https://www.elizabethrider.com/wp-content/uploads/2018/06/Black-Bean-Sweet-Potato-Salad-Elizabeth-Rider-600.jpeg",
    "Chia Seed Pudding": "https://www.elizabethrider.com/wp-content/uploads/2019/09/Elizabeth-Rider-Chia-Seed-Pudding-Recipe-Blog-copy-683x1024.jpg",
    "Mediterranean Bean Salad": "https://www.elizabethrider.com/wp-content/uploads/2025/06/Bean-Salad-updated-Elizabeth-Rider.2025-4-1024x1536.jpg",
    "Pineapple Spinach Smoothie": "https://www.elizabethrider.com/wp-content/uploads/2020/11/CandySpinachSmoothie-9.jpg",
    "Rainbow Fruit Salad": "https://www.elizabethrider.com/wp-content/uploads/2022/08/Fruit-Salad-Recipe-in-Bowl-Elizabeth-Rider.jpg",
    "Sesame Cucumber Salad": "https://www.elizabethrider.com/wp-content/uploads/2023/02/Sesame-Cucumber-Salad-05.jpg",
    "Mango Avocado Cucumber Salad": "https://www.elizabethrider.com/wp-content/uploads/2020/06/Mango-Avocado-Cucumber-Summer-Salad-Elizabeth-Rider.jpg",
    "Green Goddess Salad": "https://www.elizabethrider.com/wp-content/uploads/2024/12/Green-Goddess-Salad-Recipe-Elizabeth-Rider-.jpg",
    "Vegetarian Chili": "https://www.elizabethrider.com/wp-content/uploads/2019/10/3-bean-vegetarian-chili-Elizabeth-Rider.jpeg",
    "Apple Cider Lentil Salad": "https://www.elizabethrider.com/wp-content/uploads/2019/09/apple-cider-lentil-salad-elizabeth-rider-blog.jpeg",
    "Layered Ratatouille": "https://www.elizabethrider.com/wp-content/uploads/2020/12/Elizabeth-Rider-Ratatouille.jpg",
    "Loaded Veggie Hummus Wrap": "https://www.elizabethrider.com/wp-content/uploads/2020/09/Veggie-Hummus-Wraps-Recipe-Elizabeth-Rider.jpg",
    "Minestrone Soup": "https://www.elizabethrider.com/wp-content/uploads/2018/10/Easy-Healthy-Minestrone-Elizabeth-Rider-blog.jpeg",
    "Lemon Garlic Baked Salmon": "https://www.elizabethrider.com/wp-content/uploads/2022/05/lemon-garlic-salmon-recipe-copyrightelizabethrider.jpeg",
    "Spicy Black Bean Buddha Bowl": "https://www.elizabethrider.com/wp-content/uploads/2017/01/Buddha-Bowl-Elizabeth-Rider-600.jpeg",
    "Whipped Feta Dip": "https://www.elizabethrider.com/wp-content/uploads/2025/01/Whipped-Feta-Dip-Elizabeth-Rider.2025-07-1024x1536.jpg",
    # Longevity Advice recipes
    "Avocado & Blueberry Longevity Smoothie": "https://i0.wp.com/www.longevityadvice.com/wp-content/uploads/2024/10/blueberry-longevity-smoothie.jpg?resize=768%2C851&ssl=1",
    "Cooked Greens with Eggs": "https://images.pexels.com/photos/3609980/pexels-photo-3609980.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Wheat Germ & Almond Flour Porridge": "https://images.pexels.com/photos/4382895/pexels-photo-4382895.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Broccoli Sprout & Lentil Salad": "https://images.pexels.com/photos/8934919/pexels-photo-8934919.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Lentil & Carrot Salad with Garlic Dressing": "https://images.pexels.com/photos/35763746/pexels-photo-35763746.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Pomegranate & Parsley Salad": "https://i0.wp.com/www.longevityadvice.com/wp-content/uploads/2024/08/pomegranate.jpg?resize=768%2C510&ssl=1",
    "Sardine Salad with Spinach & Walnuts": "https://images.pexels.com/photos/18139200/pexels-photo-18139200.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Baked Purple Sweet Potatoes with Garlic": "https://images.pexels.com/photos/11316282/pexels-photo-11316282.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Chickpea & Purple Sweet Potato Curry": "https://images.pexels.com/photos/17902963/pexels-photo-17902963.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Garlic & Herb Roasted Mushrooms": "https://i0.wp.com/www.longevityadvice.com/wp-content/uploads/2024/10/roasted-mushrooms-anti-aging-recipe.jpg?resize=768%2C548&ssl=1",
    "Mushroom & Lentil Stew": "https://images.pexels.com/photos/12896844/pexels-photo-12896844.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Oven-Baked Wild Salmon with Rosemary": "https://images.pexels.com/photos/10942354/pexels-photo-10942354.jpeg?auto=compress&cs=tinysrgb&w=600",
    "Carrot & Garlic Hummus": "https://images.pexels.com/photos/20934274/pexels-photo-20934274.jpeg?auto=compress&cs=tinysrgb&w=600",
}

db = SessionLocal()

# 1. Delete all existing recipes (and their ingredients)
db.query(IngredientDB).delete()
deleted = db.query(RecipeDB).delete()
db.commit()
print(f"Deleted {deleted} existing recipes.")

# 2. Define all 31 Blue Zone recipes
recipes = [
    {
        "name": "Easy Maple Dijon Salmon",
        "description": "Baked salmon glazed with maple syrup, tamari, and Dijon mustard. Ready in 20 minutes with just a few ingredients.",
        "category": "heart-healthy",
        "meal_type": "lunch,dinner",
        "servings": 2,
        "prep_time_min": 20,
        "calories": 350,
        "macros": {"protein_g": 34, "carbs_g": 8, "fat_g": 18, "fiber_g": 0},
        "nutrients": {"omega_3_g": 2.5, "vitamin_d_mcg": 15, "potassium_mg": 500},
        "health_benefits": ["heart-healthy", "anti-inflammatory", "high-protein"],
        "allergens": ["fish", "soy"],
        "instructions": [
            "Preheat oven to 375°F (190°C). Line a baking sheet with parchment paper.",
            "Whisk together maple syrup, tamari, and Dijon mustard in a small bowl.",
            "Place salmon fillets on the baking sheet skin-side down. Season with salt and pepper.",
            "Coat salmon generously with the sauce.",
            "Bake 10-15 minutes until opaque and flakes with a fork.",
            "Let cool 5 minutes before serving."
        ],
        "ingredients": [
            {"name": "salmon fillet", "amount": 400, "unit": "g"},
            {"name": "maple syrup", "amount": 2, "unit": "tsp"},
            {"name": "soy sauce", "amount": 2, "unit": "tsp"},
            {"name": "olive oil", "amount": 1, "unit": "tbsp"},
        ]
    },
    {
        "name": "Vibrant Spinach Soup",
        "description": "A vibrant 20-minute spinach soup with coconut milk, ginger, and lime. Vegan and gluten-free immune booster.",
        "category": "anti-inflammatory",
        "meal_type": "lunch,dinner",
        "servings": 4,
        "prep_time_min": 20,
        "calories": 120,
        "macros": {"protein_g": 4, "carbs_g": 10, "fat_g": 8, "fiber_g": 3},
        "nutrients": {"vitamin_c_mg": 45, "iron_mg": 4, "magnesium_mg": 80},
        "health_benefits": ["anti-inflammatory", "gut-friendly", "antioxidant-rich"],
        "allergens": [],
        "instructions": [
            "Heat olive oil in a large pot over medium heat. Sauté onion with a pinch of salt for 2-3 minutes.",
            "Add celery, garlic, and ginger. Sauté until aromatic, about 5 minutes.",
            "Stir in fresh spinach and cook until wilted, about 2-4 minutes.",
            "Transfer to a blender. Add water, coconut milk, jalapeño, and lime juice. Blend until smooth.",
            "Serve immediately garnished with fresh mint and a swirl of coconut milk."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "celery", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "ginger", "amount": 20, "unit": "g"},
            {"name": "spinach", "amount": 280, "unit": "g"},
            {"name": "coconut milk", "amount": 120, "unit": "ml"},
            {"name": "lime", "amount": 1, "unit": "pcs"},
        ]
    },
    {
        "name": "Creamy Potato Leek Soup",
        "description": "Naturally creamy potato soup with leeks and fresh dill. No cream needed — Yukon Gold potatoes do the work.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 4,
        "prep_time_min": 35,
        "calories": 220,
        "macros": {"protein_g": 5, "carbs_g": 38, "fat_g": 7, "fiber_g": 4},
        "nutrients": {"potassium_mg": 800, "vitamin_c_mg": 25, "magnesium_mg": 40},
        "health_benefits": ["gut-friendly", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "Sauté sliced leeks in olive oil over medium-high heat until softened, about 5-7 minutes.",
            "Add chopped potatoes and broth. Bring to a simmer and cook 25-35 minutes until potatoes are very soft.",
            "Mash potatoes with a wooden spoon, leaving some chunks for texture.",
            "Stir in vinegar and fresh dill. Season with salt and pepper.",
            "Serve topped with a dollop of Greek yogurt and extra dill."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "leek", "amount": 1, "unit": "pcs"},
            {"name": "potato", "amount": 900, "unit": "g"},
            {"name": "chicken broth", "amount": 1200, "unit": "ml"},
            {"name": "dill", "amount": 15, "unit": "g"},
        ]
    },
    {
        "name": "Loaded Vegetable Soup",
        "description": "A nourishing 10-veggie soup packed with fiber, vitamins, and healing nutrients. Perfect for immune support.",
        "category": "antioxidant-rich",
        "meal_type": "lunch,dinner",
        "servings": 8,
        "prep_time_min": 40,
        "calories": 150,
        "macros": {"protein_g": 6, "carbs_g": 22, "fat_g": 4, "fiber_g": 6},
        "nutrients": {"vitamin_c_mg": 35, "potassium_mg": 450, "iron_mg": 2},
        "health_benefits": ["antioxidant-rich", "gut-friendly", "anti-inflammatory"],
        "allergens": [],
        "instructions": [
            "Heat olive oil in a large pot. Sauté onion, celery, carrots, and parsnip until soft, 5-6 minutes.",
            "Add garlic, bay leaf, pepper, and Italian seasoning. Stir 1-2 minutes.",
            "Add potato, green beans, zucchini, broccoli, and cauliflower. Sauté 3-4 minutes.",
            "Add crushed tomatoes to deglaze. Add beans, stock, salt, and pepper. Simmer 10 minutes.",
            "Add shredded cabbage and cook 5 more minutes. Adjust seasoning and serve."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "celery", "amount": 2, "unit": "pcs"},
            {"name": "potato", "amount": 1, "unit": "pcs"},
            {"name": "zucchini", "amount": 1, "unit": "pcs"},
            {"name": "broccoli", "amount": 150, "unit": "g"},
            {"name": "cauliflower", "amount": 100, "unit": "g"},
            {"name": "cabbage", "amount": 100, "unit": "g"},
            {"name": "tomatoes", "amount": 1, "unit": "can"},
            {"name": "kidney beans", "amount": 1, "unit": "can"},
        ]
    },
    {
        "name": "Mint & Pistachio Quinoa Salad",
        "description": "Crunchy quinoa salad with fresh mint, pistachios, feta, and a lemon-honey dressing. Perfect for meal prep.",
        "category": "antioxidant-rich",
        "meal_type": "lunch",
        "servings": 6,
        "prep_time_min": 25,
        "calories": 320,
        "macros": {"protein_g": 12, "carbs_g": 32, "fat_g": 16, "fiber_g": 6},
        "nutrients": {"magnesium_mg": 80, "iron_mg": 3, "potassium_mg": 350},
        "health_benefits": ["antioxidant-rich", "heart-healthy", "gut-friendly"],
        "allergens": ["dairy", "nuts"],
        "instructions": [
            "Cook quinoa according to package directions. Let cool.",
            "Dice cucumber and avocado. Drain and rinse chickpeas. Chop mint, cilantro, and pistachios.",
            "Whisk olive oil, lemon juice, honey, and salt for the dressing.",
            "Combine quinoa, cucumber, chickpeas, edamame, feta, mint, cilantro, avocado, and pistachios.",
            "Pour dressing over salad and toss gently. Garnish with extra feta and pistachios."
        ],
        "ingredients": [
            {"name": "quinoa", "amount": 180, "unit": "g"},
            {"name": "cucumber", "amount": 1, "unit": "pcs"},
            {"name": "chickpeas", "amount": 1, "unit": "can"},
            {"name": "edamame", "amount": 150, "unit": "g"},
            {"name": "feta", "amount": 100, "unit": "g"},
            {"name": "pistachios", "amount": 60, "unit": "g"},
            {"name": "avocado", "amount": 1, "unit": "pcs"},
            {"name": "olive oil", "amount": 3, "unit": "tbsp"},
            {"name": "lemon", "amount": 1, "unit": "pcs"},
            {"name": "honey", "amount": 1, "unit": "tbsp"},
        ]
    },
    {
        "name": "Miso Salmon Curry",
        "description": "Creamy miso salmon curry with coconut milk. Serve over rice or quinoa for a wholesome Blue Zone dinner.",
        "category": "anti-inflammatory",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 30,
        "calories": 380,
        "macros": {"protein_g": 30, "carbs_g": 15, "fat_g": 22, "fiber_g": 2},
        "nutrients": {"omega_3_g": 2.0, "vitamin_d_mcg": 12, "potassium_mg": 600},
        "health_benefits": ["heart-healthy", "anti-inflammatory"],
        "allergens": ["fish", "soy"],
        "instructions": [
            "Heat oil in a pan. Sauté onion and garlic until soft.",
            "Add curry paste and miso paste, stir 1 minute.",
            "Pour in coconut milk and bring to a gentle simmer.",
            "Add salmon pieces and cook 8-10 minutes until cooked through.",
            "Serve over rice or quinoa with fresh cilantro."
        ],
        "ingredients": [
            {"name": "salmon fillet", "amount": 500, "unit": "g"},
            {"name": "coconut milk", "amount": 400, "unit": "ml"},
            {"name": "miso paste", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "rice", "amount": 200, "unit": "g"},
        ]
    },
    {
        "name": "White Bean & Kale Soup",
        "description": "Hearty soup with cannellini beans, tender kale, and Yukon gold potatoes. Cozy and nourishing.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 6,
        "prep_time_min": 40,
        "calories": 200,
        "macros": {"protein_g": 10, "carbs_g": 30, "fat_g": 5, "fiber_g": 8},
        "nutrients": {"iron_mg": 4, "calcium_mg": 120, "magnesium_mg": 60},
        "health_benefits": ["gut-friendly", "anti-inflammatory", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "Heat olive oil in a large pot. Sauté onion, carrots, and celery until soft.",
            "Add garlic and cook 1 minute. Add diced potatoes and broth.",
            "Bring to a boil, reduce heat, simmer 15 minutes until potatoes are tender.",
            "Add white beans and kale. Cook 5-7 minutes until kale is wilted.",
            "Season with salt, pepper, and a squeeze of lemon. Serve warm."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "celery", "amount": 2, "unit": "pcs"},
            {"name": "potato", "amount": 2, "unit": "pcs"},
            {"name": "kale", "amount": 150, "unit": "g"},
            {"name": "white beans", "amount": 1, "unit": "can"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
        ]
    },
    {
        "name": "Red Lentil Soup with Lemon",
        "description": "Traditional red lentil soup with fresh lemon — full of protein, fiber, and hydration.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 6,
        "prep_time_min": 35,
        "calories": 180,
        "macros": {"protein_g": 11, "carbs_g": 28, "fat_g": 3, "fiber_g": 9},
        "nutrients": {"iron_mg": 4, "magnesium_mg": 50, "potassium_mg": 400},
        "health_benefits": ["gut-friendly", "heart-healthy", "anti-inflammatory"],
        "allergens": [],
        "instructions": [
            "Heat olive oil in a pot. Sauté onion, carrot, and celery until soft.",
            "Add garlic, cumin, and turmeric. Cook 1 minute until fragrant.",
            "Add red lentils and vegetable broth. Bring to a boil.",
            "Reduce heat and simmer 20-25 minutes until lentils are very soft.",
            "Blend partially for creaminess. Stir in lemon juice, salt, and pepper. Serve."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "celery", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "lentils", "amount": 250, "unit": "g"},
            {"name": "lemon", "amount": 1, "unit": "pcs"},
        ]
    },
    {
        "name": "Creamy Cauliflower Soup",
        "description": "Velvety cauliflower soup loaded with nutrition. Use bone broth for extra protein or veggie stock to keep it vegan.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 30,
        "calories": 130,
        "macros": {"protein_g": 5, "carbs_g": 15, "fat_g": 6, "fiber_g": 4},
        "nutrients": {"vitamin_c_mg": 60, "potassium_mg": 350, "magnesium_mg": 25},
        "health_benefits": ["gut-friendly", "anti-inflammatory"],
        "allergens": [],
        "instructions": [
            "Heat olive oil in a pot. Sauté onion and garlic until soft.",
            "Add cauliflower florets and broth. Bring to a boil.",
            "Simmer 15-20 minutes until cauliflower is very tender.",
            "Blend until smooth. Season with salt, pepper, and nutmeg.",
            "Serve with a drizzle of olive oil and fresh herbs."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "cauliflower", "amount": 600, "unit": "g"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
        ]
    },
    {
        "name": "Garlic Yogurt Sauce",
        "description": "Creamy garlic yogurt sauce with lemon — perfect as a dip, drizzle, or dressing. Ready in 5 minutes.",
        "category": "gut-friendly",
        "meal_type": "snack",
        "servings": 4,
        "prep_time_min": 5,
        "calories": 45,
        "macros": {"protein_g": 4, "carbs_g": 3, "fat_g": 2, "fiber_g": 0},
        "nutrients": {"calcium_mg": 80, "vitamin_b12_mcg": 0.5},
        "health_benefits": ["gut-friendly"],
        "allergens": ["dairy"],
        "instructions": [
            "Combine Greek yogurt, minced garlic, lemon juice, salt, and pepper in a bowl.",
            "Whisk until smooth and creamy.",
            "Taste and adjust seasoning as needed.",
            "Serve immediately or refrigerate up to 5 days."
        ],
        "ingredients": [
            {"name": "greek yogurt", "amount": 200, "unit": "g"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
            {"name": "lemon", "amount": 1, "unit": "pcs"},
            {"name": "olive oil", "amount": 1, "unit": "tbsp"},
        ]
    },
    {
        "name": "Butternut Squash & Carrot Curry Soup",
        "description": "Smooth and decadent vegan curry soup with roasted butternut squash and carrots. Anti-inflammatory healing in a bowl.",
        "category": "anti-inflammatory",
        "meal_type": "lunch,dinner",
        "servings": 6,
        "prep_time_min": 45,
        "calories": 180,
        "macros": {"protein_g": 3, "carbs_g": 28, "fat_g": 7, "fiber_g": 5},
        "nutrients": {"vitamin_c_mg": 30, "potassium_mg": 500, "magnesium_mg": 45},
        "health_benefits": ["anti-inflammatory", "antioxidant-rich", "gut-friendly"],
        "allergens": [],
        "instructions": [
            "Preheat oven to 400°F. Cube butternut squash and chop carrots.",
            "Toss with olive oil, salt, and curry powder. Roast 25-30 minutes.",
            "In a pot, sauté onion and garlic. Add roasted vegetables and broth.",
            "Blend until silky smooth. Add coconut milk and stir.",
            "Season with salt and pepper. Serve with a swirl of coconut milk."
        ],
        "ingredients": [
            {"name": "butternut squash", "amount": 600, "unit": "g"},
            {"name": "carrot", "amount": 3, "unit": "pcs"},
            {"name": "coconut milk", "amount": 200, "unit": "ml"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Three Bean Salad",
        "description": "Light and flavorful bean salad with a homemade Dijon vinaigrette and fresh basil. No mayo, all flavor.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 6,
        "prep_time_min": 15,
        "calories": 200,
        "macros": {"protein_g": 10, "carbs_g": 28, "fat_g": 6, "fiber_g": 8},
        "nutrients": {"iron_mg": 3, "magnesium_mg": 50, "potassium_mg": 350},
        "health_benefits": ["gut-friendly", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "Drain and rinse all three types of beans.",
            "Whisk together olive oil, red wine vinegar, Dijon mustard, salt, and pepper for the vinaigrette.",
            "Combine beans, diced red onion, and fresh basil in a large bowl.",
            "Pour dressing over and toss gently. Let marinate 10 minutes before serving."
        ],
        "ingredients": [
            {"name": "kidney beans", "amount": 1, "unit": "can"},
            {"name": "chickpeas", "amount": 1, "unit": "can"},
            {"name": "black beans", "amount": 1, "unit": "can"},
            {"name": "olive oil", "amount": 3, "unit": "tbsp"},
            {"name": "onion", "amount": 0.5, "unit": "pcs"},
        ]
    },
    {
        "name": "Sheet Pan Salmon with Asparagus",
        "description": "Easy one-pan salmon with garlic, lemon, and crisp asparagus. Ready in under 30 minutes.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 3,
        "prep_time_min": 25,
        "calories": 340,
        "macros": {"protein_g": 32, "carbs_g": 6, "fat_g": 20, "fiber_g": 3},
        "nutrients": {"omega_3_g": 2.2, "vitamin_d_mcg": 14, "potassium_mg": 550},
        "health_benefits": ["heart-healthy", "anti-inflammatory", "high-protein"],
        "allergens": ["fish"],
        "instructions": [
            "Preheat oven to 400°F (200°C). Line a baking sheet with parchment.",
            "Place salmon fillets and trimmed asparagus on the sheet.",
            "Drizzle with olive oil, minced garlic, lemon juice, salt, and pepper.",
            "Bake 12-15 minutes until salmon is opaque and asparagus is tender-crisp.",
            "Serve with lemon wedges."
        ],
        "ingredients": [
            {"name": "salmon fillet", "amount": 450, "unit": "g"},
            {"name": "asparagus", "amount": 300, "unit": "g"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "lemon", "amount": 1, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Easy Lentil Soup",
        "description": "A family-favorite lentil soup that's flexible, filling, and full of fiber. Great for meal prep.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 6,
        "prep_time_min": 40,
        "calories": 190,
        "macros": {"protein_g": 12, "carbs_g": 30, "fat_g": 3, "fiber_g": 10},
        "nutrients": {"iron_mg": 4, "magnesium_mg": 55, "potassium_mg": 420},
        "health_benefits": ["gut-friendly", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "Heat olive oil in a large pot. Sauté onion, carrots, and celery until soft.",
            "Add garlic, cumin, and paprika. Stir 1 minute.",
            "Add lentils, diced tomatoes, and vegetable broth.",
            "Bring to a boil, reduce heat, and simmer 25-30 minutes until lentils are tender.",
            "Season with salt, pepper, and a squeeze of lemon."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "celery", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "lentils", "amount": 300, "unit": "g"},
            {"name": "tomatoes", "amount": 1, "unit": "can"},
        ]
    },
    {
        "name": "Black Bean & Sweet Potato Salad",
        "description": "Fiber-rich salad with roasted sweet potatoes, black beans, fresh herbs, and zesty lime dressing.",
        "category": "antioxidant-rich",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 35,
        "calories": 280,
        "macros": {"protein_g": 10, "carbs_g": 42, "fat_g": 8, "fiber_g": 12},
        "nutrients": {"potassium_mg": 600, "vitamin_c_mg": 20, "magnesium_mg": 60},
        "health_benefits": ["antioxidant-rich", "gut-friendly", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "Preheat oven to 400°F. Cube sweet potatoes and toss with oil and salt.",
            "Roast 20-25 minutes until golden and tender.",
            "Drain and rinse black beans. Chop cilantro and red onion.",
            "Combine sweet potatoes, black beans, corn, cilantro, and onion.",
            "Dress with lime juice, olive oil, cumin, salt, and pepper. Toss and serve."
        ],
        "ingredients": [
            {"name": "sweet potato", "amount": 400, "unit": "g"},
            {"name": "black beans", "amount": 1, "unit": "can"},
            {"name": "corn", "amount": 150, "unit": "g"},
            {"name": "onion", "amount": 0.5, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lime", "amount": 1, "unit": "pcs"},
        ]
    },
    {
        "name": "Chia Seed Pudding",
        "description": "Easy overnight chia pudding — high in omega-3s, protein, and fiber. Blue Zone approved superfood.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast,snack",
        "servings": 2,
        "prep_time_min": 5,
        "calories": 220,
        "macros": {"protein_g": 7, "carbs_g": 20, "fat_g": 12, "fiber_g": 11},
        "nutrients": {"omega_3_g": 5, "calcium_mg": 180, "magnesium_mg": 95},
        "health_benefits": ["antioxidant-rich", "gut-friendly", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "Mix chia seeds with milk in a jar or bowl.",
            "Add honey or maple syrup and vanilla extract. Stir well.",
            "Refrigerate overnight (or at least 4 hours) until thick.",
            "Stir before serving. Top with fresh berries, banana, or nuts."
        ],
        "ingredients": [
            {"name": "chia seeds", "amount": 40, "unit": "g"},
            {"name": "coconut milk", "amount": 250, "unit": "ml"},
            {"name": "honey", "amount": 1, "unit": "tbsp"},
            {"name": "blueberries", "amount": 80, "unit": "g"},
        ]
    },
    {
        "name": "Mediterranean Bean Salad",
        "description": "Fresh, zesty bean salad tossed in a simple vinaigrette with arugula for a peppery kick.",
        "category": "heart-healthy",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 15,
        "calories": 230,
        "macros": {"protein_g": 10, "carbs_g": 28, "fat_g": 9, "fiber_g": 8},
        "nutrients": {"iron_mg": 3, "magnesium_mg": 50, "potassium_mg": 380},
        "health_benefits": ["heart-healthy", "gut-friendly"],
        "allergens": [],
        "instructions": [
            "Drain and rinse beans. Dice cucumber, tomatoes, and red onion.",
            "Whisk olive oil, lemon juice, oregano, salt, and pepper for dressing.",
            "Combine beans, vegetables, and arugula in a large bowl.",
            "Drizzle with dressing and toss. Serve immediately or chill for later."
        ],
        "ingredients": [
            {"name": "chickpeas", "amount": 1, "unit": "can"},
            {"name": "kidney beans", "amount": 1, "unit": "can"},
            {"name": "cucumber", "amount": 1, "unit": "pcs"},
            {"name": "tomato", "amount": 2, "unit": "pcs"},
            {"name": "onion", "amount": 0.5, "unit": "pcs"},
            {"name": "olive oil", "amount": 3, "unit": "tbsp"},
            {"name": "lemon", "amount": 1, "unit": "pcs"},
            {"name": "spinach", "amount": 50, "unit": "g"},
        ]
    },
    {
        "name": "Pineapple Spinach Smoothie",
        "description": "Vitamin C-rich green smoothie with spinach, pineapple, and banana. Hydrating and energizing.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast,snack",
        "servings": 2,
        "prep_time_min": 5,
        "calories": 150,
        "macros": {"protein_g": 3, "carbs_g": 32, "fat_g": 1, "fiber_g": 4},
        "nutrients": {"vitamin_c_mg": 80, "potassium_mg": 400, "magnesium_mg": 40},
        "health_benefits": ["antioxidant-rich", "anti-inflammatory"],
        "allergens": [],
        "instructions": [
            "Add spinach, pineapple chunks, banana, and water to a blender.",
            "Blend on high until completely smooth, about 60 seconds.",
            "Pour into glasses and serve immediately."
        ],
        "ingredients": [
            {"name": "spinach", "amount": 60, "unit": "g"},
            {"name": "banana", "amount": 1, "unit": "pcs"},
            {"name": "pineapple", "amount": 150, "unit": "g"},
        ]
    },
    {
        "name": "Rainbow Fruit Salad",
        "description": "Quick and colorful fruit salad bursting with vitamins, fiber, and natural sweetness.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast,snack",
        "servings": 4,
        "prep_time_min": 10,
        "calories": 120,
        "macros": {"protein_g": 2, "carbs_g": 28, "fat_g": 1, "fiber_g": 4},
        "nutrients": {"vitamin_c_mg": 60, "potassium_mg": 300},
        "health_benefits": ["antioxidant-rich"],
        "allergens": [],
        "instructions": [
            "Wash and chop all fruits into bite-size pieces.",
            "Combine in a large bowl.",
            "Squeeze fresh lime juice over the top and gently toss.",
            "Serve immediately or chill for up to 2 hours."
        ],
        "ingredients": [
            {"name": "strawberries", "amount": 150, "unit": "g"},
            {"name": "blueberries", "amount": 100, "unit": "g"},
            {"name": "mango", "amount": 1, "unit": "pcs"},
            {"name": "banana", "amount": 1, "unit": "pcs"},
            {"name": "orange", "amount": 1, "unit": "pcs"},
        ]
    },
    {
        "name": "Sesame Cucumber Salad",
        "description": "Crunchy Asian-inspired cucumber salad with sesame oil and rice vinegar. Ready in 10 minutes.",
        "category": "anti-inflammatory",
        "meal_type": "lunch,snack",
        "servings": 4,
        "prep_time_min": 10,
        "calories": 70,
        "macros": {"protein_g": 2, "carbs_g": 6, "fat_g": 4, "fiber_g": 1},
        "nutrients": {"vitamin_c_mg": 5, "potassium_mg": 150},
        "health_benefits": ["anti-inflammatory"],
        "allergens": ["soy"],
        "instructions": [
            "Slice cucumbers thinly (use a mandoline for best results).",
            "Whisk together rice vinegar, sesame oil, soy sauce, and honey.",
            "Toss cucumbers with the dressing.",
            "Sprinkle with sesame seeds and serve chilled."
        ],
        "ingredients": [
            {"name": "cucumber", "amount": 3, "unit": "pcs"},
            {"name": "soy sauce", "amount": 1, "unit": "tbsp"},
            {"name": "honey", "amount": 1, "unit": "tsp"},
            {"name": "sesame seeds", "amount": 10, "unit": "g"},
        ]
    },
    {
        "name": "Mango Avocado Cucumber Salad",
        "description": "Perfectly balanced flavors and textures — mango sweetness, avocado creaminess, and cucumber crunch.",
        "category": "heart-healthy",
        "meal_type": "lunch,snack",
        "servings": 4,
        "prep_time_min": 15,
        "calories": 180,
        "macros": {"protein_g": 2, "carbs_g": 18, "fat_g": 12, "fiber_g": 5},
        "nutrients": {"vitamin_c_mg": 40, "potassium_mg": 400},
        "health_benefits": ["heart-healthy", "antioxidant-rich"],
        "allergens": [],
        "instructions": [
            "Dice mango, avocado, and cucumber into similar-sized cubes.",
            "Combine in a bowl with red onion.",
            "Dress with lime juice, olive oil, salt, and pepper.",
            "Gently toss and serve immediately."
        ],
        "ingredients": [
            {"name": "mango", "amount": 1, "unit": "pcs"},
            {"name": "avocado", "amount": 1, "unit": "pcs"},
            {"name": "cucumber", "amount": 1, "unit": "pcs"},
            {"name": "lime", "amount": 1, "unit": "pcs"},
            {"name": "onion", "amount": 0.25, "unit": "pcs"},
            {"name": "olive oil", "amount": 1, "unit": "tbsp"},
        ]
    },
    {
        "name": "Green Goddess Salad",
        "description": "Viral green goddess salad with creamy herb dressing. Great as a dip with chips or wrapped in a tortilla.",
        "category": "antioxidant-rich",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 15,
        "calories": 200,
        "macros": {"protein_g": 5, "carbs_g": 12, "fat_g": 15, "fiber_g": 4},
        "nutrients": {"vitamin_c_mg": 30, "iron_mg": 2, "calcium_mg": 80},
        "health_benefits": ["antioxidant-rich", "gut-friendly"],
        "allergens": ["nuts"],
        "instructions": [
            "Finely chop cabbage, cucumber, and green onions.",
            "Blend avocado, lemon juice, olive oil, garlic, basil, and salt for the dressing.",
            "Toss chopped vegetables with the green goddess dressing.",
            "Serve with tortilla chips or wrap in a tortilla."
        ],
        "ingredients": [
            {"name": "cabbage", "amount": 200, "unit": "g"},
            {"name": "cucumber", "amount": 1, "unit": "pcs"},
            {"name": "avocado", "amount": 1, "unit": "pcs"},
            {"name": "lemon", "amount": 1, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "garlic", "amount": 1, "unit": "pcs"},
            {"name": "walnuts", "amount": 30, "unit": "g"},
        ]
    },
    {
        "name": "Vegetarian Chili",
        "description": "Classic vegetarian chili loaded with beans and vegetables. A cool-weather Blue Zone staple.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 8,
        "prep_time_min": 45,
        "calories": 250,
        "macros": {"protein_g": 12, "carbs_g": 38, "fat_g": 5, "fiber_g": 12},
        "nutrients": {"iron_mg": 4, "potassium_mg": 500, "magnesium_mg": 60},
        "health_benefits": ["gut-friendly", "heart-healthy", "anti-inflammatory"],
        "allergens": [],
        "instructions": [
            "Heat oil in a large pot. Sauté onion, bell peppers, and carrots until soft.",
            "Add garlic, chili powder, cumin, and paprika. Stir 1 minute.",
            "Add diced tomatoes, beans, corn, and vegetable broth.",
            "Bring to a boil, reduce heat, and simmer 30 minutes.",
            "Season with salt and pepper. Serve with your favorite toppings."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "bell pepper", "amount": 2, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 4, "unit": "pcs"},
            {"name": "kidney beans", "amount": 1, "unit": "can"},
            {"name": "black beans", "amount": 1, "unit": "can"},
            {"name": "tomatoes", "amount": 2, "unit": "can"},
            {"name": "corn", "amount": 150, "unit": "g"},
        ]
    },
    {
        "name": "Apple Cider Lentil Salad",
        "description": "Lentil salad with subtle apple cider sweetness, fresh herbs, and walnuts. High-fiber and satisfying.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 30,
        "calories": 240,
        "macros": {"protein_g": 12, "carbs_g": 30, "fat_g": 8, "fiber_g": 9},
        "nutrients": {"iron_mg": 4, "magnesium_mg": 50},
        "health_benefits": ["gut-friendly", "heart-healthy"],
        "allergens": ["nuts"],
        "instructions": [
            "Cook lentils in water until tender but not mushy, about 20 minutes. Drain and cool.",
            "Whisk olive oil, apple cider vinegar, honey, salt, and pepper for dressing.",
            "Combine lentils, diced apple, walnuts, and fresh herbs.",
            "Drizzle with dressing and toss gently. Serve at room temperature."
        ],
        "ingredients": [
            {"name": "lentils", "amount": 200, "unit": "g"},
            {"name": "apple", "amount": 1, "unit": "pcs"},
            {"name": "walnuts", "amount": 40, "unit": "g"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "honey", "amount": 1, "unit": "tsp"},
        ]
    },
    {
        "name": "Layered Ratatouille",
        "description": "Beautiful baked ratatouille with layered vegetables — easy to make, gorgeous to serve. Pairs with crusty bread or quinoa.",
        "category": "antioxidant-rich",
        "meal_type": "dinner",
        "servings": 6,
        "prep_time_min": 60,
        "calories": 130,
        "macros": {"protein_g": 3, "carbs_g": 15, "fat_g": 7, "fiber_g": 4},
        "nutrients": {"vitamin_c_mg": 35, "potassium_mg": 400},
        "health_benefits": ["antioxidant-rich", "anti-inflammatory", "gut-friendly"],
        "allergens": [],
        "instructions": [
            "Preheat oven to 375°F (190°C).",
            "Slice zucchini, eggplant, and tomatoes into thin rounds.",
            "Spread a thin layer of tomato sauce in a baking dish.",
            "Layer vegetables alternating in the dish. Drizzle with olive oil, salt, pepper, and herbs.",
            "Cover with foil and bake 40 minutes. Uncover and bake 15 more minutes.",
            "Serve warm with fresh basil and parmesan."
        ],
        "ingredients": [
            {"name": "zucchini", "amount": 2, "unit": "pcs"},
            {"name": "eggplant", "amount": 1, "unit": "pcs"},
            {"name": "tomato", "amount": 4, "unit": "pcs"},
            {"name": "bell pepper", "amount": 1, "unit": "pcs"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "olive oil", "amount": 3, "unit": "tbsp"},
        ]
    },
    {
        "name": "Loaded Veggie Hummus Wrap",
        "description": "Quick and satisfying hummus wrap loaded with fresh crunchy vegetables. The perfect plant-forward lunch.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 10,
        "calories": 350,
        "macros": {"protein_g": 12, "carbs_g": 42, "fat_g": 15, "fiber_g": 8},
        "nutrients": {"iron_mg": 3, "vitamin_c_mg": 20, "magnesium_mg": 40},
        "health_benefits": ["gut-friendly", "heart-healthy"],
        "allergens": ["gluten"],
        "instructions": [
            "Warm tortillas slightly for easier wrapping.",
            "Spread a generous layer of hummus on each tortilla.",
            "Layer spinach, sliced cucumber, bell pepper, carrots, and avocado.",
            "Roll up tightly, cut in half, and serve."
        ],
        "ingredients": [
            {"name": "tortilla", "amount": 2, "unit": "pcs"},
            {"name": "hummus", "amount": 100, "unit": "g"},
            {"name": "spinach", "amount": 40, "unit": "g"},
            {"name": "cucumber", "amount": 0.5, "unit": "pcs"},
            {"name": "bell pepper", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 1, "unit": "pcs"},
            {"name": "avocado", "amount": 0.5, "unit": "pcs"},
        ]
    },
    {
        "name": "Minestrone Soup",
        "description": "Classic Italian vegetarian minestrone packed with healthy veggies and beans. Blue Zone comfort food.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 8,
        "prep_time_min": 45,
        "calories": 180,
        "macros": {"protein_g": 8, "carbs_g": 28, "fat_g": 4, "fiber_g": 7},
        "nutrients": {"vitamin_c_mg": 20, "iron_mg": 3, "potassium_mg": 400},
        "health_benefits": ["gut-friendly", "anti-inflammatory", "heart-healthy"],
        "allergens": ["gluten"],
        "instructions": [
            "Heat olive oil in a large pot. Sauté onion, celery, and carrots until soft.",
            "Add garlic, zucchini, and green beans. Cook 3 minutes.",
            "Add crushed tomatoes, broth, beans, and pasta.",
            "Simmer 15-20 minutes until pasta and vegetables are tender.",
            "Season with salt, pepper, and Italian herbs. Serve with parmesan."
        ],
        "ingredients": [
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "celery", "amount": 2, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "zucchini", "amount": 1, "unit": "pcs"},
            {"name": "tomatoes", "amount": 1, "unit": "can"},
            {"name": "kidney beans", "amount": 1, "unit": "can"},
            {"name": "pasta", "amount": 100, "unit": "g"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
        ]
    },
    {
        "name": "Lemon Garlic Baked Salmon",
        "description": "Melt-in-your-mouth baked salmon with bright lemon and garlic flavors. Just a few ingredients needed.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 25,
        "calories": 320,
        "macros": {"protein_g": 34, "carbs_g": 2, "fat_g": 19, "fiber_g": 0},
        "nutrients": {"omega_3_g": 2.5, "vitamin_d_mcg": 15, "potassium_mg": 550},
        "health_benefits": ["heart-healthy", "anti-inflammatory", "high-protein"],
        "allergens": ["fish"],
        "instructions": [
            "Preheat oven to 375°F (190°C).",
            "Place salmon fillets on a parchment-lined baking sheet.",
            "Mix olive oil, minced garlic, lemon juice, salt, and pepper. Brush over salmon.",
            "Top with lemon slices and bake 12-15 minutes.",
            "Serve with fresh herbs and extra lemon wedges."
        ],
        "ingredients": [
            {"name": "salmon fillet", "amount": 600, "unit": "g"},
            {"name": "garlic", "amount": 4, "unit": "pcs"},
            {"name": "lemon", "amount": 2, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Spicy Black Bean Buddha Bowl",
        "description": "Colorful Buddha bowl with spicy black beans, rice, and fresh vegetables. Flexible and nutritious.",
        "category": "gut-friendly",
        "meal_type": "lunch,dinner",
        "servings": 2,
        "prep_time_min": 20,
        "calories": 380,
        "macros": {"protein_g": 14, "carbs_g": 56, "fat_g": 10, "fiber_g": 12},
        "nutrients": {"iron_mg": 4, "magnesium_mg": 70, "potassium_mg": 500},
        "health_benefits": ["gut-friendly", "antioxidant-rich"],
        "allergens": [],
        "instructions": [
            "Cook rice according to package directions.",
            "Heat black beans with cumin, chili powder, and lime juice.",
            "Arrange rice, spiced beans, avocado, tomato, corn, and greens in bowls.",
            "Drizzle with lime dressing and top with cilantro."
        ],
        "ingredients": [
            {"name": "brown rice", "amount": 150, "unit": "g"},
            {"name": "black beans", "amount": 1, "unit": "can"},
            {"name": "avocado", "amount": 1, "unit": "pcs"},
            {"name": "tomato", "amount": 1, "unit": "pcs"},
            {"name": "corn", "amount": 100, "unit": "g"},
            {"name": "spinach", "amount": 50, "unit": "g"},
            {"name": "lime", "amount": 1, "unit": "pcs"},
        ]
    },
    {
        "name": "Whipped Feta Dip",
        "description": "Creamy, tangy whipped feta dip ready in 5 minutes. Perfect with veggies or toasted pita.",
        "category": "gut-friendly",
        "meal_type": "snack",
        "servings": 6,
        "prep_time_min": 5,
        "calories": 120,
        "macros": {"protein_g": 5, "carbs_g": 2, "fat_g": 10, "fiber_g": 0},
        "nutrients": {"calcium_mg": 140},
        "health_benefits": ["gut-friendly"],
        "allergens": ["dairy"],
        "instructions": [
            "Add feta, cream cheese, olive oil, lemon juice, and garlic to a food processor.",
            "Blend until smooth and creamy, scraping down sides as needed.",
            "Transfer to a bowl. Drizzle with olive oil and sprinkle with herbs.",
            "Serve with fresh vegetables or toasted pita bread."
        ],
        "ingredients": [
            {"name": "feta", "amount": 200, "unit": "g"},
            {"name": "cream cheese", "amount": 60, "unit": "g"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lemon", "amount": 0.5, "unit": "pcs"},
            {"name": "garlic", "amount": 1, "unit": "pcs"},
        ]
    },
    # ===== Longevity Advice Recipes =====
    {
        "name": "Avocado & Blueberry Longevity Smoothie",
        "author": "Longevity Advice",
        "description": "A nutrient-packed smoothie with avocado, wild blueberries, and chia seeds for anti-aging antioxidants and healthy fats.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast,snack",
        "servings": 1,
        "prep_time_min": 5,
        "calories": 380,
        "macros": {"protein_g": 6, "carbs_g": 35, "fat_g": 24, "fiber_g": 12},
        "nutrients": {"vitamin_c_mg": 30, "vitamin_e_mg": 4, "potassium_mg": 600},
        "health_benefits": ["antioxidant-rich", "anti-inflammatory", "brain-health"],
        "allergens": ["tree nuts"],
        "instructions": [
            "In a blender, combine the avocado, frozen blueberries, almond milk, honey, chia seeds, and lemon juice.",
            "Blend until smooth and creamy.",
            "Serve immediately for a nutrient-packed breakfast or snack.",
            "Hint: Add some turmeric powder, cinnamon, and ginger powder for even more healthy flavonoids."
        ],
        "ingredients": [
            {"name": "avocado", "amount": 1, "unit": "pcs"},
            {"name": "blueberries", "amount": 150, "unit": "g"},
            {"name": "almond milk", "amount": 240, "unit": "ml"},
            {"name": "honey", "amount": 1, "unit": "tbsp"},
            {"name": "chia seeds", "amount": 1, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
        ]
    },
    {
        "name": "Cooked Greens with Eggs",
        "author": "Longevity Advice",
        "description": "Wilted dark greens sautéed in olive oil with garlic, topped with soft-boiled eggs and avocado. A longevity breakfast staple.",
        "category": "high-protein",
        "meal_type": "breakfast,lunch",
        "servings": 2,
        "prep_time_min": 20,
        "calories": 320,
        "macros": {"protein_g": 16, "carbs_g": 8, "fat_g": 26, "fiber_g": 5},
        "nutrients": {"vitamin_k_mcg": 400, "iron_mg": 4, "folate_mcg": 180},
        "health_benefits": ["anti-inflammatory", "high-protein", "bone-health"],
        "allergens": ["eggs"],
        "instructions": [
            "Rinse and chop greens.",
            "Chop garlic cloves and set aside for at least 10 minutes.",
            "In a large saucepan, heat 2 tablespoons of olive oil on medium heat.",
            "Add greens and stir to evenly coat with olive oil.",
            "Add salt, pepper, and chopped garlic. Cook until greens have wilted and stems are tender.",
            "Reduce heat to low, add lemon juice and parsley, stir to combine.",
            "Remove from heat and serve topped with soft-boiled eggs and remaining olive oil, add avocado slices on the side."
        ],
        "ingredients": [
            {"name": "kale", "amount": 1, "unit": "bunch"},
            {"name": "olive oil", "amount": 4, "unit": "tbsp"},
            {"name": "garlic", "amount": 4, "unit": "pcs"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
            {"name": "dried parsley", "amount": 1, "unit": "tsp"},
            {"name": "eggs", "amount": 2, "unit": "pcs"},
            {"name": "avocado", "amount": 0.5, "unit": "pcs"},
        ]
    },
    {
        "name": "Wheat Germ & Almond Flour Porridge",
        "author": "Longevity Advice",
        "description": "A spermidine-rich porridge with wheat germ and almond flour, topped with blueberries and cinnamon for brain longevity.",
        "category": "brain-health",
        "meal_type": "breakfast",
        "servings": 1,
        "prep_time_min": 15,
        "calories": 420,
        "macros": {"protein_g": 18, "carbs_g": 30, "fat_g": 26, "fiber_g": 8},
        "nutrients": {"vitamin_e_mg": 10, "magnesium_mg": 120, "zinc_mg": 5},
        "health_benefits": ["brain-health", "anti-aging", "high-fiber"],
        "allergens": ["wheat", "tree nuts", "dairy"],
        "instructions": [
            "In a saucepan combine wheat germ, almond flour, water, heavy cream, and salt.",
            "Cook over medium heat, stirring constantly, until the porridge thickens (10-15 minutes).",
            "Remove from heat and top with butter, blueberries, and cinnamon. Eat while warm."
        ],
        "ingredients": [
            {"name": "wheat germ", "amount": 0.5, "unit": "cup"},
            {"name": "almond flour", "amount": 0.5, "unit": "cup"},
            {"name": "water", "amount": 240, "unit": "ml"},
            {"name": "heavy cream", "amount": 60, "unit": "ml"},
            {"name": "butter", "amount": 1, "unit": "tbsp"},
            {"name": "blueberries", "amount": 75, "unit": "g"},
            {"name": "cinnamon", "amount": 1, "unit": "pinch"},
        ]
    },
    {
        "name": "Broccoli Sprout & Lentil Salad",
        "author": "Longevity Advice",
        "description": "A sulforaphane-rich salad with broccoli sprouts, lentils, and a bright lemon olive oil dressing.",
        "category": "anti-inflammatory",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 10,
        "calories": 250,
        "macros": {"protein_g": 14, "carbs_g": 28, "fat_g": 10, "fiber_g": 10},
        "nutrients": {"vitamin_c_mg": 35, "iron_mg": 4, "folate_mcg": 200},
        "health_benefits": ["anti-inflammatory", "antioxidant-rich", "high-fiber"],
        "allergens": [],
        "instructions": [
            "In a large bowl, combine cooked lentils, broccoli sprouts, cherry tomatoes, and cucumber.",
            "In a small bowl, whisk together olive oil, lemon juice, salt, and pepper.",
            "Drizzle the dressing over the salad and toss gently.",
            "Serve chilled as a light meal or side."
        ],
        "ingredients": [
            {"name": "lentils", "amount": 1, "unit": "cup"},
            {"name": "broccoli sprouts", "amount": 1, "unit": "cup"},
            {"name": "cherry tomatoes", "amount": 0.5, "unit": "cup"},
            {"name": "cucumber", "amount": 0.25, "unit": "cup"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Lentil & Carrot Salad with Garlic Dressing",
        "author": "Longevity Advice",
        "description": "A fiber-rich salad of lentils and raw carrots tossed in a garlic-lemon vinaigrette with fresh parsley.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 10,
        "calories": 230,
        "macros": {"protein_g": 12, "carbs_g": 26, "fat_g": 10, "fiber_g": 9},
        "nutrients": {"vitamin_a_mcg": 500, "iron_mg": 3, "potassium_mg": 400},
        "health_benefits": ["gut-friendly", "high-fiber", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "In a bowl, combine the cooked lentils, grated carrots, and parsley.",
            "In a small bowl, whisk together olive oil, minced garlic, lemon juice, salt, and pepper.",
            "Pour the dressing over the salad and toss gently to combine.",
            "Serve chilled or at room temperature."
        ],
        "ingredients": [
            {"name": "lentils", "amount": 1, "unit": "cup"},
            {"name": "carrots", "amount": 1, "unit": "cup"},
            {"name": "fresh parsley", "amount": 0.25, "unit": "cup"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "garlic", "amount": 1, "unit": "pcs"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Pomegranate & Parsley Salad",
        "author": "Longevity Advice",
        "description": "A vibrant anti-aging salad with pomegranate seeds, spinach, almonds, and a lemon-olive oil dressing.",
        "category": "antioxidant-rich",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 10,
        "calories": 220,
        "macros": {"protein_g": 6, "carbs_g": 20, "fat_g": 14, "fiber_g": 5},
        "nutrients": {"vitamin_c_mg": 20, "vitamin_k_mcg": 150, "potassium_mg": 300},
        "health_benefits": ["antioxidant-rich", "heart-healthy", "anti-inflammatory"],
        "allergens": ["tree nuts"],
        "instructions": [
            "In a large bowl, combine the spinach, pomegranate seeds, dried parsley, and almonds.",
            "In a small bowl, whisk together olive oil, lemon juice, salt, and pepper.",
            "Drizzle the dressing over the salad and toss gently to combine.",
            "Serve as a refreshing side dish or light meal."
        ],
        "ingredients": [
            {"name": "pomegranate seeds", "amount": 1, "unit": "cup"},
            {"name": "spinach", "amount": 100, "unit": "g"},
            {"name": "dried parsley", "amount": 0.25, "unit": "cup"},
            {"name": "almonds", "amount": 0.25, "unit": "cup"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Sardine Salad with Spinach & Walnuts",
        "author": "Longevity Advice",
        "description": "A protein-rich omega-3 salad with sardines, fresh spinach, walnuts, and a tangy lemon dressing.",
        "category": "heart-healthy",
        "meal_type": "lunch",
        "servings": 1,
        "prep_time_min": 10,
        "calories": 380,
        "macros": {"protein_g": 24, "carbs_g": 6, "fat_g": 30, "fiber_g": 3},
        "nutrients": {"omega_3_g": 2.0, "calcium_mg": 350, "vitamin_d_mcg": 5},
        "health_benefits": ["heart-healthy", "brain-health", "anti-inflammatory"],
        "allergens": ["fish", "tree nuts"],
        "instructions": [
            "In a bowl, combine spinach, sardines, walnuts, and red onion.",
            "In a small bowl, whisk together olive oil, lemon juice, salt, and pepper.",
            "Drizzle the dressing over the salad and toss gently to combine.",
            "Serve immediately for a healthy, protein-rich anti-aging meal."
        ],
        "ingredients": [
            {"name": "sardines", "amount": 1, "unit": "can"},
            {"name": "spinach", "amount": 60, "unit": "g"},
            {"name": "walnuts", "amount": 0.25, "unit": "cup"},
            {"name": "red onion", "amount": 0.25, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Baked Purple Sweet Potatoes with Garlic",
        "author": "Longevity Advice",
        "description": "Okinawan purple sweet potatoes baked and drizzled with garlic-infused olive oil and parsley. A Blue Zone staple.",
        "category": "anti-aging",
        "meal_type": "dinner",
        "servings": 2,
        "prep_time_min": 65,
        "calories": 280,
        "macros": {"protein_g": 4, "carbs_g": 42, "fat_g": 12, "fiber_g": 6},
        "nutrients": {"vitamin_a_mcg": 800, "potassium_mg": 500, "vitamin_c_mg": 20},
        "health_benefits": ["anti-aging", "gut-friendly", "antioxidant-rich"],
        "allergens": [],
        "instructions": [
            "Preheat your oven to 425°F (220°C).",
            "Wash and pierce the sweet potatoes with a fork. Bake for 45-60 minutes, until tender.",
            "In a small pan, heat olive oil over medium heat and sauté the garlic until fragrant (about 1 minute).",
            "Once sweet potatoes are cooked, slice them open and drizzle with garlic oil.",
            "Sprinkle with dried parsley and season with salt and pepper. Serve warm."
        ],
        "ingredients": [
            {"name": "purple sweet potato", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "dried parsley", "amount": 0.25, "unit": "cup"},
        ]
    },
    {
        "name": "Chickpea & Purple Sweet Potato Curry",
        "author": "Longevity Advice",
        "description": "A warming curry with chickpeas and Okinawan purple sweet potatoes in coconut milk, inspired by Blue Zone diets.",
        "category": "anti-inflammatory",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 35,
        "calories": 340,
        "macros": {"protein_g": 10, "carbs_g": 38, "fat_g": 18, "fiber_g": 8},
        "nutrients": {"iron_mg": 4, "potassium_mg": 500, "vitamin_a_mcg": 600},
        "health_benefits": ["anti-inflammatory", "gut-friendly", "high-fiber"],
        "allergens": [],
        "instructions": [
            "In a large pot, heat olive oil over medium heat. Add onion and garlic, sautéing until translucent.",
            "Add diced sweet potato and curry powder, stirring for 2-3 minutes.",
            "Pour in the coconut milk and chickpeas. Bring to a simmer and cook for 15-20 minutes, until the sweet potatoes are tender.",
            "Season with salt and pepper, and garnish with fresh cilantro before serving."
        ],
        "ingredients": [
            {"name": "chickpeas", "amount": 1, "unit": "can"},
            {"name": "purple sweet potato", "amount": 1, "unit": "pcs"},
            {"name": "coconut milk", "amount": 400, "unit": "ml"},
            {"name": "curry powder", "amount": 1, "unit": "tbsp"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
            {"name": "olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "cilantro", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Garlic & Herb Roasted Mushrooms",
        "author": "Longevity Advice",
        "description": "Mixed mushrooms (shiitake, reishi) roasted with garlic and rosemary. Reishi mushrooms have been shown to extend lifespan.",
        "category": "anti-aging",
        "meal_type": "dinner",
        "servings": 2,
        "prep_time_min": 25,
        "calories": 160,
        "macros": {"protein_g": 5, "carbs_g": 8, "fat_g": 12, "fiber_g": 3},
        "nutrients": {"vitamin_d_mcg": 3, "selenium_mcg": 15, "potassium_mg": 350},
        "health_benefits": ["anti-aging", "immune-boosting", "antioxidant-rich"],
        "allergens": [],
        "instructions": [
            "Preheat your oven to 400°F (200°C).",
            "In a mixing bowl, combine the mushrooms, garlic, olive oil, rosemary, salt, and pepper. Toss until well-coated.",
            "Spread the mushrooms on a baking sheet in a single layer.",
            "Roast for 15-20 minutes, stirring halfway through, until tender and golden.",
            "Garnish with fresh parsley before serving."
        ],
        "ingredients": [
            {"name": "shiitake mushrooms", "amount": 150, "unit": "g"},
            {"name": "reishi mushrooms", "amount": 100, "unit": "g"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "dried rosemary", "amount": 1, "unit": "tsp"},
            {"name": "fresh parsley", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Mushroom & Lentil Stew",
        "author": "Longevity Advice",
        "description": "A hearty stew with mixed mushrooms and lentils in vegetable broth with thyme. Rich in plant protein and fiber.",
        "category": "high-fiber",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 45,
        "calories": 280,
        "macros": {"protein_g": 16, "carbs_g": 34, "fat_g": 8, "fiber_g": 12},
        "nutrients": {"iron_mg": 5, "potassium_mg": 600, "folate_mcg": 200},
        "health_benefits": ["high-fiber", "gut-friendly", "heart-healthy"],
        "allergens": [],
        "instructions": [
            "In a large pot, heat olive oil over medium heat. Sauté the onion and carrots until softened.",
            "Add the mushrooms and cook for another 5 minutes until they release their moisture.",
            "Add the lentils, vegetable broth, thyme, salt, and pepper. Bring to a boil.",
            "Reduce heat and simmer for 25-30 minutes, or until lentils are tender.",
            "Serve hot, garnished with fresh parsley if desired."
        ],
        "ingredients": [
            {"name": "lentils", "amount": 1, "unit": "cup"},
            {"name": "shiitake mushrooms", "amount": 200, "unit": "g"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "carrots", "amount": 2, "unit": "pcs"},
            {"name": "vegetable broth", "amount": 4, "unit": "cup"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "dried thyme", "amount": 1, "unit": "tsp"},
        ]
    },
    {
        "name": "Oven-Baked Wild Salmon with Rosemary",
        "author": "Longevity Advice",
        "description": "Wild Pacific salmon baked with garlic, rosemary, and lemon. Rich in omega-3 fatty acids for heart and brain health.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 2,
        "prep_time_min": 25,
        "calories": 350,
        "macros": {"protein_g": 36, "carbs_g": 2, "fat_g": 20, "fiber_g": 0},
        "nutrients": {"omega_3_g": 2.5, "vitamin_d_mcg": 15, "selenium_mcg": 40},
        "health_benefits": ["heart-healthy", "brain-health", "anti-inflammatory"],
        "allergens": ["fish"],
        "instructions": [
            "Preheat your oven to 375°F (190°C).",
            "Place the salmon filets on a baking sheet lined with parchment paper.",
            "In a small bowl, mix the garlic, olive oil, rosemary, lemon juice, salt, and pepper. Spread the mixture over the salmon.",
            "Bake for 15-20 minutes, or until the salmon is cooked through and flakes easily with a fork."
        ],
        "ingredients": [
            {"name": "salmon fillet", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "fresh rosemary", "amount": 1, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
        ]
    },
    {
        "name": "Carrot & Garlic Hummus",
        "author": "Longevity Advice",
        "description": "A longevity twist on hummus with steamed carrots and raw garlic, served with carrot sticks for dipping.",
        "category": "gut-friendly",
        "meal_type": "snack",
        "servings": 4,
        "prep_time_min": 15,
        "calories": 180,
        "macros": {"protein_g": 5, "carbs_g": 14, "fat_g": 12, "fiber_g": 4},
        "nutrients": {"vitamin_a_mcg": 600, "vitamin_c_mg": 8, "calcium_mg": 40},
        "health_benefits": ["gut-friendly", "anti-inflammatory", "heart-healthy"],
        "allergens": ["sesame"],
        "instructions": [
            "Steam the carrots until tender (about 5-7 minutes). Allow to cool slightly.",
            "In a food processor, combine the steamed carrots, garlic, tahini, olive oil, lemon juice, salt, and pepper.",
            "Blend until smooth.",
            "Serve with raw carrot sticks for dipping, and garnish with parsley if desired."
        ],
        "ingredients": [
            {"name": "carrots", "amount": 2, "unit": "cup"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
            {"name": "tahini", "amount": 0.25, "unit": "cup"},
            {"name": "olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 2, "unit": "tbsp"},
            {"name": "fresh parsley", "amount": 1, "unit": "tbsp"},
        ]
    },
]

# 3. Insert all recipes
for i, r in enumerate(recipes, 1):
    macros = r["macros"]
    nutrients = r.get("nutrients", {})
    
    db_recipe = RecipeDB(
        name=r["name"],
        description=r["description"],
        category=r["category"],
        meal_type=r["meal_type"],
        servings=r["servings"],
        prep_time_min=r["prep_time_min"],
        calories=r["calories"],
        protein_g=macros["protein_g"],
        carbs_g=macros["carbs_g"],
        fat_g=macros["fat_g"],
        fiber_g=macros["fiber_g"],
        nutrients_json=json.dumps(nutrients),
        instructions_json=json.dumps(r["instructions"]),
        health_benefits_json=json.dumps(r["health_benefits"]),
        allergens_json=json.dumps(r["allergens"]),
        author=r.get("author", "Elizabeth Rider"),
        image_url=r.get("image_url", RECIPE_IMAGES.get(r["name"], "")),
    )
    
    for ing in r["ingredients"]:
        db_recipe.ingredients.append(
            IngredientDB(name=ing["name"], amount=ing["amount"], unit=ing["unit"])
        )
    
    db.add(db_recipe)

db.commit()
print(f"Added {len(recipes)} Blue Zone recipes successfully!")
db.close()
