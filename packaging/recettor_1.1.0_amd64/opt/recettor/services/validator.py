import json
import jsonschema
from jsonschema import validate

RECIPE_SCHEMA = {
    "type": "object",
    "required": ["nom"],
    "properties": {
        "nom": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "type_cuisine": {"type": "string"},
        "type_plat": {"type": "string"},
        "difficulte": {"type": "string", "enum": ["Facile", "Intermédiaire", "Difficile", "facile", "intermédiaire", "difficile"]},
        "temps_preparation": {"type": "number", "minimum": 0},
        "temps_cuisson": {"type": "number", "minimum": 0},
        "temps_repos": {"type": "number", "minimum": 0},
        "portions": {"type": "number", "minimum": 1},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["nom"],
                "properties": {
                    "nom": {"type": "string"},
                    "quantite": {"type": "number"},
                    "unite": {"type": "string"},
                    "preparation": {"type": "string"},
                    "optionnel": {"type": "boolean"}
                }
            }
        },
        "etapes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "numero": {"type": "number"},
                    "description": {"type": "string"},
                    "duree": {"type": "number"},
                    "temperature": {"type": "number"},
                    "technique": {"type": "string"}
                }
            }
        }
    }
}

IMPORT_SCHEMA = {
    "type": "object",
    "required": ["recettes"],
    "properties": {
        "recettes": {
            "type": "array",
            "items": RECIPE_SCHEMA
        }
    }
}


def validate_recipe(data):
    """Validate a single recipe dict. Returns (valid, errors)."""
    try:
        validate(instance=data, schema=RECIPE_SCHEMA)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e.message)]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]


def validate_import(data):
    """Validate import JSON structure. Returns (valid, errors)."""
    try:
        validate(instance=data, schema=IMPORT_SCHEMA)
        errors = []
        for i, recipe in enumerate(data.get('recettes', [])):
            valid, errs = validate_recipe(recipe)
            if not valid:
                errors.extend([f"Recette {i+1} ({recipe.get('nom', '?')}): {e}" for e in errs])
        return len(errors) == 0, errors
    except jsonschema.ValidationError as e:
        return False, [str(e.message)]
