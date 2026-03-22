from datetime import datetime
from database import db_manager
from config import MONTH_NAMES


def get_current_month():
    return datetime.now().month


def get_current_season_name():
    month = get_current_month()
    if month in (3, 4, 5):
        return "Printemps"
    elif month in (6, 7, 8):
        return "Été"
    elif month in (9, 10, 11):
        return "Automne"
    else:
        return "Hiver"


def get_seasonal_info(month=None):
    if month is None:
        month = get_current_month()

    ingredients = db_manager.get_seasonal_ingredients(month)
    recipes = db_manager.get_seasonal_recipes(month)

    # Check end-of-season alerts (ingredients ending within 2 months)
    next_month = (month % 12) + 1

    from database.db_manager import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT ingredient FROM seasonal_ingredients
        WHERE month_end = ? OR month_end = ?
    """, (month, next_month))
    ending_soon = [r['ingredient'] for r in c.fetchall()]
    conn.close()

    # Determine season name for the given month
    if month in (3, 4, 5):
        season = "Printemps"
    elif month in (6, 7, 8):
        season = "Été"
    elif month in (9, 10, 11):
        season = "Automne"
    else:
        season = "Hiver"

    return {
        'month': month,
        'month_name': MONTH_NAMES[month - 1],
        'season': season,
        'ingredients': ingredients,
        'recipes': recipes,
        'ending_soon': ending_soon
    }
