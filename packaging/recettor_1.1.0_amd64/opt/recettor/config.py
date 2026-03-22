import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'images')
STYLES_DIR = os.path.join(BASE_DIR, 'assets', 'styles')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'import_export', 'templates')
DB_PATH = os.path.join(DATA_DIR, 'recettes.db')
SAISONS_PATH = os.path.join(DATA_DIR, 'saisons.json')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

APP_NAME = "Recettor"
APP_VERSION = "1.0.0"

DIFFICULTIES = ['Facile', 'Intermédiaire', 'Difficile']
DISH_TYPES = ['Entrée', 'Plat principal', 'Dessert', 'Snack', 'Boisson', 'Amuse-bouche']
CATEGORIES = ['Soupe', 'Salade', 'Pâtisserie', 'Sauce', 'Grillades', 'Ragoût', 'Pâtes', 'Riz', 'Pizza', 'Tarte', 'Quiche', 'Autre']
DIETS = ['Standard', 'Végétarien', 'Vegan', 'Sans gluten', 'Halal', 'Casher', 'Keto', 'Sans lactose']
SEASONS = ['Printemps', 'Été', 'Automne', 'Hiver', 'Toutes saisons']
ALLERGENS = ['Gluten', 'Lactose', 'Œufs', 'Arachides', 'Fruits à coque', 'Soja', 'Poisson', 'Crustacés', 'Céleri', 'Moutarde', 'Sésame', 'Sulfites', 'Lupin', 'Mollusques']
UNITS = ['g', 'kg', 'ml', 'cl', 'l', 'cuillère à café', 'cuillère à soupe', 'pièce', 'tranche', 'pincée', 'gousse', 'botte', 'branche', 'feuille', 'tasse', 'verre', 'sachet', 'boîte', 'filet', 'au goût']
COOKING_TYPES = ['Vapeur', 'Grillade', 'Friture', 'Rôtissage', 'Braisage', 'Cuisson sous vide', 'Poché', 'Sauté', 'Mijoté', 'Cru']
CUISINES = ['Française', 'Italienne', 'Espagnole', 'Japonaise', 'Chinoise', 'Mexicaine', 'Indienne', 'Marocaine', 'Libanaise', 'Grecque', 'Américaine', 'Thaïlandaise', 'Autre']
OCCASIONS = ['Quotidien', 'Fête', 'Noël', 'Pâques', 'Anniversaire', 'Dîner romantique', 'Repas de famille', 'Brunch', 'Pique-nique', 'Apéritif']
TECHNIQUES = ['Hacher', 'Émincer', 'Blanchir', 'Saisir', 'Mijoter', 'Gratiner', 'Flamber', 'Réduire', 'Déglacer', 'Mariner', 'Fouetter', 'Pétrir']
EQUIPMENT = ['Couteau de chef', 'Planche à découper', 'Casserole', 'Poêle', 'Four', 'Mixeur', 'Robot de cuisine', 'Thermomètre', 'Fouet', 'Spatule', 'Passoire', 'Saladier', 'Rouleau à pâtisserie', 'Wok']
MONTH_NAMES = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_TIMEOUT = 120
