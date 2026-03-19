import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QGridLayout, QFrame, QLineEdit, QCompleter
)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont, QPixmap, QCursor

from database import db_manager


class FridgeIngredientTag(QFrame):
    """Removable ingredient tag displayed in the fridge zone."""
    removed = pyqtSignal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.setStyleSheet("""
            QFrame {
                background-color: #D5E8D4;
                border: 2px solid #82B366;
                border-radius: 14px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 3, 6, 3)
        layout.setSpacing(4)

        lbl = QLabel(name.capitalize())
        lbl.setFont(QFont("Arial", 12))
        lbl.setStyleSheet("color: #1B5E20; background: transparent; border: none;")
        layout.addWidget(lbl)

        btn = QPushButton("×")
        btn.setFixedSize(22, 22)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1B5E20;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover { color: #C0392B; }
        """)
        btn.clicked.connect(lambda: self.removed.emit(self.name))
        layout.addWidget(btn)


class FridgeRecipeCard(QFrame):
    """Recipe card showing ingredient match with fridge contents."""
    clicked = pyqtSignal(int)

    def __init__(self, recipe, parent=None):
        super().__init__(parent)
        self.recipe_id = recipe['id']
        self.setObjectName("recipe-card")
        self.setFixedSize(290, 150)
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
        info.setSpacing(4)

        name = QLabel(recipe['name'])
        name.setFont(QFont("Arial", 11, QFont.Bold))
        name.setWordWrap(True)
        info.addWidget(name)

        # Match badge
        pct = recipe.get('match_pct', 0)
        matching = recipe.get('matching_count', 0)
        total = recipe.get('total_ingredients', 1)

        if pct >= 80:
            match_color, match_bg = "#1B5E20", "#D5E8D4"
        elif pct >= 50:
            match_color, match_bg = "#E67E22", "#FDEBD0"
        else:
            match_color, match_bg = "#C0392B", "#FADBD8"

        match_lbl = QLabel(f"{matching}/{total} ingrédients  ({pct}%)")
        match_lbl.setStyleSheet(
            f"color: {match_color}; background-color: {match_bg}; "
            f"border-radius: 8px; padding: 3px 10px; font-size: 12px; font-weight: bold;"
        )
        info.addWidget(match_lbl)

        prep = (recipe.get('prep_time') or 0) + (recipe.get('cook_time') or 0)
        detail = QLabel(f"{prep} min  |  {recipe.get('servings', 4)} pers.")
        detail.setStyleSheet("color: #8B6555; font-size: 11px;")
        info.addWidget(detail)

        cal = recipe.get('calories_per_serving', 0) or 0
        if cal > 0:
            cal_lbl = QLabel(f"{int(cal)} kcal / pers.")
            cal_lbl.setStyleSheet("color: #E67E22; font-size: 11px;")
            info.addWidget(cal_lbl)

        info.addStretch()
        layout.addLayout(info)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.recipe_id)


