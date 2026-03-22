from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QWidget, QFrame, QCompleter,
    QMessageBox, QGridLayout, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from database import db_manager


# ── Tag ingrédient favori ─────────────────────────────────────────────────────

class FavoriteTag(QFrame):
    """Tag supprimable pour un ingrédient favori."""
    removed = pyqtSignal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.setStyleSheet("""
            QFrame {
                background-color: #FFF3CD;
                border: 2px solid #F39C12;
                border-radius: 16px;
                padding: 2px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 6, 4)
        layout.setSpacing(6)

        star = QLabel("★")
        star.setStyleSheet("color: #F39C12; font-size: 14px;")
        layout.addWidget(star)

        name_lbl = QLabel(name.capitalize())
        name_lbl.setFont(QFont("Arial", 13))
        layout.addWidget(name_lbl)

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: #E67E22;
                color: white;
                border-radius: 11px;
                font-size: 11px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover { background-color: #D35400; }
        """)
        del_btn.clicked.connect(lambda: self.removed.emit(self.name))
        layout.addWidget(del_btn)


# ── Carte recette favorite ────────────────────────────────────────────────────

class _FavoriteRecipeRow(QFrame):
    """Ligne affichant une recette favorite avec bouton retirer."""
    open_requested = pyqtSignal(int)
    removed = pyqtSignal(int)

    def __init__(self, recipe: dict, parent=None):
        super().__init__(parent)
        self._recipe_id = recipe['id']
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            "QFrame { background-color: white; border-radius: 8px; "
            "border: 1px solid #E8D5C0; }"
        )
        self._build(recipe)

    def _build(self, recipe: dict):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Étoile déco
        star_lbl = QLabel("★")
        star_lbl.setStyleSheet("color: #F39C12; font-size: 18px;")
        star_lbl.setFixedWidth(22)
        layout.addWidget(star_lbl)

        # Infos recette
        info = QVBoxLayout()
        info.setSpacing(3)

        name_lbl = QLabel(recipe['name'])
        name_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        name_lbl.setStyleSheet("color: #2C1810;")
        info.addWidget(name_lbl)

        badges_row = QHBoxLayout()
        badges_row.setSpacing(6)
        for text, bg, fg in [
            (recipe.get('dish_type') or '',    '#F5CBA7', '#2C1810'),
            (recipe.get('difficulty') or '',   '#D5E8D4', '#1B5E20'),
            (recipe.get('cuisine_type') or '',  '#D6EAF8', '#1A5276'),
        ]:
            if text:
                b = QLabel(text)
                b.setStyleSheet(
                    f"background-color: {bg}; color: {fg}; border-radius: 8px; "
                    "padding: 2px 8px; font-size: 12px; font-weight: bold;"
                )
                badges_row.addWidget(b)

        prep = (recipe.get('prep_time') or 0) + (recipe.get('cook_time') or 0)
        if prep:
            t = QLabel(f"⏱ {prep} min")
            t.setStyleSheet("color: #8B6555; font-size: 12px;")
            badges_row.addWidget(t)

        badges_row.addStretch()
        info.addLayout(badges_row)
        layout.addLayout(info, 1)

        # Bouton ouvrir
        open_btn = QPushButton("Ouvrir")
        open_btn.setFixedWidth(72)
        open_btn.setStyleSheet(
            "QPushButton { background-color: #D4A574; color: #2C1810; border-radius: 6px; "
            "padding: 5px 10px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #C49060; }"
        )
        open_btn.clicked.connect(lambda: self.open_requested.emit(self._recipe_id))
        layout.addWidget(open_btn)

        # Bouton retirer
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #C0392B; "
            "border: none; font-size: 16px; font-weight: bold; padding: 0; }"
            "QPushButton:hover { color: #922B21; }"
        )
        del_btn.clicked.connect(lambda: self.removed.emit(self._recipe_id))
        layout.addWidget(del_btn)


# ── Dialog principal ──────────────────────────────────────────────────────────

