import json
import os
import shutil
from datetime import datetime
from database import db_manager
from config import IMAGES_DIR, BACKUP_DIR


def import_recipes(filepath):
    """Import recipes from JSON file. Returns (imported_count, errors)."""
    from services.validator import validate_import

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return 0, [f"Erreur de lecture du fichier: {e}"]
    except FileNotFoundError:
        return 0, ["Fichier introuvable"]

    valid, errors = validate_import(data)
    if errors:
        # Try to import valid recipes anyway, report errors
        pass

    imported = 0
    import_errors = []

    for recipe_data in data.get('recettes', []):
        try:
            db_data = _convert_import_to_db(recipe_data)
            db_manager.add_recipe(db_data)
            imported += 1
        except Exception as e:
            import_errors.append(f"Erreur import '{recipe_data.get('nom', '?')}': {e}")

    return imported, import_errors


def _convert_import_to_db(data):
    """Convert imported JSON format to DB format."""
    # Handle capitalization
    difficulty_map = {'facile': 'Facile', 'intermédiaire': 'Intermédiaire', 'difficile': 'Difficile'}

    db_data = {
        'name': data.get('nom', ''),
        'other_names': data.get('autres_noms', ''),
        'description': data.get('description', ''),
        'history': data.get('histoire', ''),
        'author': data.get('auteur', ''),
        'source': data.get('source', ''),
        'created_date': data.get('date_creation', ''),
        'cuisine_type': data.get('type_cuisine', ''),
        'region': data.get('region', ''),
        'occasion': data.get('occasion', ''),
        'dish_type': data.get('type_plat', ''),
        'category': data.get('categorie', ''),
        'diet': data.get('regime', 'Standard'),
        'ideal_season': data.get('saison_ideale', 'Toutes saisons'),
        'prep_time': int(data.get('temps_preparation', 0) or 0),
        'cook_time': int(data.get('temps_cuisson', 0) or 0),
        'rest_time': int(data.get('temps_repos', 0) or 0),
        'difficulty': difficulty_map.get(str(data.get('difficulte', 'Facile')).lower(), data.get('difficulte', 'Facile')),
        'servings': int(data.get('portions', 4) or 4),
        'estimated_cost': data.get('cout_estime', ''),
        'calories_per_serving': float(data.get('calories', 0) or 0),
        'proteins': float(data.get('proteines', 0) or 0),
        'carbs': float(data.get('glucides', 0) or 0),
        'fats': float(data.get('lipides', 0) or 0),
        'fiber': float(data.get('fibres', 0) or 0),
        'sugar': float(data.get('sucre', 0) or 0),
        'salt': float(data.get('sel', 0) or 0),
        'oven_temperature': int(data.get('temperature_four', 0) or 0),
        'cooking_type': data.get('type_cuisson', ''),
        'fridge_duration': data.get('conservation_frigo', ''),
        'freezer_duration': data.get('conservation_congelateur', ''),
        'reheating_method': data.get('rechauffage', ''),
        'notes': data.get('notes', ''),
        'aromatic_profile': data.get('profil_aromatique', ''),
        'taste_intensity': data.get('intensite_gout', ''),
        'texture': data.get('texture', ''),
        'tags': data.get('tags', []),
        'ingredients': [],
        'steps': [],
        'equipment': data.get('equipement', []),
        'allergens': data.get('allergenes', []),
        'tips': []
    }

    for ing in data.get('ingredients', []):
        db_data['ingredients'].append({
            'name': ing.get('nom', ''),
            'quantity': float(ing.get('quantite', 0) or 0),
            'unit': ing.get('unite', ''),
            'preparation': ing.get('preparation', ''),
            'optional': ing.get('optionnel', False),
            'replacement': ing.get('remplacement', ''),
            'quality': ing.get('qualite', '')
        })

    for i, step in enumerate(data.get('etapes', []), 1):
        db_data['steps'].append({
            'step_number': step.get('numero', i),
            'description': step.get('description', ''),
            'duration': int(step.get('duree', 0) or 0),
            'temperature': int(step.get('temperature', 0) or 0),
            'technique': step.get('technique', '')
        })

    for tip_type in ['astuces', 'erreurs', 'variantes', 'accompagnements', 'accords']:
        for item in data.get(tip_type, []):
            db_data['tips'].append({'tip_type': tip_type, 'content': item})

    return db_data


