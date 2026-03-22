# 🍽️ Recettor

> **Votre carnet de recettes intelligent, entièrement local et sans abonnement.**

Recettor est une application de bureau développée en Python / PyQt5 qui centralise toutes vos recettes de cuisine dans une base de données SQLite stockée sur votre machine. Recherche floue, mode frigo, vue saisonnière, calculateur calorique… tout est là.

---

## ✨ Fonctionnalités

| 🔍 Recherche | 🌿 Saisonnalité | 🧊 Mon Frigo |
|---|---|---|
| Recherche floue par nom | Ingrédients du mois | Suggestions par compatibilité |
| Filtre par ingrédient | Alertes fin de saison | Code couleur vert / orange / rouge |
| Filtre régime, difficulté, cuisine | Navigation mois par mois | Persistance entre sessions |
| Filtre calorique (kcal / portion) | Recettes de saison filtrables | Autocomplétion des ingrédients |
| **Filtre ★ Recettes favorites** | | **✨ Suggestions IA via Ollama** |

| 📋 Fiche recette | ➕ Saisie | 📦 Import / Export |
|---|---|---|
| 6 onglets détaillés | Formulaire en 9 onglets | Format JSON standardisé |
| Graphique macronutriments | Photo de la recette | Import partiel avec rapport d'erreurs |
| Calculateur de portions | Autocomplétion ingrédients | Export intégral de la base |
| Tableau ingrédients ajustés | 14 allergènes gérés | Template d'import inclus |
| **★ Bouton Favori** | | |

| ★ Favoris | 🛒 Liste de courses | 🤖 IA locale |
|---|---|---|
| Ingrédients favoris persistants | Ajout manuel d'articles | Ollama (100 % local, sans Internet) |
| Recettes favorites avec étoile | Cochage au fur et à mesure | Génère recettes créatives |
| Filtre favoris dans la recherche | Ajout auto depuis suggestions IA | Sauvegarde enrichie (nutrition, astuces) |
| Accès rapide depuis la barre latérale | Suppression des cochés / tout vider | Compatible qwen2.5:3b / 7b / 14b |

---

## 📸 Aperçu

```
┌─────────────────────────────────────────────────────────┐
│  🍴 Recettor                                [_ □ ×]     │
├──────────┬──────────────────────────────────────────────┤
│          │  🔍 Rechercher une recette  [☆ Favoris]      │
│ Recherche│                                              │
│          │  ┌─────────────┐  ┌─────────────┐           │
│Saisonnali│  │ 🥗 Salade   │  │ 🍝 Pasta    │           │
│          │  │ Niçoise     │  │ Carbonara   │           │
│Mon Frigo │  │ Facile 20min│  │ Inter. 30min│           │
│          │  │ 320 kcal    │  │ 680 kcal    │           │
│🛒 Courses│  └─────────────┘  └─────────────┘           │
│          │                                              │
│  Ajouter │                                              │
│          │                                              │
│ ★ Favoris│                                              │
├──────────┴──────────────────────────────────────────────┤
│  📅 dimanche 22 mars 2026  |  Saison : Printemps  |  53 recettes │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prérequis

- Python **3.8+**
- pip

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/nouhailler/recettor.git
cd recettor

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
#    Linux / macOS
source venv/bin/activate
#    Windows
venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python main.py
```

> 🗄️ La base de données SQLite est créée automatiquement au premier lancement dans `data/recettes.db`.

### Pour les suggestions IA (optionnel)

```bash
# Installer Ollama (voir https://ollama.com)
ollama pull qwen2.5:7b   # Modèle recommandé (~8 Go RAM)
ollama serve             # Lancer le service (dans un terminal séparé)
```

Le modèle et l'URL sont configurables dans `config.py` (`OLLAMA_MODEL`, `OLLAMA_BASE_URL`).

---

## 📦 Dépendances

| Package | Rôle |
|---|---|
| `PyQt5` | Interface graphique |
| `fuzzywuzzy` | Recherche floue (distance de Levenshtein) |
| `python-Levenshtein` | Accélérateur pour fuzzywuzzy |
| `requests` | Appels HTTP vers l'API locale Ollama |

---

## 🗂️ Structure du projet

