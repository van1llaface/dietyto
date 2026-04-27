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

# Recipes sourced from Blue Zones (bluezones.com), NutritionFacts.org (Dr. Greger),
# and Valter Longo's Longevity Diet — adapted with Lithuanian ingredients.
RECIPES = [
    # ──────────────────────────────────────────────
    # 1. Based on: Three-Bean Soup with Turmeric and Lentils
    #    Source: NutritionFacts.org / How Not to Diet Cookbook (Dr. Greger & Robin Robertson)
    #    Adapted: Lithuanian version with local white beans (pupelės)
    # ──────────────────────────────────────────────
    {
        "name": "Three-Bean Soup with Turmeric",
        "description": "From Dr. Greger's How Not to Diet Cookbook — turmeric casts a golden glow on this hearty soup with three kinds of beans and lentils. Adapted with Lithuanian white beans.",
        "category": "anti-inflammatory",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 50,
        "calories": 310,
        "protein_g": 18, "carbs_g": 46, "fat_g": 3, "fiber_g": 15,
        "nutrients": {"iron_mg": 6.5, "potassium_mg": 800, "vitamin_c_mg": 25},
        "instructions": [
            "Heat 60ml water in a large pot over medium heat.",
            "Add chopped red onion and sliced garlic, cook 5 min to soften.",
            "Stir in turmeric, coriander, cumin, and brown lentils.",
            "Add vegetable broth and bring to a boil.",
            "Lower heat, add kidney beans, chickpeas, and white beans.",
            "Simmer 30-40 min until lentils are tender.",
            "Add spinach, parsley, spring onions, mint, and black pepper.",
            "Cook 10 more min. Serve hot.",
        ],
        "health_benefits": ["anti-inflammatory turmeric", "plant protein from 3 beans", "high fiber for gut health"],
        "allergens": [],
        "ingredients": [
            {"name": "red onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 4, "unit": "pcs"},
            {"name": "ground turmeric", "amount": 1, "unit": "tbsp"},
            {"name": "ground coriander", "amount": 1, "unit": "tsp"},
            {"name": "ground cumin", "amount": 0.5, "unit": "tsp"},
            {"name": "brown lentils (dried)", "amount": 100, "unit": "g"},
            {"name": "vegetable broth", "amount": 1700, "unit": "ml"},
            {"name": "kidney beans (cooked)", "amount": 250, "unit": "g"},
            {"name": "chickpeas (cooked)", "amount": 250, "unit": "g"},
            {"name": "white beans (cooked, pupelės)", "amount": 250, "unit": "g"},
            {"name": "fresh spinach", "amount": 150, "unit": "g"},
            {"name": "fresh parsley", "amount": 1, "unit": "handful"},
            {"name": "spring onion", "amount": 3, "unit": "pcs"},
        ],
    },
    # ──────────────────────────────────────────────
    # 2. Based on: Basic BROL (Barley, Rye, Oats, and Lentils)
    #    Source: NutritionFacts.org / How Not to Diet Cookbook (Dr. Greger)
    #    Adapted: Lithuanian grains bowl with kefir and forest berries
    # ──────────────────────────────────────────────
    {
        "name": "BROL Bowl with Forest Berries",
        "description": "Dr. Greger's BROL (Barley, Rye, Oats, Lentils) — the ultimate longevity grain mix. Served with Lithuanian kefir and wild forest berries for antioxidants and probiotics.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast",
        "servings": 2,
        "prep_time_min": 40,
        "calories": 340,
        "protein_g": 14, "carbs_g": 58, "fat_g": 5, "fiber_g": 12,
        "nutrients": {"iron_mg": 4.5, "magnesium_mg": 95, "zinc_mg": 3.0},
        "instructions": [
            "Rinse black lentils, hulled barley, rye berries, and oat groats.",
            "Pressure cook lentils in 240ml water on high, natural release.",
            "Combine barley, rye, and oat groats with 720ml water.",
            "Pressure cook 30 min or simmer on stovetop 50 min.",
            "Combine cooked lentils with cooked grains.",
            "Serve in bowls, top with kefir and mixed forest berries.",
            "Sprinkle with ground flaxseed.",
        ],
        "health_benefits": ["whole grain fiber", "antioxidant-packed black lentils", "probiotic kefir"],
        "allergens": ["gluten", "lactose"],
        "ingredients": [
            {"name": "black lentils (dried)", "amount": 80, "unit": "g"},
            {"name": "hulled barley", "amount": 80, "unit": "g"},
            {"name": "rye berries", "amount": 80, "unit": "g"},
            {"name": "oat groats", "amount": 80, "unit": "g"},
            {"name": "kefir (plain)", "amount": 150, "unit": "ml"},
            {"name": "mixed forest berries", "amount": 100, "unit": "g"},
            {"name": "ground flaxseed", "amount": 1, "unit": "tbsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 3. Based on: Ribollita with White Beans and Kale
    #    Source: NutritionFacts.org / How Not to Diet Cookbook (Dr. Greger & Robin Robertson)
    #    Adapted: Lithuanian version with savoy cabbage and dark rye bread
    # ──────────────────────────────────────────────
    {
        "name": "Ribollita with White Beans & Cabbage",
        "description": "From Dr. Greger's How Not to Diet Cookbook — a rustic Italian peasant soup that tastes even better reheated. Adapted with Lithuanian savoy cabbage and served with dark rye bread.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 55,
        "calories": 280,
        "protein_g": 14, "carbs_g": 44, "fat_g": 3, "fiber_g": 11,
        "nutrients": {"iron_mg": 5.0, "potassium_mg": 750, "vitamin_c_mg": 60},
        "instructions": [
            "Heat 60ml water in a large pot. Add onion, garlic, and carrots.",
            "Cover and cook 5 min, stirring occasionally, until softened.",
            "Add vegetable broth, celery, potatoes, cabbage, and kale.",
            "Add diced tomatoes, white beans, red pepper flakes, rosemary, and bay leaf.",
            "Bring to boil, then lower heat and simmer 45 min until very soft.",
            "Remove rosemary sprig and bay leaf.",
            "Stir in nutritional yeast. Serve hot with dark rye bread.",
        ],
        "health_benefits": ["Blue Zone peasant food", "high plant protein", "fiber-rich for gut microbiome"],
        "allergens": ["gluten"],
        "ingredients": [
            {"name": "red onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 4, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "vegetable broth", "amount": 1400, "unit": "ml"},
            {"name": "celery", "amount": 2, "unit": "pcs"},
            {"name": "potato", "amount": 2, "unit": "pcs"},
            {"name": "savoy cabbage", "amount": 200, "unit": "g"},
            {"name": "kale", "amount": 150, "unit": "g"},
            {"name": "diced tomatoes (canned)", "amount": 400, "unit": "g"},
            {"name": "white beans (cooked, pupelės)", "amount": 400, "unit": "g"},
            {"name": "red pepper flakes", "amount": 0.5, "unit": "tsp"},
            {"name": "fresh rosemary", "amount": 1, "unit": "pcs"},
            {"name": "bay leaf", "amount": 1, "unit": "pcs"},
            {"name": "nutritional yeast", "amount": 3, "unit": "tbsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 4. Based on: Rainbow Root Veggie Stew
    #    Source: NutritionFacts.org (Dusty & Erin Stanczyk)
    #    Adapted: Lithuanian root vegetables with beets and red lentils
    # ──────────────────────────────────────────────
    {
        "name": "Rainbow Root Veggie Stew",
        "description": "From NutritionFacts.org — packed with Lithuanian root vegetables and red lentils. Rich in phytonutrients. Beets provide natural nitrates proven to lower blood pressure within hours.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 40,
        "calories": 290,
        "protein_g": 13, "carbs_g": 50, "fat_g": 2, "fiber_g": 12,
        "nutrients": {"iron_mg": 5.5, "potassium_mg": 900, "vitamin_c_mg": 30},
        "instructions": [
            "Dice onion, mince garlic. Cube beets, carrots, and potatoes.",
            "Tear kale into pieces. Rinse red lentils.",
            "Place all vegetables, lentils, and vegetable broth in a large pot.",
            "Bring to boil, reduce to medium-low, simmer 30 min until soft.",
            "Season with black pepper.",
            "Serve topped with a sprinkle of nutritional yeast.",
        ],
        "health_benefits": ["beet nitrates lower blood pressure", "phytonutrient diversity", "high fiber"],
        "allergens": [],
        "ingredients": [
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
            {"name": "beet", "amount": 300, "unit": "g"},
            {"name": "carrot", "amount": 4, "unit": "pcs"},
            {"name": "potato", "amount": 2, "unit": "pcs"},
            {"name": "celery", "amount": 4, "unit": "pcs"},
            {"name": "kale", "amount": 150, "unit": "g"},
            {"name": "red lentils (dried)", "amount": 100, "unit": "g"},
            {"name": "vegetable broth", "amount": 1000, "unit": "ml"},
            {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 5. Based on: Baked Carrot Cake Oatmeal
    #    Source: NutritionFacts.org / How Not to Age Cookbook (Dr. Greger)
    #    Adapted: Lithuanian version with hemp milk and local honey
    # ──────────────────────────────────────────────
    {
        "name": "Baked Carrot Cake Oatmeal",
        "description": "From Dr. Greger's How Not to Age Cookbook — a savory baked breakfast with oats, flax, chia, and carrots. Prep night before, pop in oven in the morning.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast",
        "servings": 4,
        "prep_time_min": 40,
        "calories": 260,
        "protein_g": 9, "carbs_g": 42, "fat_g": 8, "fiber_g": 7,
        "nutrients": {"magnesium_mg": 80, "iron_mg": 3.0, "omega_3_g": 2.0},
        "instructions": [
            "Preheat oven to 190°C. Line a 20cm square pan with parchment.",
            "Combine oats, ground chia, ground flaxseed, grated carrot, walnuts, and cinnamon.",
            "Add plant milk, date syrup, and vanilla. Stir well.",
            "Transfer to pan and smooth evenly.",
            "Bake 30 min until golden brown and set.",
            "Cool 10 min before serving.",
        ],
        "health_benefits": ["omega-3 from flax and chia", "Daily Dozen breakfast", "low glycemic index"],
        "allergens": ["gluten"],
        "ingredients": [
            {"name": "rolled oats", "amount": 100, "unit": "g"},
            {"name": "ground chia seeds", "amount": 2, "unit": "tbsp"},
            {"name": "ground flaxseed", "amount": 2, "unit": "tbsp"},
            {"name": "carrot", "amount": 1, "unit": "pcs"},
            {"name": "walnut", "amount": 30, "unit": "g"},
            {"name": "ground cinnamon", "amount": 1.5, "unit": "tsp"},
            {"name": "plant-based milk", "amount": 350, "unit": "ml"},
            {"name": "date syrup or raw honey", "amount": 3, "unit": "tbsp"},
            {"name": "vanilla extract", "amount": 1, "unit": "tsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 6. Based on: Roasted Ratatouille
    #    Source: Blue Zones Kitchen One Pot Meals (Dan Buettner)
    #    Adapted: Lithuanian summer vegetables
    # ──────────────────────────────────────────────
    {
        "name": "Roasted Ratatouille",
        "description": "From The Blue Zones Kitchen — a Provençal classic combining summer nightshades in a savory stew. Zucchini, eggplant, peppers, and tomatoes roasted with herbs.",
        "category": "anti-inflammatory",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 50,
        "calories": 220,
        "protein_g": 4, "carbs_g": 18, "fat_g": 14, "fiber_g": 6,
        "nutrients": {"vitamin_c_mg": 80, "potassium_mg": 600, "vitamin_a_iu": 1500},
        "instructions": [
            "Preheat oven to 190°C.",
            "Cut zucchini and eggplant into thin rounds, sprinkle with salt, toss with olive oil.",
            "Blend bell pepper, onion, tomatoes, garlic, and half the herbs into a smooth puree.",
            "Pour half the puree into a round casserole dish.",
            "Arrange zucchini and eggplant slices on top in alternating scallop pattern.",
            "Pour remaining puree over top, sprinkle rest of herbs.",
            "Bake 40 min. Drizzle remaining olive oil, rest 5 min before serving.",
        ],
        "health_benefits": ["Mediterranean diet staple", "lycopene from tomatoes", "anti-inflammatory herbs"],
        "allergens": [],
        "ingredients": [
            {"name": "zucchini", "amount": 2, "unit": "pcs"},
            {"name": "eggplant", "amount": 1, "unit": "pcs"},
            {"name": "red bell pepper", "amount": 1, "unit": "pcs"},
            {"name": "onion", "amount": 0.5, "unit": "pcs"},
            {"name": "tomato", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 2, "unit": "pcs"},
            {"name": "fresh thyme", "amount": 4, "unit": "pcs"},
            {"name": "fresh oregano", "amount": 1, "unit": "tbsp"},
            {"name": "fresh rosemary", "amount": 1, "unit": "tsp"},
            {"name": "extra virgin olive oil", "amount": 4, "unit": "tbsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 7. Based on: Orange and Spice Overnight Oats
    #    Source: Blue Zones / Plant Powered Plus (Dr. Will Bulsiewicz)
    #    Adapted: Lithuanian version with kefir and forest berries
    # ──────────────────────────────────────────────
    {
        "name": "Overnight Oats with Kefir & Berries",
        "description": "Inspired by Blue Zones overnight oats by Dr. Bulsiewicz — prep night before, eat in the morning. Lithuanian version uses kefir for probiotics and local forest berries.",
        "category": "gut-friendly",
        "meal_type": "breakfast",
        "servings": 2,
        "prep_time_min": 10,
        "calories": 300,
        "protein_g": 11, "carbs_g": 48, "fat_g": 8, "fiber_g": 8,
        "nutrients": {"omega_3_g": 1.8, "calcium_mg": 250, "magnesium_mg": 70},
        "instructions": [
            "Combine oats, ground flaxseed, cinnamon, and cardamom in a bowl.",
            "Add kefir, vanilla, and honey. Stir to combine.",
            "Divide into 2 mason jars or bowls.",
            "Refrigerate at least 30 min or overnight.",
            "Top with mixed forest berries and hemp seeds before serving.",
        ],
        "health_benefits": ["probiotic kefir", "omega-3 from flaxseed", "overnight prep supports fasting window"],
        "allergens": ["gluten", "lactose"],
        "ingredients": [
            {"name": "rolled oats", "amount": 80, "unit": "g"},
            {"name": "ground flaxseed", "amount": 2, "unit": "tbsp"},
            {"name": "ground cinnamon", "amount": 0.5, "unit": "tsp"},
            {"name": "ground cardamom", "amount": 0.25, "unit": "tsp"},
            {"name": "kefir (plain)", "amount": 250, "unit": "ml"},
            {"name": "vanilla extract", "amount": 1, "unit": "tsp"},
            {"name": "raw honey", "amount": 2, "unit": "tsp"},
            {"name": "mixed forest berries", "amount": 100, "unit": "g"},
            {"name": "hemp seeds", "amount": 1, "unit": "tbsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 8. Based on: Chickpea Stew with Roasted Cauliflower & Root Vegetables
    #    Source: Blue Zones / The Ikaria Way (Diane Kochilas)
    #    Adapted: Lithuanian root vegetables with cumin-turmeric spice
    # ──────────────────────────────────────────────
    {
        "name": "Ikarian Chickpea & Root Vegetable Stew",
        "description": "From The Ikaria Way cookbook featured on Blue Zones — chickpeas with honey-roasted cauliflower and root vegetables. Ikaria is a Blue Zone where people forget to die.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 45,
        "calories": 380,
        "protein_g": 15, "carbs_g": 52, "fat_g": 12, "fiber_g": 13,
        "nutrients": {"iron_mg": 5.5, "potassium_mg": 700, "vitamin_c_mg": 45},
        "instructions": [
            "Preheat oven to 200°C. Line a baking tray with parchment.",
            "Whisk olive oil, cumin, turmeric, smoked paprika, and honey in a bowl.",
            "Toss cauliflower florets, carrots, and onion quarters in spice mixture.",
            "Spread on tray, roast 20 min until charred at edges.",
            "Meanwhile, sauté garlic in olive oil. Add chickpeas and tomato paste.",
            "Add rosemary and vegetable broth. Simmer 15 min.",
            "Combine roasted vegetables with chickpeas. Serve hot.",
        ],
        "health_benefits": ["Blue Zone staple food", "anti-inflammatory turmeric-cumin combo", "plant protein"],
        "allergens": [],
        "ingredients": [
            {"name": "chickpeas (cooked)", "amount": 400, "unit": "g"},
            {"name": "cauliflower", "amount": 300, "unit": "g"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "red onion", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 4, "unit": "pcs"},
            {"name": "tomato paste", "amount": 1, "unit": "tbsp"},
            {"name": "extra virgin olive oil", "amount": 3, "unit": "tbsp"},
            {"name": "ground cumin", "amount": 2, "unit": "tsp"},
            {"name": "ground turmeric", "amount": 1, "unit": "tsp"},
            {"name": "smoked paprika", "amount": 1, "unit": "tsp"},
            {"name": "raw honey", "amount": 1, "unit": "tbsp"},
            {"name": "fresh rosemary", "amount": 2, "unit": "pcs"},
            {"name": "vegetable broth", "amount": 500, "unit": "ml"},
        ],
    },
    # ──────────────────────────────────────────────
    # 9. Based on: Panchita's Gallo Pinto
    #    Source: Blue Zones (centenarian Panchita Castillo, Costa Rica)
    #    Adapted: Lithuanian version with buckwheat instead of rice
    # ──────────────────────────────────────────────
    {
        "name": "Lithuanian Gallo Pinto",
        "description": "Based on centenarian Panchita Castillo's recipe from Costa Rica's Blue Zone — black beans and grains. Lithuanian version swaps rice for buckwheat for extra rutin.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 25,
        "calories": 350,
        "protein_g": 14, "carbs_g": 58, "fat_g": 6, "fiber_g": 12,
        "nutrients": {"iron_mg": 4.5, "magnesium_mg": 110, "potassium_mg": 650},
        "instructions": [
            "Cook buckwheat until warm and fluffy.",
            "Dice onion and mince garlic.",
            "Warm olive oil in a saucepan, sauté onion 3 min until softened.",
            "Add garlic, cook until fragrant (20 seconds).",
            "Pour in black beans and water. Bring to a simmer.",
            "Gently stir in buckwheat, salt, and pepper until hot (2 min).",
            "Stir in fresh dill and sliced spring onion. Serve.",
        ],
        "health_benefits": ["Blue Zone centenarian recipe", "beans are #1 longevity food", "rutin from buckwheat"],
        "allergens": [],
        "ingredients": [
            {"name": "buckwheat (raw)", "amount": 100, "unit": "g"},
            {"name": "black beans (cooked)", "amount": 250, "unit": "g"},
            {"name": "onion", "amount": 0.5, "unit": "pcs"},
            {"name": "garlic", "amount": 1, "unit": "pcs"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "fresh dill", "amount": 1, "unit": "handful"},
            {"name": "spring onion", "amount": 2, "unit": "pcs"},
        ],
    },
    # ──────────────────────────────────────────────
    # 10. Based on: Sweet Potato Breakfast Bowls
    #     Source: Blue Zones Kitchen One Pot Meals (Dan Buettner)
    #     Adapted: Lithuanian version with kefir and walnuts
    # ──────────────────────────────────────────────
    {
        "name": "Sweet Potato Breakfast Bowl",
        "description": "From The Blue Zones Kitchen — whipped sweet potato with warm spices. Lithuanian version uses kefir instead of coconut yogurt and tops with local walnuts and flaxseed.",
        "category": "antioxidant-rich",
        "meal_type": "breakfast",
        "servings": 2,
        "prep_time_min": 15,
        "calories": 280,
        "protein_g": 7, "carbs_g": 42, "fat_g": 10, "fiber_g": 6,
        "nutrients": {"vitamin_a_iu": 18000, "potassium_mg": 500, "vitamin_c_mg": 20},
        "instructions": [
            "Bake sweet potatoes until very soft (or microwave 8 min). Peel.",
            "Put sweet potato, kefir, olive oil, honey, ginger, vanilla, and cinnamon in a bowl.",
            "Blend with immersion blender until smooth.",
            "Divide into 2 bowls.",
            "Top with chopped walnuts and ground flaxseed.",
        ],
        "health_benefits": ["beta-carotene from sweet potato", "probiotic kefir", "anti-inflammatory ginger"],
        "allergens": ["lactose"],
        "ingredients": [
            {"name": "sweet potato", "amount": 2, "unit": "pcs"},
            {"name": "kefir (plain)", "amount": 60, "unit": "ml"},
            {"name": "extra virgin olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "raw honey", "amount": 1, "unit": "tbsp"},
            {"name": "fresh grated ginger", "amount": 0.5, "unit": "tsp"},
            {"name": "vanilla extract", "amount": 0.25, "unit": "tsp"},
            {"name": "ground cinnamon", "amount": 0.25, "unit": "tsp"},
            {"name": "walnut", "amount": 2, "unit": "tbsp"},
            {"name": "ground flaxseed", "amount": 2, "unit": "tsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 11. Based on: Lemon Vinaigrette Wheat Berry Salad
    #     Source: Blue Zones / Make Better Food
    #     Adapted: Lithuanian version with rye berries instead of wheat
    # ──────────────────────────────────────────────
    {
        "name": "Rye Berry Salad with Lemon Vinaigrette",
        "description": "Inspired by Blue Zones wheat berry salad — whole grains are a top Four Always food in Blue Zones. Lithuanian version uses rye berries for a local twist.",
        "category": "heart-healthy",
        "meal_type": "lunch",
        "servings": 4,
        "prep_time_min": 80,
        "calories": 320,
        "protein_g": 10, "carbs_g": 48, "fat_g": 10, "fiber_g": 8,
        "nutrients": {"iron_mg": 3.5, "magnesium_mg": 75, "vitamin_c_mg": 50},
        "instructions": [
            "Bring vegetable broth to boil. Add rye berries, simmer 1 hour until soft.",
            "Preheat oven to 220°C.",
            "Toss brussels sprouts and spring onion with olive oil, roast 20 min.",
            "Whisk lemon juice, olive oil, salt, and pepper for dressing.",
            "Drain rye berries. Combine with roasted vegetables.",
            "Add pine nuts and raisins. Toss with dressing. Serve warm or cold.",
        ],
        "health_benefits": ["whole grain fiber", "Blue Zones Four Always food", "regulates blood sugar"],
        "allergens": ["gluten"],
        "ingredients": [
            {"name": "rye berries", "amount": 150, "unit": "g"},
            {"name": "vegetable broth", "amount": 700, "unit": "ml"},
            {"name": "brussels sprout", "amount": 300, "unit": "g"},
            {"name": "spring onion", "amount": 2, "unit": "pcs"},
            {"name": "extra virgin olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
            {"name": "pine nuts", "amount": 30, "unit": "g"},
            {"name": "golden raisins", "amount": 40, "unit": "g"},
        ],
    },
    # ──────────────────────────────────────────────
    # 12. Based on: Ikarian Longevity Stew with Black-Eyed Peas
    #     Source: Blue Zones (Dan Buettner, Ikaria Blue Zone)
    #     Adapted: Lithuanian version with local vegetables
    # ──────────────────────────────────────────────
    {
        "name": "Ikarian Longevity Stew",
        "description": "The famous Blue Zones longevity stew from the Greek island of Ikaria — black-eyed peas slow-cooked with vegetables and olive oil. A dish associated with people who forget to die.",
        "category": "anti-inflammatory",
        "meal_type": "dinner",
        "servings": 4,
        "prep_time_min": 50,
        "calories": 300,
        "protein_g": 14, "carbs_g": 42, "fat_g": 9, "fiber_g": 11,
        "nutrients": {"iron_mg": 5.0, "potassium_mg": 700, "magnesium_mg": 80},
        "instructions": [
            "Soak black-eyed peas overnight, drain and rinse.",
            "Dice onion, carrots, and celery. Mince garlic.",
            "Heat olive oil in a pot. Sauté onion and garlic 5 min.",
            "Add black-eyed peas, diced tomatoes, carrots, and celery.",
            "Add vegetable broth, bay leaf, and oregano.",
            "Bring to boil, then simmer 40 min until peas are tender.",
            "Season with salt, pepper, and a squeeze of lemon.",
        ],
        "health_benefits": ["Ikarian Blue Zone recipe", "beans lower LDL cholesterol", "longevity-associated food"],
        "allergens": [],
        "ingredients": [
            {"name": "black-eyed peas (dried)", "amount": 250, "unit": "g"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "celery", "amount": 2, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "diced tomatoes (canned)", "amount": 400, "unit": "g"},
            {"name": "extra virgin olive oil", "amount": 2, "unit": "tbsp"},
            {"name": "vegetable broth", "amount": 500, "unit": "ml"},
            {"name": "bay leaf", "amount": 1, "unit": "pcs"},
            {"name": "dried oregano", "amount": 1, "unit": "tsp"},
            {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 13. Based on: Valter Longo's Longevity Diet fish recommendation
    #     Source: The Longevity Diet (Dr. Valter Longo)
    #     Low-mercury fish 2-3x per week, herring is ideal
    # ──────────────────────────────────────────────
    {
        "name": "Herring & Buckwheat Bowl",
        "description": "Based on Dr. Valter Longo's Longevity Diet rule: eat low-mercury fish 2-3x per week. Baltic herring with buckwheat, fermented cucumber, and hemp seeds — a Lithuanian longevity classic.",
        "category": "heart-healthy",
        "meal_type": "lunch",
        "servings": 1,
        "prep_time_min": 20,
        "calories": 380,
        "protein_g": 22, "carbs_g": 42, "fat_g": 14, "fiber_g": 6,
        "nutrients": {"omega_3_g": 2.5, "vitamin_d_mcg": 8, "iron_mg": 3.0},
        "instructions": [
            "Cook buckwheat in water for 15 min until fluffy.",
            "Slice fermented cucumbers and red onion thinly.",
            "Place herring fillet over warm buckwheat.",
            "Top with hemp seeds and cucumber slices.",
            "Drizzle with flaxseed oil and fresh dill.",
        ],
        "health_benefits": ["omega-3 from low-mercury herring", "Longo Diet fish rule", "probiotic fermented cucumbers"],
        "allergens": ["fish"],
        "ingredients": [
            {"name": "buckwheat (raw)", "amount": 80, "unit": "g"},
            {"name": "herring fillet (pickled or smoked)", "amount": 100, "unit": "g"},
            {"name": "fermented cucumber", "amount": 2, "unit": "pcs"},
            {"name": "hemp seeds", "amount": 1, "unit": "tbsp"},
            {"name": "flaxseed oil", "amount": 1, "unit": "tsp"},
            {"name": "fresh dill", "amount": 1, "unit": "handful"},
            {"name": "red onion", "amount": 0.25, "unit": "pcs"},
        ],
    },
    # ──────────────────────────────────────────────
    # 14. Based on: Valter Longo's Longevity Diet — sardines
    #     Source: The Longevity Diet (Dr. Valter Longo)
    #     Sardines on rye — Lithuanian adaptation
    # ──────────────────────────────────────────────
    {
        "name": "Sardine & Sauerkraut Rye Toast",
        "description": "Dr. Longo recommends sardines as ideal longevity fish — high in omega-3, calcium from bones, and vitamin D. Served on Lithuanian dark rye with probiotic sauerkraut.",
        "category": "anti-inflammatory",
        "meal_type": "snack",
        "servings": 1,
        "prep_time_min": 5,
        "calories": 280,
        "protein_g": 20, "carbs_g": 22, "fat_g": 12, "fiber_g": 4,
        "nutrients": {"omega_3_g": 1.8, "calcium_mg": 250, "vitamin_d_mcg": 8},
        "instructions": [
            "Lay dark rye bread slices flat.",
            "Drain sardines and arrange on bread.",
            "Top generously with sauerkraut.",
            "Add sliced cucumber and a squeeze of lemon.",
            "Sprinkle with black pepper and fresh dill.",
        ],
        "health_benefits": ["calcium from sardine bones", "probiotics from sauerkraut", "omega-3 and vitamin D"],
        "allergens": ["gluten", "fish"],
        "ingredients": [
            {"name": "dark rye bread", "amount": 2, "unit": "pcs"},
            {"name": "sardines in olive oil (canned)", "amount": 100, "unit": "g"},
            {"name": "sauerkraut", "amount": 60, "unit": "g"},
            {"name": "fresh cucumber", "amount": 0.5, "unit": "pcs"},
            {"name": "lemon juice", "amount": 1, "unit": "tsp"},
            {"name": "fresh dill", "amount": 1, "unit": "handful"},
        ],
    },
    # ──────────────────────────────────────────────
    # 15. Based on: Kefir Šaltibarščiai (Lithuanian traditional)
    #     Source: Traditional Lithuanian recipe, adapted per Longo's kefir recommendation
    #     Longo Diet: fermented foods for gut-brain axis
    # ──────────────────────────────────────────────
    {
        "name": "Kefir Šaltibarščiai",
        "description": "Lithuania's iconic cold beet soup — adapted for longevity with kefir instead of sour cream, per Dr. Longo's advice on fermented foods. Probiotic, anti-inflammatory, and refreshing.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 2,
        "prep_time_min": 15,
        "calories": 220,
        "protein_g": 12, "carbs_g": 22, "fat_g": 8, "fiber_g": 4,
        "nutrients": {"vitamin_c_mg": 20, "calcium_mg": 300, "potassium_mg": 500},
        "instructions": [
            "Boil or roast beets until tender. Cool completely and dice finely.",
            "Slice cucumber and radishes thin.",
            "Pour kefir into a large bowl, add beets and vegetables.",
            "Halve hard-boiled eggs and place on top.",
            "Season with salt, garnish generously with dill.",
            "Refrigerate at least 30 min before serving.",
        ],
        "health_benefits": ["probiotic kefir", "anti-inflammatory beets", "supports gut microbiome"],
        "allergens": ["lactose"],
        "ingredients": [
            {"name": "kefir (plain)", "amount": 500, "unit": "ml"},
            {"name": "beet", "amount": 2, "unit": "pcs"},
            {"name": "fresh cucumber", "amount": 1, "unit": "pcs"},
            {"name": "radishes", "amount": 4, "unit": "pcs"},
            {"name": "egg", "amount": 2, "unit": "pcs"},
            {"name": "fresh dill", "amount": 1, "unit": "handful"},
            {"name": "spring onion", "amount": 2, "unit": "pcs"},
        ],
    },
    # ──────────────────────────────────────────────
    # 16. Based on: Sauerkraut & Buckwheat Soup (Lithuanian traditional)
    #     Source: Lithuanian peasant food, confirmed by Blue Zones fermented food research
    #     Buettner: "Fermented foods are central to every Blue Zone diet"
    # ──────────────────────────────────────────────
    {
        "name": "Sauerkraut & Buckwheat Soup",
        "description": "A Lithuanian peasant staple that Blue Zones research confirms is gut-healing. Probiotic sauerkraut with buckwheat — fermented foods are central to every Blue Zone diet.",
        "category": "gut-friendly",
        "meal_type": "lunch",
        "servings": 3,
        "prep_time_min": 35,
        "calories": 210,
        "protein_g": 8, "carbs_g": 35, "fat_g": 4, "fiber_g": 8,
        "nutrients": {"vitamin_c_mg": 30, "iron_mg": 2.8, "potassium_mg": 500},
        "instructions": [
            "Rinse sauerkraut lightly if very sour.",
            "Sauté onion and carrot in olive oil for 5 min.",
            "Add sauerkraut, potato, and vegetable broth.",
            "Bring to boil, add buckwheat.",
            "Simmer 20 min until buckwheat and potato are soft.",
            "Season with black pepper and fresh dill.",
        ],
        "health_benefits": ["probiotic sauerkraut", "rutin from buckwheat", "Blue Zone fermented food"],
        "allergens": [],
        "ingredients": [
            {"name": "sauerkraut", "amount": 200, "unit": "g"},
            {"name": "buckwheat (raw)", "amount": 60, "unit": "g"},
            {"name": "potato", "amount": 1, "unit": "pcs"},
            {"name": "carrot", "amount": 1, "unit": "pcs"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "vegetable broth", "amount": 800, "unit": "ml"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
        ],
    },
    # ──────────────────────────────────────────────
    # 17. Based on: Forest Mushroom Stew
    #     Source: NutritionFacts.org research on ergothioneine + Lithuanian tradition
    #     Greger: "Mushrooms are the only dietary source of ergothioneine"
    # ──────────────────────────────────────────────
    {
        "name": "Forest Mushroom & White Bean Stew",
        "description": "Based on Dr. Greger's research: mushrooms are the only dietary source of ergothioneine — a longevity compound. Lithuanian forest mushrooms with white beans for plant protein.",
        "category": "anti-inflammatory",
        "meal_type": "dinner",
        "servings": 2,
        "prep_time_min": 40,
        "calories": 320,
        "protein_g": 16, "carbs_g": 42, "fat_g": 8, "fiber_g": 12,
        "nutrients": {"iron_mg": 5.5, "zinc_mg": 3.0, "potassium_mg": 700},
        "instructions": [
            "Soak dried mushrooms in 300ml warm water for 20 min. Reserve liquid.",
            "Dice onion, carrot, and garlic.",
            "Heat olive oil in pot, sauté onion and carrot 5 min.",
            "Add garlic and mushrooms, cook 3 min.",
            "Add white beans, mushroom soaking liquid, and broth.",
            "Simmer 20 min. Season with thyme, salt, and pepper.",
            "Serve with dark rye bread.",
        ],
        "health_benefits": ["ergothioneine from mushrooms", "meat-free mTOR-safe protein", "high fiber"],
        "allergens": ["gluten"],
        "ingredients": [
            {"name": "dried forest mushrooms (baravykai)", "amount": 30, "unit": "g"},
            {"name": "white beans (cooked, pupelės)", "amount": 300, "unit": "g"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "onion", "amount": 1, "unit": "pcs"},
            {"name": "garlic", "amount": 3, "unit": "pcs"},
            {"name": "vegetable broth", "amount": 400, "unit": "ml"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "fresh thyme", "amount": 3, "unit": "pcs"},
        ],
    },
    # ──────────────────────────────────────────────
    # 18. Based on: Valter Longo's Longevity Diet — mackerel
    #     Source: The Longevity Diet (Dr. Valter Longo)
    #     Mackerel is one of the richest omega-3 sources
    # ──────────────────────────────────────────────
    {
        "name": "Mackerel & Roasted Root Vegetables",
        "description": "Dr. Longo recommends Atlantic mackerel as one of the richest sources of omega-3 and vitamin D. Roasted with Lithuanian root vegetables for a complete longevity dinner.",
        "category": "heart-healthy",
        "meal_type": "dinner",
        "servings": 1,
        "prep_time_min": 35,
        "calories": 490,
        "protein_g": 35, "carbs_g": 32, "fat_g": 22, "fiber_g": 7,
        "nutrients": {"omega_3_g": 4.5, "vitamin_d_mcg": 18, "selenium_mcg": 60},
        "instructions": [
            "Preheat oven to 200°C.",
            "Dice carrot, beet, and potato into chunks.",
            "Toss vegetables with olive oil, spread on baking tray.",
            "Roast vegetables for 20 min.",
            "Place mackerel fillet on tray, season with lemon and dill.",
            "Roast another 12 min until fish flakes easily.",
        ],
        "health_benefits": ["highest omega-3 of common fish", "vitamin D for immunity", "beets for blood pressure"],
        "allergens": ["fish"],
        "ingredients": [
            {"name": "mackerel fillet (fresh or frozen)", "amount": 200, "unit": "g"},
            {"name": "carrot", "amount": 2, "unit": "pcs"},
            {"name": "beet", "amount": 1, "unit": "pcs"},
            {"name": "potato", "amount": 3, "unit": "pcs"},
            {"name": "extra virgin olive oil", "amount": 1, "unit": "tbsp"},
            {"name": "lemon", "amount": 0.5, "unit": "pcs"},
            {"name": "fresh dill", "amount": 1, "unit": "handful"},
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(RecipeDB).count()
    if existing > 0:
        print(f"Database already has {existing} recipes. Skipping seed.")
        db.close()
        return

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
