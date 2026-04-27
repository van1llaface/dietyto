"""Delete all recipes + ingredients, then re-seed with updated data."""
from database import SessionLocal, Base, engine
from db_models import RecipeDB, IngredientDB

db = SessionLocal()
deleted = db.query(IngredientDB).delete()
print(f"Deleted {deleted} ingredients")
deleted = db.query(RecipeDB).delete()
print(f"Deleted {deleted} recipes")
db.commit()
db.close()

# Now seed fresh
from seed import seed
seed()