```
recettor/
│
├── 🐍 main.py                    # Point d'entrée (HiDPI activé)
├── ⚙️  config.py                  # Chemins, constantes, config Ollama
├── 📋 requirements.txt
│
├── 🖼️  ui/                        # Interface graphique (PyQt5)
│   ├── main_window.py            # Fenêtre principale + navigation
│   ├── search_panel.py           # Panneau de recherche (filtre favoris)
│   ├── seasonal_view.py          # Vue saisonnière
│   ├── fridge_view.py            # Mode Mon Frigo + bouton IA Ollama
│   ├── shopping_list_view.py     # 🛒 Liste de courses
│   ├── ollama_suggestions_dialog.py  # ✨ Dialog suggestions IA
│   ├── recipe_view.py            # Fiche recette (6 onglets + ★ favori)
│   ├── favorites_panel.py        # Favoris ingrédients + recettes (2 onglets)
│   ├── help_dialog.py            # Aide complète (F1)
│   └── forms/
│       ├── add_recipe.py         # Formulaire ajout (9 onglets)
│       └── edit_recipe.py        # Formulaire modification
│
├── 🗄️  database/
│   ├── db_manager.py             # Toutes les opérations SQLite
│   └── migrations.py             # Migrations de schéma
│
├── 🔧 services/
│   ├── search_engine.py          # Moteur de recherche floue
│   ├── seasonal_checker.py       # Calcul saison courante
│   ├── ollama_service.py         # 🤖 Client Ollama (génération IA)
│   └── validator.py              # Validation des imports JSON
│
├── 📤 import_export/
│   ├── json_handler.py           # Import / export JSON
│   └── templates/
│       └── recipe_template.json  # Template annoté d'import
│
└── 🎨 assets/
    ├── styles/main.qss           # Feuille de style Qt
    └── images/                   # Photos des recettes (local)
```

---

## 🍳 Guide rapide

<details>
<summary><b>🔍 Rechercher une recette</b></summary>

1. Cliquez sur **Rechercher** dans la barre latérale
2. Tapez un nom de recette (la recherche est **floue** : les fautes de frappe sont tolérées)
3. Affinez avec les filtres : type de plat, régime, difficulté, cuisine
4. Cochez **Calories max** pour n'afficher que les recettes sous un seuil calorique
5. Cliquez sur une carte pour ouvrir la fiche complète

</details>

<details>
<summary><b>🌿 Cuisiner de saison</b></summary>

1. Cliquez sur **Saisonnalité** — le mois courant est sélectionné automatiquement
2. Parcourez les ingrédients disponibles ce mois-ci
3. Cliquez sur un ingrédient pour filtrer les recettes qui l'utilisent
4. Une alerte ⚠️ signale les ingrédients qui arrivent en fin de saison

</details>

<details>
<summary><b>🧊 Utiliser le mode Mon Frigo</b></summary>

1. Cliquez sur **Mon Frigo**
2. Tapez les ingrédients disponibles dans votre frigo et ajoutez-les
3. Les recettes apparaissent automatiquement, triées par taux de compatibilité :
   - 🟢 **≥ 80 %** — recette très réalisable
   - 🟠 **50–79 %** — il manque quelques ingrédients
   - 🔴 **< 50 %** — peu réalisable avec le frigo actuel
4. Le contenu du frigo est **sauvegardé** entre les sessions

</details>

<details>
<summary><b>✨ Obtenir des suggestions IA (Ollama)</b></summary>

1. Assurez-vous qu'Ollama est démarré : `ollama serve`
2. Cliquez sur **Mon Frigo** et ajoutez vos ingrédients
3. Cliquez sur **✨ Suggestions IA (Ollama)** en bas du panneau
4. Patientez pendant la génération (le modèle `qwen2.5:7b` prend ~90 s sur CPU)
5. Parcourez les recettes suggérées :
   - **🔍 Voir le détail** — affiche les étapes numérotées
   - **💾 Sauvegarder dans Recettor** — enregistre dans votre base avec nutrition et astuces
   - **🛒 Ajouter manquants** — ajoute les ingrédients manquants à la liste de courses

> 💡 Modèle configurable dans `config.py` : `OLLAMA_MODEL = "qwen2.5:7b"`

</details>

<details>
<summary><b>🛒 Gérer la liste de courses</b></summary>

1. Cliquez sur **🛒 Liste de courses** dans la barre latérale
2. Ajoutez des articles manuellement ou laissez-les s'ajouter via les suggestions IA
3. Cochez les articles au fur et à mesure de vos achats (texte barré)
4. Cliquez sur **Supprimer les cochés** pour nettoyer la liste

</details>

<details>
<summary><b>★ Gérer les recettes favorites</b></summary>

