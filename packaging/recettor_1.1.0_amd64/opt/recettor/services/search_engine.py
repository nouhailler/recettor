from fuzzywuzzy import fuzz, process
from database import db_manager


def fuzzy_search(query, threshold=60):
    """Search recipes using fuzzy matching on name and description."""
    all_recipes = db_manager.get_all_recipes()
    if not query:
        return all_recipes

    results = []
    for recipe in all_recipes:
        score = max(
            fuzz.partial_ratio(query.lower(), recipe['name'].lower()),
            fuzz.partial_ratio(query.lower(), recipe.get('description', '').lower())
        )
        if score >= threshold:
            recipe['_score'] = score
            results.append(recipe)

    results.sort(key=lambda x: x.get('_score', 0), reverse=True)
    return results


def search(query='', ingredient='', dish_type='', diet='', difficulty='', season='', cuisine='', max_calories=0, use_fuzzy=True):
    """Combined search with optional fuzzy matching."""
    # Use DB search for filter-based queries
    db_results = db_manager.search_recipes(
        query=query if not use_fuzzy else '',
        ingredient=ingredient,
        dish_type=dish_type,
        diet=diet,
        difficulty=difficulty,
        season=season,
        cuisine=cuisine,
        max_calories=max_calories
    )

    if query and use_fuzzy:
        # Get all recipes matching filters, then apply fuzzy search
        if ingredient or dish_type or diet or difficulty or season or cuisine or max_calories:
            # Apply fuzzy on filtered results
            names = {r['name']: r for r in db_results}
            if names:
                matches = process.extractBests(query, names.keys(), scorer=fuzz.partial_ratio, score_cutoff=50)
                return [names[m[0]] for m in matches]
            return []
        else:
            results = fuzzy_search(query)
            if max_calories and max_calories > 0:
                results = [r for r in results if 0 < (r.get('calories_per_serving') or 0) <= max_calories]
            return results

    return db_results
