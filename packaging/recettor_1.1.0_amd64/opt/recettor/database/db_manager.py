import sqlite3
import json
import os
import shutil
from datetime import datetime
from config import DB_PATH, IMAGES_DIR, BACKUP_DIR, SAISONS_PATH


def normalize_ingredient(name):
    """Normalize French ligatures so users can type 'oeuf' instead of 'œuf'."""
    return (name
            .replace('œ', 'oe').replace('Œ', 'Oe')
            .replace('æ', 'ae').replace('Æ', 'Ae'))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            other_names TEXT DEFAULT '',
            description TEXT DEFAULT '',
            history TEXT DEFAULT '',
            author TEXT DEFAULT '',
            source TEXT DEFAULT '',
            created_date TEXT DEFAULT '',
            cuisine_type TEXT DEFAULT '',
            region TEXT DEFAULT '',
            occasion TEXT DEFAULT '',
            dish_type TEXT DEFAULT '',
            category TEXT DEFAULT '',
            diet TEXT DEFAULT 'Standard',
            ideal_season TEXT DEFAULT 'Toutes saisons',
            prep_time INTEGER DEFAULT 0,
            cook_time INTEGER DEFAULT 0,
            rest_time INTEGER DEFAULT 0,
            difficulty TEXT DEFAULT 'Facile',
            servings INTEGER DEFAULT 4,
            estimated_cost TEXT DEFAULT '',
            calories_per_serving REAL DEFAULT 0,
            proteins REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fats REAL DEFAULT 0,
            fiber REAL DEFAULT 0,
            sugar REAL DEFAULT 0,
            salt REAL DEFAULT 0,
            vitamins TEXT DEFAULT '',
            minerals TEXT DEFAULT '',
            oven_temperature INTEGER DEFAULT 0,
            fire_power TEXT DEFAULT '',
            cooking_type TEXT DEFAULT '',
            plate_type TEXT DEFAULT '',
            food_arrangement TEXT DEFAULT '',
            decoration TEXT DEFAULT '',
            garnish TEXT DEFAULT '',
            fridge_duration TEXT DEFAULT '',
            freezer_duration TEXT DEFAULT '',
            reheating_method TEXT DEFAULT '',
            storage_method TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            rating REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            aromatic_profile TEXT DEFAULT '',
            taste_intensity TEXT DEFAULT '',
            texture TEXT DEFAULT '',
            glycemic_index TEXT DEFAULT '',
            date_added TEXT DEFAULT '',
            times_cooked INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity REAL DEFAULT 0,
            unit TEXT DEFAULT '',
            preparation TEXT DEFAULT '',
            optional INTEGER DEFAULT 0,
            replacement TEXT DEFAULT '',
            quality TEXT DEFAULT '',
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        );

        CREATE TABLE IF NOT EXISTS recipe_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            description TEXT NOT NULL,
            duration INTEGER DEFAULT 0,
            temperature INTEGER DEFAULT 0,
            technique TEXT DEFAULT '',
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS recipe_equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            equipment TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS recipe_allergens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            allergen TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS recipe_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            tip_type TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS seasonal_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient TEXT NOT NULL,
            month_start INTEGER NOT NULL,
            month_end INTEGER NOT NULL,
            region TEXT DEFAULT 'France'
        );

        CREATE TABLE IF NOT EXISTS favorite_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS fridge_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            checked INTEGER DEFAULT 0,
            added_date TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS favorite_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL UNIQUE,
            added_date TEXT DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_recipe_name ON recipes(name);
        CREATE INDEX IF NOT EXISTS idx_ingredient_name ON ingredients(name);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);
    """)
    conn.commit()
    conn.close()
    _initialize_seasonal_data()


def _initialize_seasonal_data():
    """Initialize seasonal ingredients data for France."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM seasonal_ingredients")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    # French seasonal data (ingredient, month_start, month_end, region)
    seasonal_data = [
        # Légumes
        ("asperge", 4, 6, "France"),
        ("artichaut", 5, 10, "France"),
        ("aubergine", 6, 9, "France"),
        ("betterave", 9, 3, "France"),
        ("brocoli", 9, 3, "France"),
        ("carotte", 1, 12, "France"),
        ("chou-fleur", 9, 3, "France"),
        ("chou", 9, 3, "France"),
        ("courgette", 5, 9, "France"),
        ("épinard", 3, 6, "France"),
        ("épinard", 9, 11, "France"),
        ("fenouil", 9, 2, "France"),
        ("haricot vert", 6, 9, "France"),
        ("navet", 10, 3, "France"),
        ("oignon", 1, 12, "France"),
        ("ail", 6, 9, "France"),
        ("persil", 1, 12, "France"),
        ("poireau", 9, 4, "France"),
        ("poivron", 6, 9, "France"),
        ("potiron", 9, 12, "France"),
        ("pomme de terre", 1, 12, "France"),
        ("radis", 3, 7, "France"),
        ("salade", 4, 10, "France"),
        ("tomate", 6, 9, "France"),
        ("concombre", 5, 9, "France"),
        ("maïs", 7, 10, "France"),
        ("petits pois", 4, 7, "France"),
        ("céleri", 9, 3, "France"),
        ("panais", 10, 3, "France"),
        ("butternut", 9, 2, "France"),
        ("courge", 9, 12, "France"),
        # Fruits
        ("abricot", 6, 8, "France"),
        ("cerise", 5, 7, "France"),
        ("citron", 1, 12, "France"),
        ("figue", 8, 10, "France"),
        ("fraise", 4, 7, "France"),
        ("framboise", 6, 9, "France"),
        ("groseille", 6, 8, "France"),
        ("kiwi", 11, 3, "France"),
        ("mandarine", 11, 2, "France"),
        ("melon", 6, 9, "France"),
        ("mirabelle", 7, 9, "France"),
        ("mûre", 7, 9, "France"),
        ("myrtille", 7, 9, "France"),
        ("nectarine", 6, 9, "France"),
        ("pêche", 6, 9, "France"),
        ("poire", 8, 12, "France"),
        ("pomme", 8, 3, "France"),
        ("prune", 7, 10, "France"),
        ("quetsche", 8, 10, "France"),
        ("raisin", 8, 10, "France"),
        ("rhubarbe", 4, 6, "France"),
        ("pastèque", 6, 9, "France"),
        ("orange", 11, 4, "France"),
        ("pamplemousse", 11, 4, "France"),
    ]

    c.executemany(
        "INSERT INTO seasonal_ingredients (ingredient, month_start, month_end, region) VALUES (?,?,?,?)",
        seasonal_data
    )
    conn.commit()
    conn.close()


