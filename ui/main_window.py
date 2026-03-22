import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QStatusBar, QAction, QMessageBox,
    QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from ui.search_panel import SearchPanel
from ui.seasonal_view import SeasonalView
from ui.fridge_view import FridgeView
from ui.shopping_list_view import ShoppingListView
from ui.recipe_view import RecipeViewDialog
from ui.forms.add_recipe import AddRecipeDialog
from services.seasonal_checker import get_current_season_name
from import_export.json_handler import import_recipes, export_recipes
from database import db_manager
from config import STYLES_DIR, APP_NAME, APP_VERSION, BACKUP_DIR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self._load_styles()
        self._build_ui()
        self._build_menu()
        self._update_status_bar()

    def _load_styles(self):
        qss_path = os.path.join(STYLES_DIR, 'main.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App title
        title_label = QLabel(f"Recettor")
        title_label.setObjectName("app-title")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(70)
        sidebar_layout.addWidget(title_label)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("Rechercher", 0),
            ("Saisonnalite", 1),
            ("Mon Frigo", 2),
            ("🛒 Liste de courses", 3),
            ("Ajouter", -1),
            ("Importer/Exporter", -2),
            ("★ Favoris", -3),
        ]

        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(index >= 0)
            btn.setFixedHeight(50)
            if index >= 0:
                btn.clicked.connect(lambda checked, i=index: self._switch_panel(i))
                self.nav_buttons.append((btn, index))
            elif index == -1:
                btn.setCheckable(False)
                btn.clicked.connect(self._open_add_recipe)
            elif index == -2:
                btn.setCheckable(False)
                btn.clicked.connect(self._show_import_export_menu)
            elif index == -3:
                btn.setCheckable(False)
                btn.clicked.connect(self._open_favorites)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Version label
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #8B6555; padding: 10px;")
        sidebar_layout.addWidget(version_label)

        layout.addWidget(sidebar)

        # Main content area
        self.stack = QStackedWidget()
        self.search_panel = SearchPanel()
        self.search_panel.recipe_selected.connect(self._open_recipe_view)
        self.seasonal_view = SeasonalView()
        self.seasonal_view.recipe_selected.connect(self._open_recipe_view)

        self.fridge_view = FridgeView()
        self.fridge_view.recipe_selected.connect(self._open_recipe_view)

        self.shopping_list_view = ShoppingListView()

        self.stack.addWidget(self.search_panel)        # index 0
        self.stack.addWidget(self.seasonal_view)       # index 1
        self.stack.addWidget(self.fridge_view)         # index 2
        self.stack.addWidget(self.shopping_list_view)  # index 3

        layout.addWidget(self.stack)

        # Set initial active button
        self._switch_panel(0)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _build_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Fichier")
        backup_action = QAction("Sauvegarder la base", self)
        backup_action.triggered.connect(self._do_backup)
        file_menu.addAction(backup_action)
        file_menu.addSeparator()
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("Outils")
        import_action = QAction("Importer des recettes (JSON)", self)
        import_action.triggered.connect(self._import_recipes)
        tools_menu.addAction(import_action)

        export_action = QAction("Exporter toutes les recettes (JSON)", self)
        export_action.triggered.connect(self._export_all)
        tools_menu.addAction(export_action)

        template_action = QAction("Voir le format d'import", self)
        template_action.triggered.connect(self._show_import_format)
        tools_menu.addAction(template_action)

        help_menu = menubar.addMenu("Aide")
        help_action = QAction("Aide complète", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        about_action = QAction("A propos", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _switch_panel(self, index):
        self.stack.setCurrentIndex(index)
        for btn, btn_index in self.nav_buttons:
            btn.setChecked(btn_index == index)
        if index == 3:
            self.shopping_list_view.refresh()

    def _update_status_bar(self):
        now = datetime.now()
        season = get_current_season_name()
        count = db_manager.get_recipe_count()
        self.status_bar.showMessage(
            f"  {now.strftime('%A %d %B %Y')}  |  Saison : {season}  |  {count} recettes  |  {APP_NAME} {APP_VERSION}"
        )

    def _open_recipe_view(self, recipe_id):
        recipe = db_manager.get_recipe_by_id(recipe_id)
        if recipe:
            dialog = RecipeViewDialog(recipe, self)
            dialog.recipe_edited.connect(self._refresh_panels)
            dialog.recipe_deleted.connect(self._refresh_panels)
            dialog.exec_()

    def _open_add_recipe(self):
        dialog = AddRecipeDialog(self)
        if dialog.exec_():
            self._refresh_panels()
            self.status_bar.showMessage("Recette ajoutee avec succes !", 3000)

    def _refresh_panels(self):
        self.search_panel.refresh()
        self.seasonal_view.refresh()
        self.fridge_view.refresh()
        self.shopping_list_view.refresh()
        self._update_status_bar()

    def _show_import_export_menu(self):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("Importer (JSON)", self._import_recipes)
        menu.addAction("Exporter tout (JSON)", self._export_all)
        menu.addAction("Format d'import", self._show_import_format)
        menu.exec_(self.cursor().pos())

    def _import_recipes(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Importer des recettes", "", "JSON (*.json);;Tous (*.*)"
        )
        if not filepath:
            return
        count, errors = import_recipes(filepath)
        if errors:
            error_text = "\n".join(errors[:10])
            if len(errors) > 10:
                error_text += f"\n... et {len(errors)-10} autres erreurs"
            QMessageBox.warning(self, "Import partiel",
                f"{count} recette(s) importee(s).\n\nErreurs :\n{error_text}")
        else:
            QMessageBox.information(self, "Import reussi",
                f"{count} recette(s) importee(s) avec succes !")
        self._refresh_panels()

    def _export_all(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter les recettes", "recettes_export.json", "JSON (*.json)"
        )
        if not filepath:
            return
        try:
            count = export_recipes(filepath)
            QMessageBox.information(self, "Export reussi",
                f"{count} recette(s) exportee(s) vers :\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Echec de l'export : {e}")

    def _show_import_format(self):
        from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton
        import json
        from config import TEMPLATES_DIR
        template_path = os.path.join(TEMPLATES_DIR, 'recipe_template.json')
        dialog = QDialog(self)
        dialog.setWindowTitle("Format d'import JSON")
        dialog.resize(800, 600)
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont("Courier", 11))
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                text.setPlainText(f.read())
        except Exception:
            text.setPlainText("Template non trouve.")
        layout.addWidget(text)
        btn = QPushButton("Fermer")
        btn.clicked.connect(dialog.close)
        layout.addWidget(btn)
        dialog.exec_()

    def _do_backup(self):
        try:
            path = db_manager.backup_database()
            QMessageBox.information(self, "Sauvegarde", f"Sauvegarde creee :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Echec de la sauvegarde : {e}")

    def _open_favorites(self):
        from ui.favorites_panel import ManageFavoritesDialog
        dialog = ManageFavoritesDialog(self)
        dialog.exec_()
        self._refresh_panels()

    def _show_help(self):
        from ui.help_dialog import HelpDialog
        dialog = HelpDialog(self)
        dialog.exec_()

    def _show_about(self):
        QMessageBox.about(self, f"A propos de {APP_NAME}",
            f"<h2>{APP_NAME} {APP_VERSION}</h2>"
            "<p>Application de gestion de recettes de cuisine.</p>"
            "<p>Fonctionnalites :</p>"
            "<ul>"
            "<li>Recherche par ingredient (floue)</li>"
            "<li>Fiches recettes completes</li>"
            "<li>Vue saisonniere</li>"
            "<li>Import/Export JSON</li>"
            "<li>Base de donnees locale SQLite</li>"
            "</ul>"
        )
