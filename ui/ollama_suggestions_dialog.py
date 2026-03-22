import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QFrame, QWidget, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database import db_manager


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_steps(etapes_resume: str) -> list:
    """Découpe etapes_resume en étapes individuelles."""
    parts = re.split(r'[EÉeé]tape\s+\d+\s*[:\-]\s*', etapes_resume)
    steps = [s.strip() for s in parts if s.strip()]
    return steps if steps else [etapes_resume]


def _save_to_db(recipe: dict) -> int:
    """Convertit un dict recette Ollama au format db et l'enregistre."""
    from config import OLLAMA_MODEL

    ingredients = []
    for ing in recipe.get('ingredients_utilises', []):
        ingredients.append(
            {'name': ing, 'quantity': 0, 'unit': 'au goût', 'optional': False}
        )
    for ing in recipe.get('ingredients_manquants', []):
        ingredients.append(
            {'name': ing, 'quantity': 0, 'unit': 'au goût', 'optional': True}
        )

    raw_steps = _parse_steps(recipe.get('etapes_resume', ''))
    steps = [
        {'step_number': i + 1, 'description': desc}
        for i, desc in enumerate(raw_steps)
    ]

    tips = []
    if recipe.get('astuces'):
        tips.append({'tip_type': 'Astuces', 'content': recipe['astuces']})
    if recipe.get('erreurs_a_eviter'):
        tips.append({'tip_type': 'Erreurs', 'content': recipe['erreurs_a_eviter']})
    if recipe.get('variantes'):
        tips.append({'tip_type': 'Variantes', 'content': recipe['variantes']})

    nom = recipe.get('nom', 'Recette IA')

    data = {
        'name': nom,
        'description': recipe.get('description_courte', ''),
        'prep_time': recipe.get('temps_preparation', 0),
        'cook_time': recipe.get('temps_cuisson', 0),
        'difficulty': recipe.get('difficulte', 'Facile'),
        'servings': recipe.get('nb_portions', 4),
        'dish_type': recipe.get('type_plat', ''),
        'cuisine_type': recipe.get('type_cuisine', ''),
        'diet': recipe.get('regime', 'Standard'),
        'ideal_season': recipe.get('saison', 'Toutes saisons'),
        'calories_per_serving': recipe.get('calories_portion', 0),
        'proteins': recipe.get('proteines', 0),
        'carbs': recipe.get('glucides', 0),
        'fats': recipe.get('lipides', 0),
        'fiber': recipe.get('fibres', 0),
        'source': OLLAMA_MODEL,
        'notes': f"{nom}\nRecette générée par : {OLLAMA_MODEL}",
        'ingredients': ingredients,
        'steps': steps,
        'tips': tips,
    }
    return db_manager.add_recipe(data)


# ── Dialog de détail ──────────────────────────────────────────────────────────