def export_recipes(filepath, recipe_ids=None):
    """Export recipes to JSON file."""
    if recipe_ids:
        recipes = [db_manager.get_recipe_by_id(rid) for rid in recipe_ids]
        recipes = [r for r in recipes if r]
    else:
        recipes = db_manager.get_all_recipes_for_export()

    export_data = {'recettes': [_convert_db_to_export(r) for r in recipes]}

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    return len(recipes)


def _convert_db_to_export(recipe):
    """Convert DB recipe dict to export format."""
    tags = recipe.get('tags', '[]')
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = []

    data = {
        'nom': recipe.get('name', ''),
        'autres_noms': recipe.get('other_names', ''),
        'description': recipe.get('description', ''),
        'histoire': recipe.get('history', ''),
        'auteur': recipe.get('author', ''),
        'source': recipe.get('source', ''),
        'date_creation': recipe.get('created_date', ''),
        'type_cuisine': recipe.get('cuisine_type', ''),
        'region': recipe.get('region', ''),
        'occasion': recipe.get('occasion', ''),
        'type_plat': recipe.get('dish_type', ''),
        'categorie': recipe.get('category', ''),
        'regime': recipe.get('diet', ''),
        'saison_ideale': recipe.get('ideal_season', ''),
        'temps_preparation': recipe.get('prep_time', 0),
        'temps_cuisson': recipe.get('cook_time', 0),
        'temps_repos': recipe.get('rest_time', 0),
        'difficulte': recipe.get('difficulty', ''),
        'portions': recipe.get('servings', 4),
        'cout_estime': recipe.get('estimated_cost', ''),
        'calories': recipe.get('calories_per_serving', 0),
        'proteines': recipe.get('proteins', 0),
        'glucides': recipe.get('carbs', 0),
        'lipides': recipe.get('fats', 0),
        'fibres': recipe.get('fiber', 0),
        'sucre': recipe.get('sugar', 0),
        'sel': recipe.get('salt', 0),
        'temperature_four': recipe.get('oven_temperature', 0),
        'type_cuisson': recipe.get('cooking_type', ''),
        'conservation_frigo': recipe.get('fridge_duration', ''),
        'conservation_congelateur': recipe.get('freezer_duration', ''),
        'rechauffage': recipe.get('reheating_method', ''),
        'notes': recipe.get('notes', ''),
        'profil_aromatique': recipe.get('aromatic_profile', ''),
        'intensite_gout': recipe.get('taste_intensity', ''),
        'texture': recipe.get('texture', ''),
        'tags': tags,
        'ingredients': [],
        'etapes': [],
        'equipement': recipe.get('equipment', []),
        'allergenes': recipe.get('allergens', []),
        'astuces': [],
        'erreurs': [],
        'variantes': [],
        'accompagnements': [],
        'accords': []
    }

    for ing in recipe.get('ingredients', []):
        data['ingredients'].append({
            'nom': ing.get('ingredient_name', ''),
            'quantite': ing.get('quantity', 0),
            'unite': ing.get('unit', ''),
            'preparation': ing.get('preparation', ''),
            'optionnel': bool(ing.get('optional', 0)),
            'remplacement': ing.get('replacement', ''),
            'qualite': ing.get('quality', '')
        })

    for step in recipe.get('steps', []):
        data['etapes'].append({
            'numero': step.get('step_number', 1),
            'description': step.get('description', ''),
            'duree': step.get('duration', 0),
            'temperature': step.get('temperature', 0),
            'technique': step.get('technique', '')
        })

    for tip in recipe.get('tips', []):
        tip_type = tip.get('tip_type', '')
        content = tip.get('content', '')
        if tip_type in data:
            data[tip_type].append(content)

    return data