def get_recipe_count():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM recipes")
    count = c.fetchone()[0]
    conn.close()
    return count


def get_all_recipes(sort_by="name"):
    conn = get_connection()
    c = conn.cursor()
    allowed_sorts = {"name": "name", "date": "date_added DESC", "rating": "rating DESC", "difficulty": "difficulty"}
    order = allowed_sorts.get(sort_by, "name")
    c.execute(f"SELECT id, name, description, dish_type, cuisine_type, difficulty, prep_time, cook_time, servings, image_path, rating, ideal_season, diet, calories_per_serving FROM recipes ORDER BY {order}")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recipe_by_id(recipe_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,))
    recipe = c.fetchone()
    if not recipe:
        conn.close()
        return None
    recipe = dict(recipe)

    # Load related data
    c.execute("""
        SELECT ri.*, i.name as ingredient_name
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id=?
        ORDER BY ri.id
    """, (recipe_id,))
    recipe['ingredients'] = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM recipe_steps WHERE recipe_id=? ORDER BY step_number", (recipe_id,))
    recipe['steps'] = [dict(r) for r in c.fetchall()]

    c.execute("SELECT equipment FROM recipe_equipment WHERE recipe_id=?", (recipe_id,))
    recipe['equipment'] = [r['equipment'] for r in c.fetchall()]

    c.execute("SELECT allergen FROM recipe_allergens WHERE recipe_id=?", (recipe_id,))
    recipe['allergens'] = [r['allergen'] for r in c.fetchall()]

    c.execute("SELECT tip_type, content FROM recipe_tips WHERE recipe_id=?", (recipe_id,))
    recipe['tips'] = [dict(r) for r in c.fetchall()]

    conn.close()
    return recipe


