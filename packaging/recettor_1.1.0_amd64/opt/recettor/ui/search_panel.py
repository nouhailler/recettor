import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QGridLayout, QComboBox, QFrame,
    QSizePolicy, QCompleter, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QStringListModel
from PyQt5.QtGui import QPixmap, QFont, QColor

from database import db_manager
from services.search_engine import search
from config import DIFFICULTIES, DISH_TYPES, DIETS, CUISINES
from ui.favorites_panel import ManageFavoritesDialog


class FavoriteIngredientTag(QFrame):
    """Clickable tag for a favorite ingredient in the search panel."""
    clicked = pyqtSignal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFF3CD;
                border: 2px solid #F39C12;
                border-radius: 14px;
                padding: 1px;
            }
            QFrame:hover {
                background-color: #FDEBD0;
                border-color: #D68910;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(4)

        star = QLabel("★")
        star.setStyleSheet("color: #F39C12; font-size: 12px;")
        layout.addWidget(star)

        lbl = QLabel(name.capitalize())
        lbl.setFont(QFont("Arial", 12))
        layout.addWidget(lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name)


class RecipeCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, recipe, parent=None):
        super().__init__(parent)
        self.recipe_id = recipe['id']
        self.setObjectName("recipe-card")
        self.setFixedSize(220, 280)
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.StyledPanel)
        self._build(recipe)

    def _build(self, recipe):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Image
        img_label = QLabel()
        img_label.setFixedSize(200, 130)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("background-color: #F0E8D8; border-radius: 8px;")

        img_path = recipe.get('image_path', '')
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(200, 130, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            img_label.setPixmap(pix)
        else:
            img_label.setText("[ ]")
            img_label.setFont(QFont("Arial", 16))
        layout.addWidget(img_label)

        # Name
        name_label = QLabel(recipe['name'])
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(40)
        layout.addWidget(name_label)

        # Badges row
        badges = QHBoxLayout()
        badges.setSpacing(4)

        if recipe.get('dish_type'):
            badge = QLabel(recipe['dish_type'])
            badge.setObjectName("badge")
            badge.setMaximumWidth(100)
            badges.addWidget(badge)

        diff = recipe.get('difficulty', '')
        if diff:
            diff_badge = QLabel(diff)
            colors = {'Facile': 'badge-green', 'Intermediaire': 'badge', 'Difficile': 'badge-red'}
            diff_badge.setObjectName(colors.get(diff, 'badge'))
            badges.addWidget(diff_badge)

        badges.addStretch()
        layout.addLayout(badges)

        # Time & servings
        prep = recipe.get('prep_time', 0) or 0
        cook = recipe.get('cook_time', 0) or 0
        total = prep + cook
        info_label = QLabel(f"{total} min  /  {recipe.get('servings', 4)} pers.")
        info_label.setStyleSheet("color: #8B6555; font-size: 11px;")
        layout.addWidget(info_label)

        # Diet
        diet = recipe.get('diet', '')
        if diet and diet != 'Standard':
            diet_label = QLabel(diet)
            diet_label.setStyleSheet("color: #27AE60; font-size: 11px; font-weight: bold;")
            layout.addWidget(diet_label)

        # Calories
        cal = recipe.get('calories_per_serving', 0) or 0
        if cal > 0:
            cal_label = QLabel(f"{int(cal)} kcal / pers.")
            cal_label.setStyleSheet("color: #E67E22; font-size: 11px; font-weight: bold;")
            layout.addWidget(cal_label)

        # Rating
        rating = recipe.get('rating', 0) or 0
        if rating > 0:
            stars = '*' * int(rating)
            rating_label = QLabel(f"Note: {stars} ({rating}/5)")
            rating_label.setStyleSheet("font-size: 11px;")
            layout.addWidget(rating_label)

        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.recipe_id)


