import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QComboBox, QGridLayout, QFrame, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QCursor

from services.seasonal_checker import get_seasonal_info, get_current_month, get_current_season_name
from database import db_manager
from config import MONTH_NAMES


SEASON_EMOJIS = {
    'Printemps': 'Printemps', 'Ete': 'Ete', 'Automne': 'Automne', 'Hiver': 'Hiver'
}

SEASON_COLORS = {
    'Printemps': '#27AE60', 'Ete': '#F39C12', 'Automne': '#E67E22', 'Hiver': '#3498DB',
    'Été': '#F39C12'
}


class IngredientTag(QLabel):
    """Tag cliquable pour un ingrédient de saison."""
    clicked = pyqtSignal(str)

    STYLE_NORMAL = (
        "background-color: #D4A574; color: #2C1810; border-radius: 14px; "
        "padding: 6px 14px; font-size: 14px; font-weight: bold; margin: 3px; "
        "border: 2px solid transparent;"
    )
    STYLE_SELECTED = (
        "background-color: #C0392B; color: white; border-radius: 14px; "
        "padding: 6px 14px; font-size: 14px; font-weight: bold; margin: 3px; "
        "border: 2px solid #922B21;"
    )

    def __init__(self, ingredient, parent=None):
        super().__init__(ingredient.capitalize(), parent)
        self.ingredient = ingredient
        self.selected = False
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(self.STYLE_NORMAL)

    def set_selected(self, selected):
        self.selected = selected
        self.setStyleSheet(self.STYLE_SELECTED if selected else self.STYLE_NORMAL)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.ingredient)


class SeasonalRecipeCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, recipe, parent=None):
        super().__init__(parent)
        self.recipe_id = recipe['id']
        self.setObjectName("recipe-card")
        self.setFixedSize(240, 160)
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.StyledPanel)
        self._build(recipe)

    def _build(self, recipe):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Thumbnail
        img_label = QLabel()
        img_label.setFixedSize(80, 80)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("background-color: #F0E8D8; border-radius: 8px;")
        img_path = recipe.get('image_path', '')
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            img_label.setPixmap(pix)
        else:
            img_label.setText("[ ]")
            img_label.setFont(QFont("Arial", 14))
        layout.addWidget(img_label)

        info = QVBoxLayout()
        name = QLabel(recipe['name'])
        name.setFont(QFont("Arial", 12, QFont.Bold))
        name.setWordWrap(True)
        info.addWidget(name)

        prep = (recipe.get('prep_time') or 0) + (recipe.get('cook_time') or 0)
        detail = QLabel(f"{prep} min  |  {recipe.get('servings', 4)} pers.")
        detail.setStyleSheet("color: #8B6555; font-size: 11px;")
        info.addWidget(detail)

        seasonal_count = recipe.get('seasonal_count', 0)
        total = recipe.get('total_ingredients', 1)
        pct = int((seasonal_count / max(total, 1)) * 100)
        seasonal_lbl = QLabel(f"{pct}% ingredients de saison")
        seasonal_lbl.setStyleSheet("color: #27AE60; font-size: 11px;")
        info.addWidget(seasonal_lbl)

        info.addStretch()
        layout.addLayout(info)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.recipe_id)