def get_or_create_ingredient(conn, name):
    name = normalize_ingredient(name.lower().strip())
    c = conn.cursor()
    c.execute("SELECT id FROM ingredients WHERE name=?", (name,))
    row = c.fetchone()
    if row:
        return row['id']
    c.execute("INSERT INTO ingredients (name) VALUES (?)", (name,))
    return c.lastrowid


def add_recipe(data):
    conn = get_connection()
    c = conn.cursor()
    data['date_added'] = datetime.now().isoformat()

    # Handle tags as JSON
    if isinstance(data.get('tags'), list):
        data['tags'] = json.dumps(data['tags'], ensure_ascii=False)

    recipe_fields = [
        'name', 'other_names', 'description', 'history', 'author', 'source',
        'created_date', 'cuisine_type', 'region', 'occasion', 'dish_type',
        'category', 'diet', 'ideal_season', 'prep_time', 'cook_time', 'rest_time',
        'difficulty', 'servings', 'estimated_cost', 'calories_per_serving',
        'proteins', 'carbs', 'fats', 'fiber', 'sugar', 'salt', 'vitamins', 'minerals',
        'oven_temperature', 'fire_power', 'cooking_type',
        'plate_type', 'food_arrangement', 'decoration', 'garnish',
        'fridge_duration', 'freezer_duration', 'reheating_method', 'storage_method',
        'tags', 'rating', 'notes', 'image_path',
        'aromatic_profile', 'taste_intensity', 'texture', 'glycemic_index', 'date_added'
    ]

    fields_present = {k: data.get(k, '') for k in recipe_fields}
    # Convert None to ''
    for k, v in fields_present.items():
        if v is None:
            fields_present[k] = ''

    cols = ', '.join(fields_present.keys())
    placeholders = ', '.join(['?' for _ in fields_present])
    c.execute(f"INSERT INTO recipes ({cols}) VALUES ({placeholders})", list(fields_present.values()))
    recipe_id = c.lastrowid

    # Insert ingredients
    for ing in data.get('ingredients', []):
        ing_id = get_or_create_ingredient(conn, ing['name'])
        c.execute("""
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation, optional, replacement, quality)
            VALUES (?,?,?,?,?,?,?,?)
        """, (recipe_id, ing_id, ing.get('quantity', 0), ing.get('unit', ''),
              ing.get('preparation', ''), 1 if ing.get('optional') else 0,
              ing.get('replacement', ''), ing.get('quality', '')))

    # Insert steps
    for step in data.get('steps', []):
        c.execute("""
            INSERT INTO recipe_steps (recipe_id, step_number, description, duration, temperature, technique)
            VALUES (?,?,?,?,?,?)
        """, (recipe_id, step.get('step_number', 1), step.get('description', ''),
              step.get('duration', 0), step.get('temperature', 0), step.get('technique', '')))

    # Insert equipment
    for eq in data.get('equipment', []):
        c.execute("INSERT INTO recipe_equipment (recipe_id, equipment) VALUES (?,?)", (recipe_id, eq))

    # Insert allergens
    for al in data.get('allergens', []):
        c.execute("INSERT INTO recipe_allergens (recipe_id, allergen) VALUES (?,?)", (recipe_id, al))

    # Insert tips
    for tip in data.get('tips', []):
        c.execute("INSERT INTO recipe_tips (recipe_id, tip_type, content) VALUES (?,?,?)",
                  (recipe_id, tip.get('tip_type', ''), tip.get('content', '')))

    conn.commit()
    conn.close()
    return recipe_id


