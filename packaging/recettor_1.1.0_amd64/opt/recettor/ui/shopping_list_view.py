from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QLineEdit, QCheckBox, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database import db_manager


class _ShoppingItem(QFrame):
    """Ligne d'un article dans la liste de courses."""

    def __init__(self, item: dict, on_toggle, on_delete, parent=None):
        super().__init__(parent)
        self._item_id = item['id']
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self.setFrameShape(QFrame.NoFrame)
        self._build(item)

    def _build(self, item: dict):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self._checkbox = QCheckBox(item['name'].capitalize())
        self._checkbox.setChecked(bool(item['checked']))
        self._checkbox.setFont(QFont("Arial", 13))
        self._apply_style(bool(item['checked']))
        self._checkbox.stateChanged.connect(self._on_check_changed)
        layout.addWidget(self._checkbox, 1)

        del_btn = QPushButton("×")
        del_btn.setFixedSize(26, 26)
        del_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #C0392B; "
            "border: none; font-size: 18px; font-weight: bold; padding: 0; }"
            "QPushButton:hover { color: #922B21; }"
        )
        del_btn.clicked.connect(lambda: self._on_delete(self._item_id))
        layout.addWidget(del_btn)

    def _on_check_changed(self, state):
        checked = bool(state)
        self._apply_style(checked)
        db_manager.toggle_shopping_item(self._item_id)
        self._on_toggle()

    def _apply_style(self, checked: bool):
        if checked:
            self._checkbox.setStyleSheet(
                "QCheckBox { color: #AAAAAA; text-decoration: line-through; }"
                "QCheckBox::indicator { border: 2px solid #AAAAAA; border-radius: 3px; "
                "background-color: #D5E8D4; }"
            )
        else:
            self._checkbox.setStyleSheet(
                "QCheckBox { color: #2C1810; }"
                "QCheckBox::indicator { border: 2px solid #D4A574; border-radius: 3px; "
                "background-color: white; }"
                "QCheckBox::indicator:checked { background-color: #27AE60; "
                "border-color: #27AE60; }"
            )


class ShoppingListView(QWidget):
    """Vue principale de la liste de courses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ── Titre ─────────────────────────────────────────────────────
        title = QLabel("🛒 Liste de courses")
        title.setObjectName("section-title")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel(
            "Ajoutez des articles manuellement ou depuis les suggestions IA — "
            "cochez-les au fur et à mesure de vos achats."
        )
        subtitle.setStyleSheet("color: #8B6555; font-style: italic; font-size: 13px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # ── Input d'ajout ──────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ajouter un article...")
        self._input.setMinimumHeight(42)
        self._input.returnPressed.connect(self._add_item)
        input_row.addWidget(self._input)

        add_btn = QPushButton("+ Ajouter")
        add_btn.setMinimumHeight(42)
        add_btn.setStyleSheet(
            "QPushButton { background-color: #27AE60; color: white; border-radius: 8px; "
            "padding: 6px 20px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1E8449; }"
        )
        add_btn.clicked.connect(self._add_item)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        # ── Compteur ──────────────────────────────────────────────────
        self._count_lbl = QLabel("Liste vide")
        self._count_lbl.setStyleSheet(
            "color: #1B5E20; font-weight: bold; font-size: 14px;"
        )
        layout.addWidget(self._count_lbl)

        # ── Zone scrollable ───────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: 2px solid #E8D5C0; border-radius: 10px; "
            "background-color: white; }"
        )

        self._items_widget = QWidget()
        self._items_widget.setStyleSheet("background: white;")
        self._items_layout = QVBoxLayout(self._items_widget)
        self._items_layout.setContentsMargins(10, 8, 10, 8)
        self._items_layout.setSpacing(4)
        self._items_layout.setAlignment(Qt.AlignTop)

        self._empty_lbl = QLabel("Aucun article pour l'instant.")
        self._empty_lbl.setStyleSheet(
            "color: #8B6555; font-style: italic; font-size: 13px; padding: 20px;"
        )
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._items_layout.addWidget(self._empty_lbl)

        scroll.setWidget(self._items_widget)
        layout.addWidget(scroll)

        # ── Actions en bas ────────────────────────────────────────────
        actions = QHBoxLayout()
        actions.setSpacing(10)

        clear_checked_btn = QPushButton("Supprimer les cochés")
        clear_checked_btn.setStyleSheet(
            "QPushButton { background-color: #E8D5C0; color: #2C1810; border-radius: 6px; "
            "padding: 6px 16px; font-size: 13px; }"
            "QPushButton:hover { background-color: #D4A574; }"
        )
        clear_checked_btn.clicked.connect(self._clear_checked)
        actions.addWidget(clear_checked_btn)

        clear_all_btn = QPushButton("Tout vider")
        clear_all_btn.setStyleSheet(
            "QPushButton { background-color: #FADBD8; color: #C0392B; border-radius: 6px; "
            "padding: 6px 16px; font-size: 13px; }"
            "QPushButton:hover { background-color: #F1948A; color: white; }"
        )
        clear_all_btn.clicked.connect(self._clear_all)
        actions.addWidget(clear_all_btn)

        actions.addStretch()
        layout.addLayout(actions)

    # ── Chargement / rafraîchissement ─────────────────────────────────

    def _load(self):
        """Recharge la liste depuis la DB et rafraîchit l'affichage."""
        # Supprimer les items existants (sauf empty_lbl)
        while self._items_layout.count():
            item = self._items_layout.takeAt(0)
            if item.widget() and item.widget() is not self._empty_lbl:
                item.widget().deleteLater()

        items = db_manager.get_shopping_list()

        if not items:
            self._items_layout.addWidget(self._empty_lbl)
            self._empty_lbl.show()
            self._count_lbl.setText("Liste vide")
            return

        self._empty_lbl.hide()
        total = len(items)
        checked = sum(1 for i in items if i['checked'])

        for item in items:
            row = _ShoppingItem(item, on_toggle=self._load, on_delete=self._delete_item)
            self._items_layout.addWidget(row)

        if checked == 0:
            self._count_lbl.setText(
                f"{total} article{'s' if total > 1 else ''}"
            )
        else:
            self._count_lbl.setText(
                f"{total} article{'s' if total > 1 else ''}  —  {checked} coché{'s' if checked > 1 else ''}"
            )

    # ── Actions ────────────────────────────────────────────────────────

    def _add_item(self):
        name = self._input.text().strip()
        self._input.clear()
        if not name:
            return
        added = db_manager.add_shopping_item(name)
        if not added:
            self._input.setPlaceholderText(f"« {name} » est déjà dans la liste")
        else:
            self._input.setPlaceholderText("Ajouter un article...")
        self._load()

    def _delete_item(self, item_id: int):
        db_manager.remove_shopping_item(item_id)
        self._load()

    def _clear_checked(self):
        db_manager.clear_checked_items()
        self._load()

    def _clear_all(self):
        reply = QMessageBox.question(
            self, "Vider la liste",
            "Supprimer tous les articles de la liste de courses ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db_manager.clear_shopping_list()
            self._load()

    # ── Interface publique ─────────────────────────────────────────────

    def refresh(self):
        """Appelé depuis l'extérieur quand des articles sont ajoutés."""
        self._load()
