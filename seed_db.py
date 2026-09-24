# Seed script for Smart Recipe & Pantry Assistant Firestore database
import os
from google.cloud import firestore

# Hardcode project ID as a literal string to ensure compatibility on Agent Platform
PROJECT_ID = "qwiklabs-gcp-01-e1fa088249da"

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    # 1. Seed Pantry Items
    pantry_items = [
        {
            "id": "pantry_001",
            "name": "Extra Virgin Olive Oil",
            "category": "Oils & Condiments",
            "quantity": "500ml",
            "expiration_date": "2026-12-31",
        },
        {
            "id": "pantry_002",
            "name": "Garlic Cloves",
            "category": "Produce",
            "quantity": "1 head",
            "expiration_date": "2026-10-15",
        },
        {
            "id": "pantry_003",
            "name": "Arborio Rice",
            "category": "Grains & Pasta",
            "quantity": "1 kg",
            "expiration_date": "2027-01-01",
        },
        {
            "id": "pantry_004",
            "name": "Parmesan Cheese",
            "category": "Dairy",
            "quantity": "200g",
            "expiration_date": "2026-11-01",
        },
        {
            "id": "pantry_005",
            "name": "Organic Tomatoes",
            "category": "Produce",
            "quantity": "4 items",
            "expiration_date": "2026-10-05",
        },
    ]

    print("Seeding 'pantry_items' collection...")
    pantry_ref = db.collection("pantry_items")
    for item in pantry_items:
        pantry_ref.document(item["id"]).set(item)
        print(f"  - Added pantry item: {item['name']}")

    # 2. Seed Recipes
    recipes = [
        {
            "id": "rec_001",
            "title": "Garlic & Tomato Tuscan Risotto",
            "ingredients": ["Arborio Rice", "Garlic Cloves", "Organic Tomatoes", "Extra Virgin Olive Oil", "Parmesan Cheese"],
            "prep_time_minutes": 30,
            "dietary_tags": ["vegetarian", "gluten-free"],
            "instructions": "1. Sauté minced garlic in olive oil. 2. Add arborio rice and toast slightly. 3. Add warm broth in increments. 4. Stir in diced tomatoes and parmesan cheese before serving.",
        },
        {
            "id": "rec_002",
            "title": "Simple Roasted Garlic Tomato Salad",
            "ingredients": ["Organic Tomatoes", "Garlic Cloves", "Extra Virgin Olive Oil", "Parmesan Cheese"],
            "prep_time_minutes": 15,
            "dietary_tags": ["vegetarian", "gluten-free", "low-carb"],
            "instructions": "1. Slice tomatoes into rounds. 2. Drizzle with extra virgin olive oil and minced garlic. 3. Top with shaved parmesan and serve fresh.",
        },
    ]

    print("Seeding 'recipes' collection...")
    recipes_ref = db.collection("recipes")
    for recipe in recipes:
        recipes_ref.document(recipe["id"]).set(recipe)
        print(f"  - Added recipe: {recipe['title']}")

    print("\n✅ Database seeding complete!")

if __name__ == "__main__":
    seed_database()