def update_recipe(recipe_id, data):
    conn = get_connection()
    c = conn.cursor()

    if isinstance(data.get('tags'), list):
        data['tags'] = json.dumps(data['tags'], ensure_ascii=False)

    recipe_fields = [
        'name', 'other_names', 'description', 'history', 'author', 'source',
        'created_date', 'cuisine_type', 'region', 'occasion', 'dish_type',
        'category', 'diet', 'ideal_season', 'prep_time', 'cook_time', 'rest_time',
        'difficulty', 'servings', 'estimated_cost', 'calories_per_serving',
        'proteins', 'carbs', 'fats', 'fiber', 'sugar', 'salt', 'vitamins', 'minerals',
        'oven_temperature', 'fire_power', 'cooking_type',
        'plate_type', 'food_arrangement', 'decoration', 'garnish',
        'fridge_duration', 'freezer_duration', 'reheating_method', 'storage_method',
        'tags', 'rating', 'notes', 'image_path',
        'aromatic_profile', 'taste_intensity', 'texture', 'glycemic_index'
    ]

    fields_present = {k: data.get(k, '') for k in recipe_fields if k in data}
    for k, v in fields_present.items():
        if v is None:
            fields_present[k] = ''

    if fields_present:
        set_clause = ', '.join([f"{k}=?" for k in fields_present.keys()])
        c.execute(f"UPDATE recipes SET {set_clause} WHERE id=?",
                  list(fields_present.values()) + [recipe_id])

    # Update related data (delete and re-insert)
    if 'ingredients' in data:
        c.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?", (recipe_id,))
        for ing in data['ingredients']:
            ing_id = get_or_create_ingredient(conn, ing['name'])
            c.execute("""
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation, optional, replacement, quality)
                VALUES (?,?,?,?,?,?,?,?)
            """, (recipe_id, ing_id, ing.get('quantity', 0), ing.get('unit', ''),
                  ing.get('preparation', ''), 1 if ing.get('optional') else 0,
                  ing.get('replacement', ''), ing.get('quality', '')))

    if 'steps' in data:
        c.execute("DELETE FROM recipe_steps WHERE recipe_id=?", (recipe_id,))
        for step in data['steps']:
            c.execute("""
                INSERT INTO recipe_steps (recipe_id, step_number, description, duration, temperature, technique)
                VALUES (?,?,?,?,?,?)
            """, (recipe_id, step.get('step_number', 1), step.get('description', ''),
                  step.get('duration', 0), step.get('temperature', 0), step.get('technique', '')))

    if 'equipment' in data:
        c.execute("DELETE FROM recipe_equipment WHERE recipe_id=?", (recipe_id,))
        for eq in data['equipment']:
            c.execute("INSERT INTO recipe_equipment (recipe_id, equipment) VALUES (?,?)", (recipe_id, eq))

    if 'allergens' in data:
        c.execute("DELETE FROM recipe_allergens WHERE recipe_id=?", (recipe_id,))
        for al in data['allergens']:
            c.execute("INSERT INTO recipe_allergens (recipe_id, allergen) VALUES (?,?)", (recipe_id, al))

    if 'tips' in data:
        c.execute("DELETE FROM recipe_tips WHERE recipe_id=?", (recipe_id,))
        for tip in data['tips']:
            c.execute("INSERT INTO recipe_tips (recipe_id, tip_type, content) VALUES (?,?,?)",
                      (recipe_id, tip.get('tip_type', ''), tip.get('content', '')))

    conn.commit()
    conn.close()


def delete_recipe(recipe_id):
    conn = get_connection()
    # Delete image if exists
    c = conn.cursor()
    c.execute("SELECT image_path FROM recipes WHERE id=?", (recipe_id,))
    row = c.fetchone()
    if row and row['image_path'] and os.path.exists(row['image_path']):
        try:
            os.remove(row['image_path'])
        except Exception:
            pass
    c.execute("DELETE FROM favorite_recipes WHERE recipe_id=?", (recipe_id,))
    c.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()