1. Ouvrez une fiche recette et cliquez sur **☆ Favori** dans l'en-tête
2. L'étoile passe en orange **(★ Favori)** — la recette est ajoutée aux favoris
3. Retrouvez toutes vos favorites dans **★ Favoris → onglet ★ Recettes**
4. Ou activez le filtre **☆ Recettes favorites** dans le panneau Recherche

</details>

<details>
<summary><b>📊 Utiliser le calculateur calorique</b></summary>

1. Ouvrez une fiche recette → onglet **Nutrition**
2. Saisissez votre objectif calorique (ex : 400 kcal)
3. Recettor calcule automatiquement :
   - Le **pourcentage d'une portion** correspondant à votre objectif
   - Le **poids estimé** dans l'assiette
   - Les **quantités ajustées** de chaque ingrédient

```
Exemple : Bœuf Bourguignon à 415 kcal/portion, objectif 400 kcal
  ratio   = 400 / 415 = 0,96
  résultat = 96% d'une portion individuelle (415 kcal × 96% = 400 kcal)
```

</details>

<details>
<summary><b>📤 Importer des recettes JSON</b></summary>

1. Menu **Outils → Importer des recettes (JSON)**
2. Sélectionnez votre fichier JSON
3. Les recettes valides sont importées ; un rapport liste les éventuelles erreurs

Consultez **Outils → Voir le format d'import** pour le template complet avec tous les champs disponibles.

> ⚠️ Il n'y a pas de détection de doublons : effectuez une sauvegarde avant un import massif.

</details>

---

## 📐 Calculs & formules

<details>
<summary><b>Voir le détail de tous les calculs</b></summary>

### Recherche floue
```
score = max( partial_ratio(requête, nom), partial_ratio(requête, description) )
Seuil : score ≥ 60 — tri par score décroissant
```

### Compatibilité Frigo
```
score = ROUND( ingrédients_communs / total_ingrédients_recette × 100 )
```

### Macronutriments (coefficients Atwater)
```
Énergie = glucides × 4  +  protéines × 4  +  lipides × 9   (kcal)
```

### Calculateur calorique
```
ratio          = objectif_kcal / calories_par_portion
poids_assiette = poids_portion_moyen × ratio
quantité_ing   = (quantité_recette / portions) × ratio
```

### Normalisation des ingrédients
```
œuf → oeuf,  æ → ae  (+ minuscules + strip)
Garantit que « Œuf », « oeuf », « OEUF » désignent le même ingrédient.
```

</details>

---

## 🗄️ Format JSON d'import

```jsonc
{
  "recettes": [
    {
      "nom": "Ratatouille",                // ← OBLIGATOIRE
      "type_plat": "Plat principal",       // Entrée | Plat principal | Dessert | …
      "regime": "Végétarien",              // Standard | Végétarien | Sans lactose | …
      "difficulte": "Facile",              // Facile | Intermédiaire | Difficile
      "saison_ideale": "Été",             // Toutes saisons | Printemps | Été | Automne | Hiver
      "type_cuisine": "Française",
      "calories": 280,
      "portions": 4,
      "temps_preparation": 20,
      "temps_cuisson": 45,
      "ingredients": [
        { "nom": "tomate", "quantite": 4, "unite": "pièce", "preparation": "en dés" }
      ],
      "etapes": [
        { "numero": 1, "description": "Couper les légumes.", "duree": 15 }
      ]
    }
  ]
}
```

---

## ⌨️ Raccourcis clavier

| Touche | Action |
|---|---|
| `F1` | Ouvrir l'aide complète |
| `Entrée` | Valider la recherche / ajouter un ingrédient au frigo |

---

## 🛣️ Roadmap

- [x] Liste de courses (ajout manuel + auto depuis suggestions IA)
- [x] Suggestions IA via Ollama (local, sans Internet)
- [x] Recettes favorites (étoile + filtre dans la recherche)
- [ ] Planificateur de menus hebdomadaire
- [ ] Export PDF des fiches recettes
- [ ] Synchronisation multi-appareils
- [ ] Application mobile compagnon

---

## 🤝 Contribution

Les contributions sont les bienvenues !

```bash
# Forker le dépôt, puis :
git checkout -b feature/ma-fonctionnalite
git commit -m "Ajout : ma fonctionnalité"
git push origin feature/ma-fonctionnalite
# Ouvrir une Pull Request
```

---

## 📄 Licence

Ce projet est distribué sous licence **MIT** — libre d'utilisation, de modification et de distribution.

---

<div align="center">

🍴 **Recettor** — *Cuisinez mieux, organisez facilement.*

Fait avec ❤️ et 🐍 Python

</div>
