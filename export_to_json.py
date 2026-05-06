"""
Exporte la base de données SQLite de Recettor vers un fichier JSON
pour la version web Netlify.

Usage:
    python export_to_json.py
    python export_to_json.py --output ../recettor-web/public/data/recipes.json
"""

import sqlite3
import json
import os
import argparse
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "recettes.db"
DEFAULT_OUT = Path(__file__).parent.parent / "recettor-web" / "public" / "data" / "recipes.json"


def fetch_recipes(conn):
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, description, dish_type, diet, difficulty, cuisine_type,
               prep_time, cook_time, rest_time, servings, calories_per_serving,
               proteins, carbs, fats, fiber, salt,
               ideal_season, image_path, date_added, rating, tags, notes,
               region, occasion, category, estimated_cost
        FROM recipes
        ORDER BY name
    """)
    recipes = [dict(r) for r in cur.fetchall()]

    for recipe in recipes:
        rid = recipe["id"]

        # Ingrédients
        cur.execute("""
            SELECT i.name, ri.quantity, ri.unit, ri.preparation, ri.optional, ri.replacement
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (rid,))
        recipe["ingredients"] = [dict(r) for r in cur.fetchall()]

        # Étapes
        cur.execute("""
            SELECT step_number, description, duration, technique
            FROM recipe_steps
            WHERE recipe_id = ?
            ORDER BY step_number
        """, (rid,))
        recipe["steps"] = [dict(r) for r in cur.fetchall()]

        # Conseils
        cur.execute("""
            SELECT tip_type, content
            FROM recipe_tips
            WHERE recipe_id = ?
        """, (rid,))
        recipe["tips"] = [dict(r) for r in cur.fetchall()]

        # Équipement
        cur.execute("""
            SELECT equipment
            FROM recipe_equipment
            WHERE recipe_id = ?
        """, (rid,))
        recipe["equipment"] = [r["equipment"] for r in cur.fetchall()]

        # Allergènes
        cur.execute("""
            SELECT allergen
            FROM recipe_allergens
            WHERE recipe_id = ?
        """, (rid,))
        recipe["allergens"] = [r["allergen"] for r in cur.fetchall()]

        # Pas d'images dans la version web
        recipe["image_path"] = None

    return recipes


def fetch_seasonal(conn):
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT ingredient, month_start, month_end, region
        FROM seasonal_ingredients
        ORDER BY month_start, ingredient
    """)
    return [dict(r) for r in cur.fetchall()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Base de données introuvable : {DB_PATH}")
        print("Lance d'abord : python main.py (pour créer la base)")
        raise SystemExit(1)

    conn = sqlite3.connect(DB_PATH)
    recipes = fetch_recipes(conn)
    seasonal = fetch_seasonal(conn)
    conn.close()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = {"recipes": recipes, "seasonal": seasonal}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    print(f"Export OK : {len(recipes)} recettes → {out_path}")


if __name__ == "__main__":
    main()