def search_recipes(query='', ingredient='', dish_type='', diet='', difficulty='', season='', cuisine='', max_calories=0):
    conn = get_connection()
    c = conn.cursor()

    sql = """
        SELECT DISTINCT r.id, r.name, r.description, r.dish_type, r.cuisine_type,
               r.difficulty, r.prep_time, r.cook_time, r.servings, r.image_path,
               r.rating, r.ideal_season, r.diet, r.calories_per_serving
        FROM recipes r
        LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        LEFT JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (r.name LIKE ? OR r.description LIKE ? OR r.other_names LIKE ?)"
        q = f"%{query}%"
        params.extend([q, q, q])

    if ingredient:
        sql += " AND i.name LIKE ?"
        params.append(f"%{normalize_ingredient(ingredient.lower())}%")

    if dish_type:
        sql += " AND r.dish_type = ?"
        params.append(dish_type)

    if diet:
        sql += " AND r.diet = ?"
        params.append(diet)

    if difficulty:
        sql += " AND r.difficulty = ?"
        params.append(difficulty)

    if season:
        sql += " AND (r.ideal_season = ? OR r.ideal_season = 'Toutes saisons')"
        params.append(season)

    if cuisine:
        sql += " AND r.cuisine_type = ?"
        params.append(cuisine)

    if max_calories and max_calories > 0:
        sql += " AND r.calories_per_serving > 0 AND r.calories_per_serving <= ?"
        params.append(max_calories)

    sql += " ORDER BY r.name"
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_seasonal_ingredients(month):
    """Get ingredients in season for a given month (1-12)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT ingredient FROM seasonal_ingredients
        WHERE (month_start <= month_end AND month_start <= ? AND month_end >= ?)
           OR (month_start > month_end AND (? >= month_start OR ? <= month_end))
        ORDER BY ingredient
    """, (month, month, month, month))
    rows = c.fetchall()
    conn.close()
    return [r['ingredient'] for r in rows]


def get_seasonal_recipes(month):
    """Get recipes whose ingredients are in season."""
    seasonal_ings = get_seasonal_ingredients(month)
    if not seasonal_ings:
        return []

    conn = get_connection()
    c = conn.cursor()

    placeholders = ','.join(['?' for _ in seasonal_ings])
    c.execute(f"""
        SELECT DISTINCT r.id, r.name, r.description, r.dish_type, r.cuisine_type,
               r.difficulty, r.prep_time, r.cook_time, r.servings, r.image_path,
               r.rating, r.ideal_season, r.diet,
               COUNT(DISTINCT ri2.ingredient_id) as total_ingredients,
               COUNT(DISTINCT CASE WHEN i2.name IN ({placeholders}) THEN ri2.id END) as seasonal_count
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.id
        LEFT JOIN recipe_ingredients ri2 ON r.id = ri2.recipe_id
        LEFT JOIN ingredients i2 ON ri2.ingredient_id = i2.id
        WHERE i.name IN ({placeholders})
        GROUP BY r.id
        ORDER BY seasonal_count DESC, r.name
    """, seasonal_ings + seasonal_ings)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_recipes_by_fridge(fridge_ingredients):
    """Return recipes that use at least one fridge ingredient, ranked by match %."""
    if not fridge_ingredients:
        return []
    fridge_lower = [normalize_ingredient(f.lower().strip()) for f in fridge_ingredients]

    conn = get_connection()
    c = conn.cursor()
    placeholders = ','.join(['?' for _ in fridge_lower])

    c.execute(f"""
        SELECT r.id, r.name, r.description, r.dish_type, r.cuisine_type,
               r.difficulty, r.prep_time, r.cook_time, r.servings, r.image_path,
               r.rating, r.ideal_season, r.diet, r.calories_per_serving,
               COUNT(DISTINCT ri.ingredient_id) AS total_ingredients,
               SUM(CASE WHEN i.name IN ({placeholders}) THEN 1 ELSE 0 END) AS matching_count
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.id
        GROUP BY r.id
        HAVING matching_count > 0
    """, fridge_lower)

    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    for row in rows:
        total = max(row['total_ingredients'], 1)
        row['match_pct'] = int(row['matching_count'] / total * 100)

    rows.sort(key=lambda r: (r['match_pct'], r['matching_count']), reverse=True)
    return rows


def get_all_ingredients():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM ingredients ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [r['name'] for r in rows]


def get_all_recipes_for_export():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM recipes ORDER BY name")
    ids = [r['id'] for r in c.fetchall()]
    conn.close()
    return [get_recipe_by_id(rid) for rid in ids]


def backup_database():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"recettes_backup_{timestamp}.db")
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def get_favorite_ingredients():
    """Return list of favorite ingredient names sorted alphabetically."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS favorite_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    c.execute("SELECT name FROM favorite_ingredients ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [r['name'] for r in rows]