class OllamaRecipeDetailDialog(QDialog):
    """Vue détaillée d'une recette IA avec étapes numérotées."""

    def __init__(self, recipe: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(recipe.get('nom', 'Détail recette'))
        self.setMinimumWidth(540)
        self.resize(580, 620)
        self._build_ui(recipe)

    def _build_ui(self, recipe: dict):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── En-tête violet ────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background-color: #6C3483;")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(4)

        nom_lbl = QLabel(recipe.get('nom', '—'))
        nom_lbl.setFont(QFont("Arial", 15, QFont.Bold))
        nom_lbl.setStyleSheet("color: white;")
        nom_lbl.setWordWrap(True)
        h_layout.addWidget(nom_lbl)

        desc = recipe.get('description_courte', '')
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(
                "color: #E8D5FF; font-style: italic; font-size: 13px;"
            )
            desc_lbl.setWordWrap(True)
            h_layout.addWidget(desc_lbl)

        layout.addWidget(header)

        # ── Corps scrollable ──────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #F5F0E8; }")

        body = QWidget()
        body.setStyleSheet("background-color: #F5F0E8;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 16)
        body_layout.setSpacing(12)

        # Temps + difficulté
        temps = recipe.get('temps_preparation', 0)
        diff = recipe.get('difficulte', '')
        diff_colors = {
            'Facile': '#27AE60',
            'Intermédiaire': '#E67E22',
            'Difficile': '#C0392B',
        }
        meta = QLabel(
            f"<span style='color:#8B6555;'>⏱ {temps} min</span>"
            f"  •  <span style='color:{diff_colors.get(diff, '#8B6555')};"
            f"font-weight:bold;'>{diff}</span>"
        )
        meta.setStyleSheet("font-size: 14px;")
        body_layout.addWidget(meta)

        # Séparateur + ingrédients
        body_layout.addWidget(_hline())

        ing_row = QHBoxLayout()
        ing_row.setSpacing(20)

        have = recipe.get('ingredients_utilises', [])
        if have:
            col = QVBoxLayout()
            col.setSpacing(3)
            t = QLabel("✅ Vous avez :")
            t.setFont(QFont("Arial", 12, QFont.Bold))
            t.setStyleSheet("color: #1B5E20;")
            col.addWidget(t)
            for ing in have:
                l = QLabel(f"  • {ing}")
                l.setStyleSheet("color: #27AE60; font-size: 13px;")
                col.addWidget(l)
            col.addStretch()
            ing_row.addLayout(col)

        missing = recipe.get('ingredients_manquants', [])
        if missing:
            col = QVBoxLayout()
            col.setSpacing(3)
            t = QLabel("🛒 Il manque :")
            t.setFont(QFont("Arial", 12, QFont.Bold))
            t.setStyleSheet("color: #A04000;")
            col.addWidget(t)
            for ing in missing:
                l = QLabel(f"  • {ing}")
                l.setStyleSheet("color: #E67E22; font-size: 13px;")
                col.addWidget(l)
            col.addStretch()
            ing_row.addLayout(col)

        ing_row.addStretch()
        body_layout.addLayout(ing_row)

        # Séparateur + étapes
        etapes_raw = recipe.get('etapes_resume', '')
        if etapes_raw:
            body_layout.addWidget(_hline())

            steps_title = QLabel("Étapes")
            steps_title.setFont(QFont("Arial", 13, QFont.Bold))
            steps_title.setStyleSheet("color: #2C1810;")
            body_layout.addWidget(steps_title)

            for i, step in enumerate(_parse_steps(etapes_raw), 1):
                step_frame = QFrame()
                step_frame.setStyleSheet(
                    "QFrame { background-color: white; border-radius: 6px; "
                    "border: 1px solid #E8D5C0; }"
                )
                sf_layout = QHBoxLayout(step_frame)
                sf_layout.setContentsMargins(12, 8, 12, 8)
                sf_layout.setSpacing(10)

                num = QLabel(str(i))
                num.setFixedSize(28, 28)
                num.setAlignment(Qt.AlignCenter)
                num.setStyleSheet(
                    "background-color: #6C3483; color: white; border-radius: 14px; "
                    "font-weight: bold; font-size: 13px;"
                )
                sf_layout.addWidget(num)

                step_lbl = QLabel(step)
                step_lbl.setWordWrap(True)
                step_lbl.setStyleSheet(
                    "color: #2C1810; font-size: 13px; border: none;"
                )
                sf_layout.addWidget(step_lbl, 1)
                body_layout.addWidget(step_frame)

        body_layout.addStretch()
        scroll.setWidget(body)
        layout.addWidget(scroll)

        # ── Footer ────────────────────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet(
            "background-color: #F5F0E8; border-top: 1px solid #E8D5C0;"
        )
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 12, 20, 12)
        f_layout.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        f_layout.addWidget(close_btn)
        layout.addWidget(footer)


# ── Carte recette ─────────────────────────────────────────────────────────────