class ManageFavoritesDialog(QDialog):
    favorites_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mes Favoris")
        self.setMinimumSize(620, 540)
        self.resize(680, 580)
        self._build_ui()
        self._refresh_ingredients()
        self._refresh_recipes()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── En-tête ───────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background-color: #2C1810;")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 12)
        h_layout.setSpacing(4)

        title = QLabel("★ Mes Favoris")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #F39C12;")
        h_layout.addWidget(title)

        subtitle = QLabel("Retrouvez vos ingrédients et recettes préférés en un clin d'œil.")
        subtitle.setStyleSheet("color: #D4A574; font-size: 13px;")
        h_layout.addWidget(subtitle)
        layout.addWidget(header)

        # ── Onglets ───────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.addTab(self._build_ingredients_tab(), "★ Ingrédients")
        self._tabs.addTab(self._build_recipes_tab(),     "★ Recettes")
        layout.addWidget(self._tabs)

        # ── Footer ────────────────────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet("background-color: #F5F0E8; border-top: 1px solid #E8D5C0;")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 10, 20, 10)
        f_layout.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        f_layout.addWidget(close_btn)
        layout.addWidget(footer)

    # ── Onglet ingrédients ────────────────────────────────────────────

    def _build_ingredients_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        desc = QLabel(
            "Ajoutez vos ingrédients préférés pour les retrouver rapidement "
            "et rechercher des recettes qui les utilisent."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7F8C8D; font-size: 13px;")
        layout.addWidget(desc)

        # Saisie
        add_lbl = QLabel("Ajouter un ingrédient favori :")
        add_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(add_lbl)

        add_row = QHBoxLayout()
        add_row.setSpacing(10)

        self.add_edit = QLineEdit()
        self.add_edit.setPlaceholderText("Ex : tomate, poulet, basilic...")
        self.add_edit.setMinimumHeight(38)
        self.add_edit.setFont(QFont("Arial", 13))
        known = db_manager.get_all_ingredients()
        completer = QCompleter(known)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.add_edit.setCompleter(completer)
        self.add_edit.returnPressed.connect(self._add_ingredient)
        add_row.addWidget(self.add_edit)

        add_btn = QPushButton("★ Ajouter")
        add_btn.setMinimumHeight(38)
        add_btn.setFont(QFont("Arial", 13, QFont.Bold))
        add_btn.setStyleSheet(
            "QPushButton { background-color: #F39C12; color: white; border-radius: 8px; padding: 4px 16px; }"
            "QPushButton:hover { background-color: #D68910; }"
        )
        add_btn.clicked.connect(self._add_ingredient)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #E74C3C; font-size: 12px;")
        layout.addWidget(self.error_lbl)

        lbl = QLabel("Mes ingrédients favoris :")
        lbl.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(160)
        self.tags_container = QWidget()
        self.tags_layout = QGridLayout(self.tags_container)
        self.tags_layout.setSpacing(10)
        self.tags_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.tags_container)
        layout.addWidget(scroll)

        self.ing_empty_lbl = QLabel("Aucun ingrédient favori pour l'instant.")
        self.ing_empty_lbl.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 13px;")
        self.ing_empty_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ing_empty_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        clear_btn = QPushButton("Tout supprimer")
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #E74C3C; color: white; border-radius: 6px; padding: 6px 16px; }"
            "QPushButton:hover { background-color: #C0392B; }"
        )
        clear_btn.clicked.connect(self._clear_all_ingredients)
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)

        return tab

    # ── Onglet recettes ───────────────────────────────────────────────

    def _build_recipes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        desc = QLabel(
            "Vos recettes favorites — cliquez sur l'étoile ★ dans une fiche recette "
            "pour l'ajouter ici."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7F8C8D; font-size: 13px;")
        layout.addWidget(desc)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #F5F0E8; }")

        self._recipes_container = QWidget()
        self._recipes_container.setStyleSheet("background-color: #F5F0E8;")
        self._recipes_layout = QVBoxLayout(self._recipes_container)
        self._recipes_layout.setContentsMargins(0, 0, 0, 0)
        self._recipes_layout.setSpacing(8)
        self._recipes_layout.setAlignment(Qt.AlignTop)

        self.rec_empty_lbl = QLabel(
            "Aucune recette favorite pour l'instant.\n\n"
            "Ouvrez une recette et cliquez sur ☆ Favori dans l'en-tête."
        )
        self.rec_empty_lbl.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 13px;")
        self.rec_empty_lbl.setAlignment(Qt.AlignCenter)
        self._recipes_layout.addWidget(self.rec_empty_lbl)

        scroll.setWidget(self._recipes_container)
        layout.addWidget(scroll)

        return tab

    # ── Rafraîchissement ingrédients ──────────────────────────────────

    def _refresh_ingredients(self):
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        favorites = db_manager.get_favorite_ingredients()
        self.ing_empty_lbl.setVisible(len(favorites) == 0)

        cols = 3
        for i, name in enumerate(favorites):
            tag = FavoriteTag(name)
            tag.removed.connect(self._remove_ingredient)
            self.tags_layout.addWidget(tag, i // cols, i % cols)

        self.favorites_changed.emit()

    # ── Rafraîchissement recettes ─────────────────────────────────────

    def _refresh_recipes(self):
        while self._recipes_layout.count():
            item = self._recipes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recipes = db_manager.get_favorite_recipes()
        if not recipes:
            self._recipes_layout.addWidget(self.rec_empty_lbl)
            self.rec_empty_lbl.show()
            return

        self.rec_empty_lbl.hide()
        for recipe in recipes:
            row = _FavoriteRecipeRow(recipe)
            row.open_requested.connect(self._open_recipe)
            row.removed.connect(self._remove_recipe)
            self._recipes_layout.addWidget(row)

    # ── Actions ingrédients ───────────────────────────────────────────

    def _add_ingredient(self):
        name = self.add_edit.text().strip()
        if not name:
            self.error_lbl.setText("Veuillez saisir un nom d'ingrédient.")
            return
        if db_manager.is_favorite_ingredient(name):
            self.error_lbl.setText(f"« {name} » est déjà dans vos favoris.")
            return
        db_manager.add_favorite_ingredient(name)
        self.add_edit.clear()
        self.error_lbl.setText("")
        self._refresh_ingredients()

    def _remove_ingredient(self, name):
        db_manager.remove_favorite_ingredient(name)
        self._refresh_ingredients()

    def _clear_all_ingredients(self):
        favorites = db_manager.get_favorite_ingredients()
        if not favorites:
            return
        reply = QMessageBox.question(
            self, "Confirmer",
            "Supprimer tous vos ingrédients favoris ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for name in favorites:
                db_manager.remove_favorite_ingredient(name)
            self._refresh_ingredients()

    # ── Actions recettes ──────────────────────────────────────────────

    def _open_recipe(self, recipe_id: int):
        from ui.recipe_view import RecipeViewDialog
        recipe = db_manager.get_recipe_by_id(recipe_id)
        if recipe:
            dlg = RecipeViewDialog(recipe, self)
            dlg.exec_()
            self._refresh_recipes()

    def _remove_recipe(self, recipe_id: int):
        db_manager.remove_favorite_recipe(recipe_id)
        self._refresh_recipes()
        self.favorites_changed.emit()
