from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QWidget, QFrame, QCompleter,
    QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from database import db_manager


class FavoriteTag(QFrame):
    """A removable tag widget for a favorite ingredient."""
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


class ManageFavoritesDialog(QDialog):
    favorites_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gérer mes ingrédients favoris")
        self.setMinimumSize(560, 480)
        self.resize(600, 520)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("★ Mes ingrédients favoris")
        title.setFont(QFont("Arial", 17, QFont.Bold))
        title.setStyleSheet("color: #E67E22;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Ajoutez vos ingrédients préférés pour les retrouver rapidement "
            "et rechercher des recettes qui les utilisent."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #7F8C8D; font-size: 13px;")
        layout.addWidget(subtitle)

        # Add ingredient row
        add_group_lbl = QLabel("Ajouter un ingrédient favori :")
        add_group_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(add_group_lbl)

        add_row = QHBoxLayout()
        add_row.setSpacing(10)

        self.add_edit = QLineEdit()
        self.add_edit.setPlaceholderText("Tapez un ingrédient (ex: tomate, poulet, basilic...)")
        self.add_edit.setMinimumHeight(38)
        self.add_edit.setFont(QFont("Arial", 13))
        # Autocomplete from known ingredients
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

        # Favorites list
        list_lbl = QLabel("Mes favoris :")
        list_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(list_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(180)
        self.tags_container = QWidget()
        self.tags_layout = QGridLayout(self.tags_container)
        self.tags_layout.setSpacing(10)
        self.tags_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.tags_container)
        layout.addWidget(scroll)

        self.empty_lbl = QLabel("Aucun ingrédient favori pour l'instant.")
        self.empty_lbl.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 13px;")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        clear_btn = QPushButton("Tout supprimer")
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #E74C3C; color: white; border-radius: 6px; padding: 6px 16px; }"
        )
        clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(clear_btn)
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet(
            "QPushButton { background-color: #95A5A6; color: white; border-radius: 6px; padding: 6px 20px; }"
        )
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _refresh(self):
        # Clear tags
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        favorites = db_manager.get_favorite_ingredients()
        self.empty_lbl.setVisible(len(favorites) == 0)

        cols = 3
        for i, name in enumerate(favorites):
            tag = FavoriteTag(name)
            tag.removed.connect(self._remove_ingredient)
            self.tags_layout.addWidget(tag, i // cols, i % cols)

        self.favorites_changed.emit()

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
        self._refresh()

    def _remove_ingredient(self, name):
        db_manager.remove_favorite_ingredient(name)
        self._refresh()

    def _clear_all(self):
        favorites = db_manager.get_favorite_ingredients()
        if not favorites:
            return
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Confirmer",
            "Supprimer tous vos ingrédients favoris ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for name in favorites:
                db_manager.remove_favorite_ingredient(name)
            self._refresh()