class FridgeView(QWidget):
    recipe_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fridge = []   # list of lowercase ingredient names
        self._build_ui()
        self._update_completer()
        self._load_from_db()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ── Title ────────────────────────────────────────────────────
        title = QLabel("Mon Frigo")
        title.setObjectName("section-title")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel(
            "Ajoutez les ingrédients disponibles dans votre frigo — "
            "les recettes réalisables s'affichent automatiquement, "
            "triées par taux de compatibilité."
        )
        subtitle.setStyleSheet("color: #8B6555; font-style: italic; font-size: 13px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # ── Ingredient input ─────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.ing_input = QLineEdit()
        self.ing_input.setPlaceholderText("Tapez un ingrédient et appuyez sur Entrée...")
        self.ing_input.setMinimumHeight(42)
        self.ing_input.returnPressed.connect(self._add_ingredient)

        self._completer_model = QStringListModel()
        completer = QCompleter(self._completer_model, self.ing_input)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setMaxVisibleItems(12)
        popup = completer.popup()
        popup.setFont(QFont("Arial", 14))
        popup.setMinimumWidth(320)
        popup.setMinimumHeight(280)
        popup.setStyleSheet("""
            QListView {
                background: white;
                border: 2px solid #82B366;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }
            QListView::item { padding: 8px 14px; min-height: 32px; border-radius: 4px; }
            QListView::item:hover { background-color: #D5E8D4; }
            QListView::item:selected { background-color: #82B366; color: white; font-weight: bold; }
            QScrollBar:vertical { width: 10px; background: #F0E8D8; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #82B366; border-radius: 5px; min-height: 20px; }
        """)
        self.ing_input.setCompleter(completer)

        add_btn = QPushButton("+ Ajouter")
        add_btn.setMinimumHeight(42)
        add_btn.setStyleSheet(
            "QPushButton { background-color: #27AE60; color: white; border-radius: 8px; "
            "padding: 6px 20px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1E8449; }"
        )
        add_btn.clicked.connect(self._add_ingredient)

        input_row.addWidget(self.ing_input)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        # ── Fridge zone header ───────────────────────────────────────
        fridge_header = QHBoxLayout()
        self.fridge_count_lbl = QLabel("Frigo vide")
        self.fridge_count_lbl.setStyleSheet(
            "color: #1B5E20; font-weight: bold; font-size: 14px;"
        )
        fridge_header.addWidget(self.fridge_count_lbl)
        fridge_header.addStretch()

        clear_btn = QPushButton("Vider le frigo")
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #E8D5C0; color: #2C1810; border-radius: 6px; "
            "padding: 4px 14px; font-size: 12px; }"
            "QPushButton:hover { background-color: #D4A574; }"
        )
        clear_btn.clicked.connect(self._clear_fridge)
        fridge_header.addWidget(clear_btn)
        layout.addLayout(fridge_header)

        # ── Fridge tags scroll area ───────────────────────────────────
        fridge_scroll = QScrollArea()
        fridge_scroll.setWidgetResizable(True)
        fridge_scroll.setFixedHeight(68)
        fridge_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        fridge_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        fridge_scroll.setStyleSheet(
            "QScrollArea { border: 2px dashed #82B366; border-radius: 10px; "
            "background-color: #F0FFF0; }"
        )

        self.tags_widget = QWidget()
        self.tags_widget.setStyleSheet("background: transparent;")
        self.tags_layout = QHBoxLayout(self.tags_widget)
        self.tags_layout.setContentsMargins(8, 6, 8, 6)
        self.tags_layout.setSpacing(8)
        self.tags_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        fridge_scroll.setWidget(self.tags_widget)
        layout.addWidget(fridge_scroll)

        # ── Results label ─────────────────────────────────────────────
        self.results_lbl = QLabel("Ajoutez des ingrédients pour voir les recettes.")
        self.results_lbl.setStyleSheet("color: #8B6555; font-style: italic; font-size: 13px;")
        layout.addWidget(self.results_lbl)

        # ── Recipe cards grid ─────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

    # ── Internal helpers ──────────────────────────────────────────────

    def _update_completer(self):
        ingredients = db_manager.get_all_ingredients()
        self._completer_model.setStringList(
            [i.capitalize() for i in sorted(set(ingredients))]
        )

    def _load_from_db(self):
        """Restore fridge contents saved from the previous session."""
        for name in db_manager.get_fridge_ingredients():
            if name not in self._fridge:
                self._fridge.append(name)
                tag = FridgeIngredientTag(name)
                tag.removed.connect(self._remove_ingredient)
                self.tags_layout.addWidget(tag)
        self._update_fridge_label()
        if self._fridge:
            self._search()

    def _add_ingredient(self):
        name = self.ing_input.text().strip().lower()
        self.ing_input.clear()
        if not name or name in self._fridge:
            return

        self._fridge.append(name)
        db_manager.add_fridge_ingredient(name)

        tag = FridgeIngredientTag(name)
        tag.removed.connect(self._remove_ingredient)
        self.tags_layout.addWidget(tag)

        self._update_fridge_label()
        self._search()

    def _remove_ingredient(self, name):
        if name in self._fridge:
            self._fridge.remove(name)
        db_manager.remove_fridge_ingredient(name)
        for i in range(self.tags_layout.count()):
            item = self.tags_layout.itemAt(i)
            if item and isinstance(item.widget(), FridgeIngredientTag):
                if item.widget().name == name:
                    item.widget().deleteLater()
                    break
        self._update_fridge_label()
        self._search()

    def _clear_fridge(self):
        self._fridge.clear()
        db_manager.clear_fridge_ingredients()
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._update_fridge_label()
        self._search()

    def _update_fridge_label(self):
        n = len(self._fridge)
        if n == 0:
            self.fridge_count_lbl.setText("Frigo vide")
        elif n == 1:
            self.fridge_count_lbl.setText("1 ingrédient dans le frigo")
        else:
            self.fridge_count_lbl.setText(f"{n} ingrédients dans le frigo")

    def _search(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._fridge:
            self.results_lbl.setText("Ajoutez des ingrédients pour voir les recettes.")
            return

        recipes = db_manager.search_recipes_by_fridge(self._fridge)

        if not recipes:
            self.results_lbl.setText("Aucune recette ne correspond aux ingrédients du frigo.")
            return

        n = len(recipes)
        self.results_lbl.setText(
            f"{n} recette(s) trouvée(s) — triées par compatibilité décroissante"
        )

        cols = max(1, (self.width() - 60) // 310)
        for i, recipe in enumerate(recipes):
            card = FridgeRecipeCard(recipe)
            card.clicked.connect(self.recipe_selected.emit)
            self.cards_layout.addWidget(card, i // cols, i % cols)

    # ── Public interface ──────────────────────────────────────────────

    def refresh(self):
        """Called when recipes are added/deleted globally."""
        self._update_completer()
        if self._fridge:
            self._search()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fridge:
            self._search()