class _RecipeCard(QFrame):
    """Carte affichant une suggestion de recette IA avec actions."""

    def __init__(self, recipe: dict, parent=None):
        super().__init__(parent)
        self._recipe = recipe
        self.setObjectName("ai-recipe-card")
        self.setStyleSheet("""
            QFrame#ai-recipe-card {
                background-color: white;
                border: 1px solid #E8D5C0;
                border-radius: 10px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._build(recipe)

    def _build(self, recipe: dict):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # ── Nom ──────────────────────────────────────────────────────
        nom = QLabel(recipe.get('nom', '—'))
        nom.setFont(QFont("Arial", 13, QFont.Bold))
        nom.setStyleSheet("color: #2C1810;")
        nom.setWordWrap(True)
        layout.addWidget(nom)

        # ── Description courte ────────────────────────────────────────
        desc = recipe.get('description_courte', '')
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(
                "color: #8B6555; font-style: italic; font-size: 13px;"
            )
            desc_lbl.setWordWrap(True)
            layout.addWidget(desc_lbl)

        # ── Temps + difficulté ─────────────────────────────────────────
        temps = recipe.get('temps_preparation', 0)
        diff = recipe.get('difficulte', '')
        diff_colors = {
            'Facile': '#27AE60',
            'Intermédiaire': '#E67E22',
            'Difficile': '#C0392B',
        }
        meta = QLabel(
            f"<span style='color:#8B6555;'>⏱ {temps} min</span>"
            f"  •  <span style='color:{diff_colors.get(diff, '#8B6555')};"
            f"font-weight:bold;'>{diff}</span>"
        )
        meta.setStyleSheet("font-size: 13px;")
        layout.addWidget(meta)

        # ── Ingrédients (deux colonnes) ────────────────────────────────
        ing_row = QHBoxLayout()
        ing_row.setSpacing(16)

        have = recipe.get('ingredients_utilises', [])
        if have:
            col = QVBoxLayout()
            col.setSpacing(2)
            t = QLabel("✅ Vous avez :")
            t.setFont(QFont("Arial", 11, QFont.Bold))
            t.setStyleSheet("color: #1B5E20;")
            col.addWidget(t)
            for ing in have:
                l = QLabel(f"  • {ing}")
                l.setStyleSheet("color: #27AE60; font-size: 13px;")
                col.addWidget(l)
            col.addStretch()
            ing_row.addLayout(col)

        missing = recipe.get('ingredients_manquants', [])
        if missing:
            col = QVBoxLayout()
            col.setSpacing(2)
            t = QLabel("🛒 Il manque :")
            t.setFont(QFont("Arial", 11, QFont.Bold))
            t.setStyleSheet("color: #A04000;")
            col.addWidget(t)
            for ing in missing:
                l = QLabel(f"  • {ing}")
                l.setStyleSheet("color: #E67E22; font-size: 13px;")
                col.addWidget(l)
            col.addStretch()
            ing_row.addLayout(col)

        ing_row.addStretch()
        layout.addLayout(ing_row)

        # ── Résumé des étapes ─────────────────────────────────────────
        etapes = recipe.get('etapes_resume', '')
        if etapes:
            layout.addWidget(_hline())
            steps_lbl = QLabel(etapes)
            steps_lbl.setStyleSheet(
                "color: #2C1810; font-size: 12px;"
            )
            steps_lbl.setWordWrap(True)
            layout.addWidget(steps_lbl)

        # ── Boutons d'action ──────────────────────────────────────────
        layout.addWidget(_hline())
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        detail_btn = QPushButton("🔍 Voir le détail")
        detail_btn.setStyleSheet(
            "QPushButton { background-color: #F0E8D8; color: #2C1810; "
            "border-radius: 6px; padding: 5px 14px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background-color: #D4A574; }"
        )
        detail_btn.clicked.connect(self._open_detail)
        btn_row.addWidget(detail_btn)

        self._save_btn = QPushButton("💾 Sauvegarder dans Recettor")
        self._save_btn.setStyleSheet(
            "QPushButton { background-color: #27AE60; color: white; "
            "border-radius: 6px; padding: 5px 14px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1E8449; }"
            "QPushButton:disabled { background-color: #BDC3C7; color: #7F8C8D; }"
        )
        self._save_btn.clicked.connect(self._save_recipe)
        btn_row.addWidget(self._save_btn)

        missing = recipe.get('ingredients_manquants', [])
        if missing:
            cart_btn = QPushButton(f"🛒 Ajouter manquants ({len(missing)})")
            cart_btn.setStyleSheet(
                "QPushButton { background-color: #EAF4FB; color: #1A5276; "
                "border-radius: 6px; padding: 5px 14px; font-size: 13px; font-weight: bold; "
                "border: 1px solid #AED6F1; }"
                "QPushButton:hover { background-color: #AED6F1; }"
                "QPushButton:disabled { background-color: #BDC3C7; color: #7F8C8D; }"
            )
            cart_btn.clicked.connect(lambda: self._add_to_shopping_list(missing, cart_btn))
            btn_row.addWidget(cart_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _open_detail(self):
        dlg = OllamaRecipeDetailDialog(self._recipe, self)
        dlg.exec_()

    def _add_to_shopping_list(self, missing: list, btn: 'QPushButton'):
        added = [ing for ing in missing if db_manager.add_shopping_item(ing)]
        already = [ing for ing in missing if ing not in added]

        btn.setEnabled(False)
        btn.setText("✅ Ajoutés !")

        if added:
            msg = f"{len(added)} article(s) ajouté(s) à la liste de courses :\n"
            msg += "\n".join(f"  • {i}" for i in added)
        else:
            msg = "Ces articles sont déjà dans votre liste de courses."
        if already:
            msg += f"\n\nDéjà présent(s) : {', '.join(already)}"

        QMessageBox.information(self, "Liste de courses", msg)

    def _save_recipe(self):
        try:
            _save_to_db(self._recipe)
            self._save_btn.setEnabled(False)
            self._save_btn.setText("✅ Sauvegardée !")
            QMessageBox.information(
                self,
                "Recette sauvegardée",
                f"« {self._recipe.get('nom', 'La recette')} » a été ajoutée "
                "à votre carnet de recettes.\n\n"
                "Vous la retrouverez dans la liste principale."
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Erreur", f"Impossible de sauvegarder la recette :\n{e}"
            )


# ── Dialog principal ──────────────────────────────────────────────────────────

class OllamaSuggestionsDialog(QDialog):
    """Dialog affichant les suggestions de recettes générées par Ollama."""

    def __init__(self, suggestions: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✨ Suggestions IA pour votre frigo")
        self.setMinimumWidth(620)
        self.setMinimumHeight(500)
        self.resize(680, 700)
        self._build_ui(suggestions)

    def _build_ui(self, suggestions: list):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── En-tête ───────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background-color: #2C1810;")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(4)

        title_lbl = QLabel("✨ Suggestions IA pour votre frigo")
        title_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #F5F0E8;")
        h_layout.addWidget(title_lbl)

        count_lbl = QLabel(
            f"{len(suggestions)} recette(s) suggérée(s) • {_model_display()}"
        )
        count_lbl.setStyleSheet("color: #D4A574; font-size: 12px;")
        h_layout.addWidget(count_lbl)

        layout.addWidget(header)

        # ── Zone scrollable ───────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: #F5F0E8; }"
        )

        container = QWidget()
        container.setStyleSheet("background-color: #F5F0E8;")
        cards_layout = QVBoxLayout(container)
        cards_layout.setContentsMargins(20, 20, 20, 20)
        cards_layout.setSpacing(16)

        if not suggestions:
            empty_lbl = QLabel("Aucune suggestion reçue. Réessayez.")
            empty_lbl.setStyleSheet("color: #8B6555; font-style: italic;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            cards_layout.addWidget(empty_lbl)
        else:
            for recipe in suggestions:
                cards_layout.addWidget(_RecipeCard(recipe))

        cards_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # ── Bouton Fermer ─────────────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet(
            "background-color: #F5F0E8; border-top: 1px solid #E8D5C0;"
        )
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 12, 20, 12)
        f_layout.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumWidth(120)
        close_btn.setMinimumHeight(38)
        close_btn.clicked.connect(self.accept)
        f_layout.addWidget(close_btn)
        layout.addWidget(footer)


# ── Utilitaires ───────────────────────────────────────────────────────────────

def _hline() -> QFrame:
    """Séparateur horizontal léger."""
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet("color: #F0E8D8;")
    return sep


def _model_display() -> str:
    try:
        from config import OLLAMA_MODEL
        return OLLAMA_MODEL
    except ImportError:
        return "Ollama"