class SearchPanel(QWidget):
    recipe_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Rechercher une recette")
        title.setObjectName("section-title")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        # Search bar
        search_row = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("search-bar")
        self.search_bar.setPlaceholderText("Rechercher par nom de recette...")
        self.search_bar.setMinimumHeight(45)
        self.search_bar.textChanged.connect(self._on_text_changed)
        search_row.addWidget(self.search_bar)

        clear_btn = QPushButton("X")
        clear_btn.setFixedSize(45, 45)
        clear_btn.setObjectName("secondary-btn")
        clear_btn.clicked.connect(self._clear_search)
        search_row.addWidget(clear_btn)
        layout.addLayout(search_row)

        # Ingredient search
        ing_row = QHBoxLayout()
        ing_label = QLabel("Par ingredient :")
        ing_label.setFixedWidth(130)
        self.ingredient_bar = QLineEdit()
        self.ingredient_bar.setPlaceholderText("Ex: tomate, poulet, fromage...")
        self.ingredient_bar.textChanged.connect(self._on_text_changed)

        # Autocomplétion sur les ingrédients connus
        self._ing_completer_model = QStringListModel()
        ing_completer = QCompleter(self._ing_completer_model, self.ingredient_bar)
        ing_completer.setCaseSensitivity(Qt.CaseInsensitive)
        ing_completer.setFilterMode(Qt.MatchStartsWith)
        ing_completer.setCompletionMode(QCompleter.PopupCompletion)
        ing_completer.setMaxVisibleItems(12)

        popup = ing_completer.popup()
        popup.setFont(QFont("Arial", 15))
        popup.setMinimumWidth(350)
        popup.setMinimumHeight(300)
        popup.setStyleSheet("""
            QListView {
                background: white;
                border: 2px solid #D4A574;
                border-radius: 8px;
                padding: 6px;
                font-size: 15px;
                outline: none;
            }
            QListView::item {
                padding: 10px 16px;
                min-height: 36px;
                border-radius: 4px;
            }
            QListView::item:hover {
                background-color: #FFF3CD;
                color: #2C1810;
            }
            QListView::item:selected {
                background-color: #F39C12;
                color: white;
                font-weight: bold;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #F0E8D8;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #D4A574;
                border-radius: 5px;
                min-height: 20px;
            }
        """)
        self.ingredient_bar.setCompleter(ing_completer)
        self._update_ingredient_completer()

        ing_row.addWidget(ing_label)
        ing_row.addWidget(self.ingredient_bar)
        layout.addLayout(ing_row)

        # Favorites section
        fav_section = QWidget()
        fav_section.setStyleSheet("background-color: #FFFBF0; border-radius: 10px; padding: 4px;")
        fav_main = QVBoxLayout(fav_section)
        fav_main.setContentsMargins(10, 8, 10, 8)
        fav_main.setSpacing(8)

        # Header row
        fav_header = QHBoxLayout()
        fav_title = QLabel("★ Mes ingrédients favoris")
        fav_title.setFont(QFont("Arial", 13, QFont.Bold))
        fav_title.setStyleSheet("color: #E67E22;")
        fav_header.addWidget(fav_title)
        fav_header.addStretch()

        self.search_all_fav_btn = QPushButton("Rechercher avec tous mes favoris")
        self.search_all_fav_btn.setStyleSheet(
            "QPushButton { background-color: #F39C12; color: white; border-radius: 6px; "
            "padding: 4px 12px; font-size: 12px; }"
            "QPushButton:hover { background-color: #D68910; }"
        )
        self.search_all_fav_btn.clicked.connect(self._search_all_favorites)
        fav_header.addWidget(self.search_all_fav_btn)

        manage_btn = QPushButton("Gérer mes favoris")
        manage_btn.setStyleSheet(
            "QPushButton { background-color: #E67E22; color: white; border-radius: 6px; "
            "padding: 4px 12px; font-size: 12px; }"
            "QPushButton:hover { background-color: #D35400; }"
        )
        manage_btn.clicked.connect(self._open_manage_favorites)
        fav_header.addWidget(manage_btn)
        fav_main.addLayout(fav_header)

        # Tags scroll area
        fav_scroll = QScrollArea()
        fav_scroll.setWidgetResizable(True)
        fav_scroll.setFixedHeight(58)
        fav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        fav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        fav_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.fav_tags_widget = QWidget()
        self.fav_tags_widget.setStyleSheet("background: transparent;")
        self.fav_tags_layout = QHBoxLayout(self.fav_tags_widget)
        self.fav_tags_layout.setContentsMargins(0, 0, 0, 0)
        self.fav_tags_layout.setSpacing(8)
        self.fav_tags_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        fav_scroll.setWidget(self.fav_tags_widget)
        fav_main.addWidget(fav_scroll)

        layout.addWidget(fav_section)
        self._refresh_favorites()

        # Filters row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.dish_type_filter = QComboBox()
        self.dish_type_filter.addItem("Tous les types", "")
        for dt in DISH_TYPES:
            self.dish_type_filter.addItem(dt, dt)
        self.dish_type_filter.currentIndexChanged.connect(self._do_search)

        self.diet_filter = QComboBox()
        self.diet_filter.addItem("Tous les regimes", "")
        for d in DIETS:
            self.diet_filter.addItem(d, d)
        self.diet_filter.currentIndexChanged.connect(self._do_search)

        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItem("Toutes difficultes", "")
        for diff in DIFFICULTIES:
            self.difficulty_filter.addItem(diff, diff)
        self.difficulty_filter.currentIndexChanged.connect(self._do_search)

        self.cuisine_filter = QComboBox()
        self.cuisine_filter.addItem("Toutes cuisines", "")
        for c in CUISINES:
            self.cuisine_filter.addItem(c, c)
        self.cuisine_filter.currentIndexChanged.connect(self._do_search)

        for widget in [self.dish_type_filter, self.diet_filter,
                       self.difficulty_filter, self.cuisine_filter]:
            filters_row.addWidget(widget)

        self.fav_recipes_btn = QPushButton("☆ Recettes favorites")
        self.fav_recipes_btn.setCheckable(True)
        self.fav_recipes_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #555; color: #F5F0E8;"
            "  border-radius: 6px; padding: 6px 14px; font-size: 13px;"
            "}"
            "QPushButton:hover { background-color: #F39C12; color: white; }"
            "QPushButton:checked {"
            "  background-color: #F39C12; color: white; font-weight: bold;"
            "}"
        )
        self.fav_recipes_btn.toggled.connect(self._on_fav_recipes_toggled)
        filters_row.addWidget(self.fav_recipes_btn)

        reset_btn = QPushButton("Reinitialiser")
        reset_btn.setObjectName("secondary-btn")
        reset_btn.clicked.connect(self._reset_filters)
        filters_row.addWidget(reset_btn)
        layout.addLayout(filters_row)

        # Calorie filter row
        cal_row = QHBoxLayout()
        cal_row.setSpacing(8)

        self.cal_checkbox = QCheckBox("Calories max par personne :")
        self.cal_checkbox.setStyleSheet("font-size: 14px; color: #2C1810;")
        self.cal_checkbox.toggled.connect(self._on_cal_filter_toggled)
        cal_row.addWidget(self.cal_checkbox)

        self.cal_spinbox = QSpinBox()
        self.cal_spinbox.setRange(50, 3000)
        self.cal_spinbox.setSingleStep(50)
        self.cal_spinbox.setValue(500)
        self.cal_spinbox.setFixedWidth(100)
        self.cal_spinbox.setEnabled(False)
        self.cal_spinbox.valueChanged.connect(self._do_search)
        cal_row.addWidget(self.cal_spinbox)

        cal_unit = QLabel("kcal")
        cal_unit.setStyleSheet("color: #E67E22; font-weight: bold; font-size: 14px;")
        cal_row.addWidget(cal_unit)
        cal_row.addStretch()
        layout.addLayout(cal_row)

        # Results count
        self.results_label = QLabel("Chargement...")
        self.results_label.setStyleSheet("color: #8B6555; font-style: italic;")
        layout.addWidget(self.results_label)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

    def _update_ingredient_completer(self):
        """Recharge la liste d'autocomplétion depuis la base."""
        ingredients = db_manager.get_all_ingredients()
        # Capitaliser pour l'affichage
        self._ing_completer_model.setStringList(
            [i.capitalize() for i in sorted(set(ingredients))]
        )

    def _on_cal_filter_toggled(self, checked):
        self.cal_spinbox.setEnabled(checked)
        self._do_search()

    def _on_text_changed(self):
        self._search_timer.start(400)

    def _do_search(self):
        query = self.search_bar.text().strip()
        ingredient = self.ingredient_bar.text().strip()
        dish_type = self.dish_type_filter.currentData()
        diet = self.diet_filter.currentData()
        difficulty = self.difficulty_filter.currentData()
        cuisine = self.cuisine_filter.currentData()
        max_calories = self.cal_spinbox.value() if self.cal_checkbox.isChecked() else 0

        results = search(
            query=query,
            ingredient=ingredient,
            dish_type=dish_type,
            diet=diet,
            difficulty=difficulty,
            cuisine=cuisine,
            max_calories=max_calories,
            use_fuzzy=bool(query)
        )

        if self.fav_recipes_btn.isChecked():
            fav_ids = {r['id'] for r in db_manager.get_favorite_recipes()}
            if not fav_ids:
                self.results_label.setText(
                    "Aucune recette favorite — ouvrez une recette et cliquez sur ★ Favori."
                )
                self._clear_cards()
                return
            results = [r for r in results if r['id'] in fav_ids]

        self._display_results(results)

    def _display_results(self, recipes):
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        count = len(recipes)
        self.results_label.setText(f"{count} recette(s) trouvee(s)")

        cols = max(1, (self.width() - 40) // 240)
        for i, recipe in enumerate(recipes):
            card = RecipeCard(recipe)
            card.clicked.connect(self.recipe_selected.emit)
            self.cards_layout.addWidget(card, i // cols, i % cols)

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_fav_recipes_toggled(self, checked):
        self.fav_recipes_btn.setText("★ Recettes favorites" if checked else "☆ Recettes favorites")
        self._do_search()

    def _clear_search(self):
        self.search_bar.clear()
        self.ingredient_bar.clear()

    def _reset_filters(self):
        self.search_bar.clear()
        self.ingredient_bar.clear()
        self.dish_type_filter.setCurrentIndex(0)
        self.diet_filter.setCurrentIndex(0)
        self.difficulty_filter.setCurrentIndex(0)
        self.cuisine_filter.setCurrentIndex(0)
        self.cal_checkbox.setChecked(False)
        self.cal_spinbox.setValue(500)
        self.fav_recipes_btn.setChecked(False)

    def _refresh_favorites(self):
        from database import db_manager as dm
        # Clear
        while self.fav_tags_layout.count():
            item = self.fav_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        favorites = dm.get_favorite_ingredients()
        if favorites:
            for name in favorites:
                tag = FavoriteIngredientTag(name)
                tag.clicked.connect(self._on_favorite_clicked)
                self.fav_tags_layout.addWidget(tag)
            self.search_all_fav_btn.setVisible(True)
        else:
            empty = QLabel("Aucun favori — cliquez sur « Gérer mes favoris » pour en ajouter.")
            empty.setStyleSheet("color: #B7950B; font-style: italic; font-size: 12px;")
            self.fav_tags_layout.addWidget(empty)
            self.search_all_fav_btn.setVisible(False)

    def _on_favorite_clicked(self, name):
        self.ingredient_bar.setText(name)
        self._do_search()

    def _search_all_favorites(self):
        from database import db_manager as dm
        favorites = dm.get_favorite_ingredients()
        if favorites:
            # Search one by one and union results via DB
            self.ingredient_bar.setText(', '.join(favorites))
            self._search_with_multiple_favorites(favorites)

    def _search_with_multiple_favorites(self, favorites):
        from database.db_manager import get_connection
        conn = get_connection()
        c = conn.cursor()
        placeholders = ','.join(['?' for _ in favorites])
        c.execute(f"""
            SELECT DISTINCT r.id, r.name, r.description, r.dish_type, r.cuisine_type,
                   r.difficulty, r.prep_time, r.cook_time, r.servings, r.image_path,
                   r.rating, r.ideal_season, r.diet
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE i.name IN ({placeholders})
            ORDER BY r.name
        """, favorites)
        results = [dict(r) for r in c.fetchall()]
        conn.close()
        self._display_results(results)

    def _open_manage_favorites(self):
        dialog = ManageFavoritesDialog(self)
        dialog.favorites_changed.connect(self._refresh_favorites)
        dialog.exec_()
        self._refresh_favorites()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._do_search()

    def refresh(self):
        self._update_ingredient_completer()
        self._do_search()
