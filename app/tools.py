# Firestore, Image, and Public API tools for Smart Recipe & Pantry Assistant
import os
import uuid
from typing import Any
import requests
from google import genai
from google.genai import types
from google.cloud import firestore, storage
from google.adk.tools import ToolContext

# HARDCODED PROJECT ID & BUCKET NAME - Prevents project-number resolution issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-01-e1fa088249da"
BUCKET_NAME = "smart-recipe-media-qwiklabs-gcp-01-e1fa088249da"

def get_firestore_db() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_pantry_items() -> list[dict[str, Any]]:
    """List all available items currently in the household pantry.

    Returns:
        A list of dictionaries representing pantry items, including name, category, quantity, and expiration date.
    """
    db = get_firestore_db()
    docs = db.collection("pantry_items").stream()
    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)
    return items


def add_pantry_item(name: str, quantity: str, category: str = "General", expiration_date: str = "N/A") -> str:
    """Add a new item or update quantity of an existing item in the household pantry.

    Args:
        name: Name of the pantry item (e.g., 'Extra Virgin Olive Oil').
        quantity: Quantity of the item (e.g., '1 bottle', '500g').
        category: Category of the item (e.g., 'Produce', 'Dairy', 'Grains & Pasta', 'Oils & Condiments').
        expiration_date: Optional expiration date string (e.g., '2026-12-31').

    Returns:
        Confirmation message string.
    """
    db = get_firestore_db()
    doc_id = name.lower().replace(" ", "_")
    item_data = {
        "id": doc_id,
        "name": name,
        "quantity": quantity,
        "category": category,
        "expiration_date": expiration_date,
    }
    db.collection("pantry_items").document(doc_id).set(item_data)
    return f"Successfully added/updated pantry item '{name}' with quantity '{quantity}' in category '{category}'."


def search_recipes(ingredient: str = "", dietary_tag: str = "") -> list[dict[str, Any]]:
    """Search for matching recipes in the database by ingredient or dietary requirement.

    Args:
        ingredient: Optional ingredient keyword to filter recipes by (e.g., 'tomatoes', 'garlic', 'rice').
        dietary_tag: Optional dietary tag to filter by (e.g., 'vegetarian', 'gluten-free', 'vegan').

    Returns:
        A list of matching recipe dictionaries.
    """
    db = get_firestore_db()
    docs = db.collection("recipes").stream()
    recipes = []
    
    ingredient_lower = ingredient.lower().strip()
    tag_lower = dietary_tag.lower().strip()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        
        # Check ingredient match
        ingredients_list = [ing.lower() for ing in data.get("ingredients", [])]
        match_ingredient = not ingredient_lower or any(ingredient_lower in ing for ing in ingredients_list)
        
        # Check dietary tag match
        tags_list = [t.lower() for t in data.get("dietary_tags", [])]
        match_tag = not tag_lower or any(tag_lower in t for t in tags_list)

        if match_ingredient and match_tag:
            recipes.append(data)

    return recipes


def add_recipe(title: str, ingredients: list[str], prep_time_minutes: int, dietary_tags: list[str], instructions: str) -> str:
    """Add a new recipe to the recipe database.

    Args:
        title: Title of the recipe.
        ingredients: List of required ingredients.
        prep_time_minutes: Total preparation and cooking time in minutes.
        dietary_tags: List of applicable dietary tags (e.g., ['vegetarian', 'gluten-free']).
        instructions: Cooking instructions.

    Returns:
        Confirmation message string.
    """
    db = get_firestore_db()
    doc_id = title.lower().replace(" ", "_")
    recipe_data = {
        "id": doc_id,
        "title": title,
        "ingredients": ingredients,
        "prep_time_minutes": prep_time_minutes,
        "dietary_tags": dietary_tags,
        "instructions": instructions,
    }
    db.collection("recipes").document(doc_id).set(recipe_data)
    return f"Successfully added recipe '{title}' to database."


async def generate_dish_image(dish_description: str, tool_context: ToolContext) -> str:
    """Generate a photo of a cooked dish or recipe item using gemini-3.1-flash-lite-image in the global region.

    Saves the generated image as an ADK artifact for Playground and uploads it to Cloud Storage, returning the public HTTPS URL.

    Args:
        dish_description: Visual description of the dish (e.g. 'A bowl of Garlic & Tomato Tuscan Risotto topped with parmesan cheese').

    Returns:
        Public image HTTPS URL string from Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"Professional food photography of: {dish_description}. High quality, delicious presentation."

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        )
    )

    image_bytes = None
    mime_type = "image/jpeg"

    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

    if not image_bytes:
        return "Failed to generate image for the requested dish."

    ext = "png" if "png" in mime_type else "jpg"
    filename = f"dish_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload the same image bytes to the public Cloud Storage bucket and return public HTTPS URL
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url


async def generate_recipe_video(item_description: str, tool_context: ToolContext) -> str:
    """Generate a short video demonstration for a dish or recipe item using gemini-omni-flash-preview in the global region.

    Saves the generated video as an ADK artifact for Playground and uploads it to Cloud Storage, returning the public HTTPS URL.

    Args:
        item_description: Visual description of the dish or cooking process (e.g. 'Fresh garlic and spinach sizzling in olive oil').

    Returns:
        Public video HTTPS URL string from Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"Short video demonstration of: {item_description}."

    response = client.models.generate_content(
        model="gemini-omni-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["VIDEO", "TEXT"]
        )
    )

    video_bytes = None
    mime_type = "video/mp4"

    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                video_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "video/mp4"
                break

    if not video_bytes:
        return "Failed to generate video for the requested item."

    ext = "mp4"
    filename = f"recipe_video_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload the same video bytes to the public Cloud Storage bucket and return public HTTPS URL
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url


def fetch_online_recipes(query: str = "") -> list[dict[str, Any]]:
    """Fetch real-world recipe ideas from TheMealDB public online API.

    Args:
        query: Optional search keyword or meal name (e.g., 'pasta', 'chicken', 'salad'). If empty, fetches a random recipe.

    Returns:
        List of formatted online recipe dictionaries with title, category, area, ingredients, instructions, and thumbnail image URL.
    """
    api_key = os.getenv("MEALDB_API_KEY", "1")
    
    if query.strip():
        url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={query.strip()}"
    else:
        url = f"https://www.themealdb.com/api/json/v1/{api_key}/random.php"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        meals = data.get("meals") or []
        
        results = []
        for meal in meals[:3]:  # Top 3 matches
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                meas = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    measure_str = f"{meas.strip()} " if meas and meas.strip() else ""
                    ingredients.append(f"{measure_str}{ing.strip()}")

            results.append({
                "title": meal.get("strMeal"),
                "category": meal.get("strCategory"),
                "area": meal.get("strArea"),
                "ingredients": ingredients,
                "instructions": meal.get("strInstructions"),
                "thumbnail_url": meal.get("strMealThumb"),
            })
        return results
    except Exception as e:
        return [{"error": f"Failed to fetch recipes from public online API: {str(e)}"}]