def add_favorite_ingredient(name):
    name = name.lower().strip()
    if not name:
        return False
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS favorite_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    try:
        c.execute("INSERT INTO favorite_ingredients (name) VALUES (?)", (name,))
        conn.commit()
        result = True
    except Exception:
        result = False
    conn.close()
    return result


def remove_favorite_ingredient(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM favorite_ingredients WHERE name=?", (name.lower().strip(),))
    conn.commit()
    conn.close()


def is_favorite_ingredient(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM favorite_ingredients WHERE name=?", (name.lower().strip(),))
    row = c.fetchone()
    conn.close()
    return row is not None


# ── Fridge persistence ────────────────────────────────────────────────────────

def get_fridge_ingredients():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM fridge_ingredients ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [r['name'] for r in rows]


def add_fridge_ingredient(name):
    name = normalize_ingredient(name.lower().strip())
    if not name:
        return
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO fridge_ingredients (name) VALUES (?)", (name,))
        conn.commit()
    finally:
        conn.close()


def remove_fridge_ingredient(name):
    name = normalize_ingredient(name.lower().strip())
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM fridge_ingredients WHERE name=?", (name,))
    conn.commit()
    conn.close()


def clear_fridge_ingredients():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM fridge_ingredients")
    conn.commit()
    conn.close()


# ── Liste de courses ──────────────────────────────────────────────────────────

def get_shopping_list():
    """Retourne tous les articles : non cochés d'abord, puis cochés."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, checked, added_date FROM shopping_list "
        "ORDER BY checked ASC, id DESC"
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_shopping_item(name):
    """Ajoute un article. Retourne True si ajouté, False si déjà présent."""
    name = name.strip()
    if not name:
        return False
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT OR IGNORE INTO shopping_list (name, added_date) VALUES (?, ?)",
            (name, datetime.now().isoformat())
        )
        added = c.rowcount > 0
        conn.commit()
    finally:
        conn.close()
    return added


def remove_shopping_item(item_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM shopping_list WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def toggle_shopping_item(item_id):
    """Bascule l'état coché/non-coché d'un article."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE shopping_list SET checked = 1 - checked WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def clear_checked_items():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM shopping_list WHERE checked=1")
    conn.commit()
    conn.close()


def clear_shopping_list():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM shopping_list")
    conn.commit()
    conn.close()


# ── Recettes favorites ────────────────────────────────────────────────────────

def get_favorite_recipes():
    """Retourne les recettes favorites avec leurs infos de base."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT r.id, r.name, r.dish_type, r.difficulty, r.cuisine_type,
               r.prep_time, r.cook_time, r.image_path
        FROM favorite_recipes fr
        JOIN recipes r ON fr.recipe_id = r.id
        ORDER BY fr.added_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_favorite_recipe(recipe_id):
    """Ajoute une recette aux favoris. Retourne True si ajoutée."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT OR IGNORE INTO favorite_recipes (recipe_id, added_date) VALUES (?, ?)",
            (recipe_id, datetime.now().isoformat())
        )
        added = c.rowcount > 0
        conn.commit()
    finally:
        conn.close()
    return added


def remove_favorite_recipe(recipe_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM favorite_recipes WHERE recipe_id=?", (recipe_id,))
    conn.commit()
    conn.close()


def is_favorite_recipe(recipe_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM favorite_recipes WHERE recipe_id=?", (recipe_id,))
    row = c.fetchone()
    conn.close()
    return row is not None
