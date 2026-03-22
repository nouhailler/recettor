import json
import re
import requests

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


# ── Custom exceptions ─────────────────────────────────────────────────────────

class OllamaNotRunningError(Exception):
    """Ollama n'est pas démarré (service inaccessible)."""

class OllamaModelNotFoundError(Exception):
    """Modèle absent dans Ollama."""

class OllamaTimeoutError(Exception):
    """Délai Ollama dépassé."""

class OllamaParseError(Exception):
    """Réponse JSON non parseable malgré le fallback."""


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Tu es un chef cuisinier créatif et expert, spécialisé dans la cuisine \
du quotidien. Tu sais transformer des ingrédients simples en plats savoureux.

Ton rôle : proposer des recettes réalistes et gourmandes à partir d'une \
liste d'ingrédients disponibles.

Règles absolues :
- Réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après
- Pas de bloc markdown, pas de ```json, juste le tableau brut
- Respecte scrupuleusement ce schéma pour chaque recette :
{
  "nom": "Nom appétissant de la recette",
  "description_courte": "Une phrase qui donne envie, évocatrice et précise",
  "ingredients_utilises": ["ingrédient1", "ingrédient2"],
  "ingredients_manquants": ["ingrédient optionnel si vraiment utile"],
  "temps_preparation": 20,
  "temps_cuisson": 15,
  "difficulte": "Facile",
  "nb_portions": 4,
  "type_plat": "Plat principal",
  "type_cuisine": "Française",
  "regime": "Standard",
  "saison": "Toutes saisons",
  "calories_portion": 400,
  "proteines": 25.0,
  "glucides": 40.0,
  "lipides": 12.0,
  "fibres": 3.0,
  "astuces": "Conseil pratique pour réussir la recette",
  "erreurs_a_eviter": "Erreur classique à ne pas commettre",
  "variantes": "Comment adapter ou personnaliser la recette",
  "etapes_resume": "Étape 1 : ... Étape 2 : ... Étape 3 : ..."
}

Contraintes de valeurs :
- difficulte : exactement "Facile", "Intermédiaire" ou "Difficile"
- type_plat : exactement un de : "Entrée", "Plat principal", "Dessert", "Snack", "Boisson", "Amuse-bouche"
- type_cuisine : ex. "Française", "Italienne", "Méditerranéenne", "Asiatique", etc.
- regime : exactement un de : "Standard", "Végétarien", "Vegan", "Sans gluten", "Halal", "Keto"
- saison : exactement un de : "Printemps", "Été", "Automne", "Hiver", "Toutes saisons"
- temps_preparation, temps_cuisson, nb_portions, calories_portion : entiers réalistes
- proteines, glucides, lipides, fibres : décimaux réalistes en grammes
- Maximise les ingredients_utilises, ingredients_manquants max 3
- etapes_resume : 3 à 6 étapes concises"""


# ── Service ───────────────────────────────────────────────────────────────────

class OllamaService:
    """Client pour l'API Ollama locale."""

    def suggest_recipes(self, ingredients: list) -> list:
        """Interroge Ollama pour suggérer des recettes à partir des ingrédients.

        Args:
            ingredients: liste de noms d'ingrédients (chaînes de caractères)

        Returns:
            Liste de dicts recettes parsés depuis la réponse JSON

        Raises:
            OllamaNotRunningError: si Ollama n'est pas démarré
            OllamaModelNotFoundError: si le modèle est introuvable
            OllamaTimeoutError: si le délai est dépassé
            OllamaParseError: si la réponse ne peut pas être parsée
        """
        ing_list = ', '.join(ingredients)
        user_prompt = (
            f"Voici les ingrédients disponibles dans mon frigo : {ing_list}.\n"
            "Propose entre 3 et 5 recettes variées (différents types de plats si possible) "
            "qui utilisent au maximum ces ingrédients. Varie les techniques de cuisson."
        )

        payload = {
            "model": OLLAMA_MODEL,
            "system": _SYSTEM_PROMPT,
            "prompt": user_prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            raise OllamaNotRunningError("Ollama n'est pas démarré.")
        except requests.exceptions.Timeout:
            raise OllamaTimeoutError(f"Délai dépassé ({OLLAMA_TIMEOUT}s).")

        # Vérification du statut HTTP
        if response.status_code == 404:
            raise OllamaModelNotFoundError(f"Modèle {OLLAMA_MODEL!r} introuvable (404).")
        if response.status_code != 200:
            body = response.text.lower()
            if "model not found" in body or "model" in body and "not found" in body:
                raise OllamaModelNotFoundError(f"Modèle {OLLAMA_MODEL!r} introuvable.")
            response.raise_for_status()

        data = response.json()

        # Vérification d'un message d'erreur dans la réponse Ollama elle-même
        if data.get("error") and "model" in data["error"].lower():
            raise OllamaModelNotFoundError(data["error"])

        raw = data.get("response", "").strip()

        # ── Étape 1 : parse direct ────────────────────────────────────────────
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # ── Étape 2 : fallback regex — premier tableau JSON trouvé ────────────
        pattern = re.compile(r'\[.*?\]', re.DOTALL)
        for match in pattern.finditer(raw):
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue

        raise OllamaParseError(
            f"Réponse inattendue d'Ollama. Début : {raw[:200]!r}"
        )