class SeasonalView(QWidget):
    recipe_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_month = get_current_month()
        self._selected_ingredient = None   # ingrédient actif pour filtre
        self._ingredient_tags = []         # liste des tags pour gérer la sélection
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_row = QHBoxLayout()
        self.season_title = QLabel()
        self.season_title.setObjectName("section-title")
        self.season_title.setFont(QFont("Arial", 20, QFont.Bold))
        header_row.addWidget(self.season_title)
        header_row.addStretch()

        # Month selector
        month_label = QLabel("Mois :")
        header_row.addWidget(month_label)
        self.month_combo = QComboBox()
        for i, name in enumerate(MONTH_NAMES, 1):
            self.month_combo.addItem(name, i)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.currentIndexChanged.connect(self._on_month_changed)
        self.month_combo.setFixedWidth(130)
        header_row.addWidget(self.month_combo)
        layout.addLayout(header_row)

        # Content scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(20)
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _on_month_changed(self):
        self.current_month = self.month_combo.currentData()
        self._selected_ingredient = None
        self.refresh()

    def _on_ingredient_clicked(self, ingredient):
        """Sélectionne ou désélectionne un ingrédient pour filtrer les recettes."""
        if self._selected_ingredient == ingredient:
            # Deuxième clic → réinitialise le filtre
            self._selected_ingredient = None
        else:
            self._selected_ingredient = ingredient

        # Met à jour la surbrillance de tous les tags
        for tag in self._ingredient_tags:
            tag.set_selected(tag.ingredient == self._selected_ingredient)

        # Recharge uniquement la section recettes
        self._refresh_recipes_section()

    def refresh(self):
        self._info = get_seasonal_info(self.current_month)
        season = self._info['season']
        color = SEASON_COLORS.get(season, '#27AE60')

        self.season_title.setText(f"{self._info['month_name']} — {season}")
        self.season_title.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")

        # Vide tout le contenu
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._ingredient_tags = []

        # ── Alertes fin de saison ────────────────────────────────────
        if self._info['ending_soon']:
            alert_box = QGroupBox("Fin de saison bientôt")
            alert_box.setStyleSheet(
                "QGroupBox { border-color: #E67E22; } "
                "QGroupBox::title { color: #E67E22; }"
            )
            alert_layout = QHBoxLayout(alert_box)
            for ing in self._info['ending_soon']:
                tag = QLabel(f"⚠ {ing.capitalize()}")
                tag.setStyleSheet(
                    "background-color: #FDEBD0; color: #E67E22; border-radius: 10px; "
                    "padding: 4px 12px; font-size: 13px; margin: 2px;"
                )
                alert_layout.addWidget(tag)
            alert_layout.addStretch()
            self.content_layout.addWidget(alert_box)

        # ── Ingrédients de saison (cliquables) ───────────────────────
        if self._info['ingredients']:
            hint_lbl = QLabel("Cliquez sur un ingrédient pour filtrer les recettes :")
            hint_lbl.setStyleSheet("color: #8B6555; font-style: italic; font-size: 13px;")
            self.content_layout.addWidget(hint_lbl)

            ing_group = QGroupBox(
                f"Ingrédients de saison — {len(self._info['ingredients'])} disponibles"
            )
            ing_layout = QVBoxLayout(ing_group)

            tag_scroll = QScrollArea()
            tag_scroll.setWidgetResizable(True)
            tag_scroll.setMaximumHeight(150)
            tag_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            tag_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            tag_container = QWidget()
            tag_grid = QGridLayout(tag_container)
            tag_grid.setSpacing(8)
            tag_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            cols = 5
            for i, ing in enumerate(self._info['ingredients']):
                tag = IngredientTag(ing)
                tag.clicked.connect(self._on_ingredient_clicked)
                if ing == self._selected_ingredient:
                    tag.set_selected(True)
                tag_grid.addWidget(tag, i // cols, i % cols)
                self._ingredient_tags.append(tag)

            tag_scroll.setWidget(tag_container)
            ing_layout.addWidget(tag_scroll)
            self.content_layout.addWidget(ing_group)
        else:
            no_ing = QLabel("Aucun ingrédient saisonnier référencé pour ce mois.")
            no_ing.setStyleSheet("color: #8B6555; font-style: italic;")
            self.content_layout.addWidget(no_ing)

        # ── Zone recettes (placeholder, remplie par _refresh_recipes_section) ──
        self._recipes_area = QWidget()
        self._recipes_layout = QVBoxLayout(self._recipes_area)
        self._recipes_layout.setContentsMargins(0, 0, 0, 0)
        self._recipes_layout.setSpacing(10)
        self.content_layout.addWidget(self._recipes_area)

        self.content_layout.addStretch()
        self._refresh_recipes_section()

    def _refresh_recipes_section(self):
        """Recharge uniquement la liste des recettes selon l'ingrédient sélectionné."""
        # Vide la zone recettes
        while self._recipes_layout.count():
            item = self._recipes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ── Titre avec indicateur de filtre ──────────────────────────
        title_row = QHBoxLayout()

        if self._selected_ingredient:
            recipes = db_manager.search_recipes(ingredient=self._selected_ingredient)
            title_txt = (
                f"Recettes avec « {self._selected_ingredient.capitalize()} »"
                f"  —  {len(recipes)} résultat(s)"
            )
            title_color = "#C0392B"

            reset_btn = QPushButton("✕ Voir toutes les recettes de saison")
            reset_btn.setStyleSheet(
                "QPushButton { background-color: #E8D5C0; color: #2C1810; "
                "border-radius: 6px; padding: 4px 14px; font-size: 13px; }"
                "QPushButton:hover { background-color: #D4A574; }"
            )
            reset_btn.clicked.connect(lambda: self._on_ingredient_clicked(self._selected_ingredient))
            title_row.addWidget(reset_btn)
        else:
            recipes = self._info['recipes']
            title_txt = f"Recettes de saison  —  {len(recipes)} recette(s)"
            title_color = "#2C1810"

        recipes_title = QLabel(title_txt)
        recipes_title.setFont(QFont("Arial", 15, QFont.Bold))
        recipes_title.setStyleSheet(f"color: {title_color};")
        title_row.insertWidget(0, recipes_title)
        title_row.addStretch()

        title_widget = QWidget()
        title_widget.setLayout(title_row)
        self._recipes_layout.addWidget(title_widget)

        # ── Grille de cartes ─────────────────────────────────────────
        if recipes:
            cards_widget = QWidget()
            cards_layout = QGridLayout(cards_widget)
            cards_layout.setSpacing(15)
            cards_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            cols = 3
            for i, recipe in enumerate(recipes):
                card = SeasonalRecipeCard(recipe)
                card.clicked.connect(self.recipe_selected.emit)
                cards_layout.addWidget(card, i // cols, i % cols)

            self._recipes_layout.addWidget(cards_widget)
        else:
            if self._selected_ingredient:
                msg = (
                    f"Aucune recette contenant « {self._selected_ingredient.capitalize()} ».\n"
                    "Essayez un autre ingrédient ou ajoutez des recettes !"
                )
            else:
                msg = "Aucune recette de saison.\nAjoutez des recettes avec des ingrédients de saison !"
            no_rec = QLabel(msg)
            no_rec.setStyleSheet("color: #8B6555; font-style: italic; font-size: 14px;")
            no_rec.setAlignment(Qt.AlignCenter)
            self._recipes_layout.addWidget(no_rec)
