import os
import json
import math
from database import db_manager
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QScrollArea, QTableWidget, QTableWidgetItem,
    QGroupBox, QGridLayout, QTextEdit, QHeaderView, QMessageBox,
    QFrame, QSpinBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QPen, QBrush, QPainterPath


class MacroPieChart(QWidget):
    """Widget dessinant un camembert des macronutriments."""

    COLORS = [
        QColor("#3498DB"),   # Glucides - bleu
        QColor("#E74C3C"),   # Protéines - rouge
        QColor("#F39C12"),   # Lipides - orange
    ]

    def __init__(self, carbs, proteins, fats, parent=None):
        super().__init__(parent)
        self.carbs = carbs
        self.proteins = proteins
        self.fats = fats
        self.setMinimumSize(260, 260)
        self.setMaximumSize(300, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        total = self.carbs + self.proteins + self.fats
        if total == 0:
            painter.drawText(self.rect(), Qt.AlignCenter, "Données\nnon renseignées")
            return

        values = [self.carbs, self.proteins, self.fats]
        size = min(self.width(), self.height()) - 20
        x = (self.width() - size) // 2
        y = (self.height() - size) // 2
        rect = QRectF(x, y, size, size)

        start_angle = 90 * 16  # départ à 12h en unités Qt (1/16 de degré)
        for i, val in enumerate(values):
            if val <= 0:
                continue
            span = int(round((val / total) * 360 * 16))
            painter.setBrush(QBrush(self.COLORS[i]))
            painter.setPen(QPen(Qt.white, 2))
            painter.drawPie(rect, start_angle, span)
            start_angle += span

        # Cercle central blanc (effet donut)
        inner = size * 0.38
        cx = x + size / 2
        cy = y + size / 2
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(cx - inner / 2, cy - inner / 2, inner, inner))

        # Texte central
        painter.setPen(QColor("#2C1810"))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.drawText(QRectF(cx - inner/2, cy - inner/2, inner, inner),
                         Qt.AlignCenter, "Macro\nnutriments")

from config import MONTH_NAMES


def make_section(title):
    label = QLabel(title)
    label.setFont(QFont("Arial", 13, QFont.Bold))
    label.setStyleSheet("color: #C0392B; margin-top: 8px; margin-bottom: 4px;")
    return label


def make_badge(text, color="#D4A574", text_color="#2C1810"):
    label = QLabel(text)
    label.setStyleSheet(f"""
        background-color: {color};
        color: {text_color};
        border-radius: 10px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: bold;
    """)
    label.setAlignment(Qt.AlignCenter)
    return label


class RecipeViewDialog(QDialog):
    recipe_edited = pyqtSignal()
    recipe_deleted = pyqtSignal()

    def __init__(self, recipe, parent=None):
        super().__init__(parent)
        self.recipe = recipe
        self.setWindowTitle(f"{recipe['name']}")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #2C1810;")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel(self.recipe['name'])
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        is_fav = db_manager.is_favorite_recipe(self.recipe['id'])
        self._fav_btn = QPushButton("★ Favori" if is_fav else "☆ Favori")
        self._fav_btn.setMinimumWidth(100)
        self._fav_btn.setStyleSheet(self._fav_style(is_fav))
        self._fav_btn.clicked.connect(self._toggle_favorite)

        edit_btn = QPushButton("Modifier")
        edit_btn.setStyleSheet("background-color: #D4A574; color: #2C1810; font-weight: bold; padding: 8px 16px;")
        edit_btn.clicked.connect(self._edit)

        delete_btn = QPushButton("Supprimer")
        delete_btn.setObjectName("danger-btn")
        delete_btn.clicked.connect(self._delete)

        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("background-color: #555; color: white; padding: 8px 16px;")
        close_btn.clicked.connect(self.close)

        for btn in [self._fav_btn, edit_btn, delete_btn, close_btn]:
            header_layout.addWidget(btn)

        layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        tabs.addTab(self._build_presentation_tab(), "Presentation")
        tabs.addTab(self._build_ingredients_tab(), "Ingredients")
        tabs.addTab(self._build_steps_tab(), "Etapes")
        tabs.addTab(self._build_info_tab(), "Informations")
        tabs.addTab(self._build_nutrition_tab(), "Nutrition")
        tabs.addTab(self._build_tips_tab(), "Conseils")

        layout.addWidget(tabs)

    def _scrollable(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return scroll

    def _build_presentation_tab(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Left: image
        left = QVBoxLayout()
        img_label = QLabel()
        img_label.setFixedSize(280, 210)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("background-color: #F0E8D8; border-radius: 12px; border: 2px solid #D4A574;")
        img_path = self.recipe.get('image_path', '')
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(280, 210, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            img_label.setPixmap(pix)
        else:
            img_label.setText("[ Photo ]")
            img_label.setFont(QFont("Arial", 18))
        left.addWidget(img_label)

        # Quick info card
        info_box = QGroupBox("Infos rapides")
        info_grid = QGridLayout(info_box)

        def add_info(row, icon, label, value):
            if value:
                info_grid.addWidget(QLabel(f"{icon} {label}:"), row, 0)
                v = QLabel(str(value))
                v.setFont(QFont("Arial", 11, QFont.Bold))
                info_grid.addWidget(v, row, 1)

        prep = self.recipe.get('prep_time', 0) or 0
        cook = self.recipe.get('cook_time', 0) or 0
        rest = self.recipe.get('rest_time', 0) or 0
        total = prep + cook + rest

        add_info(0, "Prep.", "Preparation", f"{prep} min" if prep else "")
        add_info(1, "Cuiss.", "Cuisson", f"{cook} min" if cook else "")
        add_info(2, "Repos", "Repos", f"{rest} min" if rest else "")
        add_info(3, "Total", "Total", f"{total} min" if total else "")
        add_info(4, "Pers.", "Portions", self.recipe.get('servings', ''))
        add_info(5, "Cout", "Cout", self.recipe.get('estimated_cost') or "")
        add_info(6, "Saison", "Saison", self.recipe.get('ideal_season') or "")

        rating = self.recipe.get('rating', 0) or 0
        if rating > 0:
            add_info(7, "Note", "Note", f"{rating}/5")

        left.addWidget(info_box)
        left.addStretch()
        layout.addLayout(left)

        # Right: details
        right_widget = QWidget()
        right = QVBoxLayout(right_widget)
        right.setSpacing(10)

        # Badges
        badges_row = QHBoxLayout()
        for text, color, text_color in [
            (self.recipe.get('dish_type') or '', '#D4A574', '#2C1810'),
            (self.recipe.get('difficulty') or '',
             '#27AE60' if self.recipe.get('difficulty') == 'Facile' else '#E67E22' if self.recipe.get('difficulty') == 'Intermediaire' else '#E74C3C',
             'white'),
            (self.recipe.get('cuisine_type') or '', '#3498DB', 'white'),
            (self.recipe.get('diet') or '', '#9B59B6', 'white'),
        ]:
            if text:
                badges_row.addWidget(make_badge(text, color, text_color))
        badges_row.addStretch()
        right.addLayout(badges_row)

        # Description
        if self.recipe.get('description'):
            right.addWidget(make_section("Description"))
            desc = QLabel(self.recipe['description'])
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 14px; line-height: 1.5;")
            right.addWidget(desc)

        # History/Origin
        for field, label in [
            ('history', 'Histoire / Origine'),
            ('author', 'Auteur / Chef'),
            ('source', 'Source'),
            ('region', 'Region'),
            ('occasion', 'Occasion'),
        ]:
            val = self.recipe.get(field, '')
            if val:
                right.addWidget(make_section(label))
                lbl = QLabel(val)
                lbl.setWordWrap(True)
                right.addWidget(lbl)

        # Category/Tags
        tags_raw = self.recipe.get('tags', '[]')
        if isinstance(tags_raw, str):
            try:
                tags = json.loads(tags_raw)
            except Exception:
                tags = []
        else:
            tags = tags_raw or []

        if tags:
            right.addWidget(make_section("Tags"))
            tags_row = QHBoxLayout()
            for tag in tags:
                t = make_badge(f"#{tag}", "#ECF0F1", "#2C1810")
                tags_row.addWidget(t)
            tags_row.addStretch()
            right.addLayout(tags_row)

        # Notes
        if self.recipe.get('notes'):
            right.addWidget(make_section("Notes personnelles"))
            notes = QTextEdit()
            notes.setPlainText(self.recipe['notes'])
            notes.setReadOnly(True)
            notes.setMaximumHeight(80)
            right.addWidget(notes)

        right.addStretch()
        layout.addWidget(right_widget, stretch=1)

        return container

    def _build_ingredients_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)

        ings = self.recipe.get('ingredients', [])
        if not ings:
            layout.addWidget(QLabel("Aucun ingredient renseigne."))
            return container

        # Servings info
        mult_row = QHBoxLayout()
        mult_row.addWidget(QLabel(f"Recette pour {self.recipe.get('servings', 4)} personnes"))
        mult_row.addStretch()
        layout.addLayout(mult_row)

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Ingredient", "Quantite", "Unite", "Preparation", "Optionnel", "Remplacement", "Qualite"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(ings))

        for row, ing in enumerate(ings):
            name = ing.get('ingredient_name', '')
            qty = ing.get('quantity', 0)

            table.setItem(row, 0, QTableWidgetItem(name.capitalize()))
            table.setItem(row, 1, QTableWidgetItem(str(qty) if qty else ''))
            table.setItem(row, 2, QTableWidgetItem(ing.get('unit', '')))
            table.setItem(row, 3, QTableWidgetItem(ing.get('preparation', '')))

            opt_item = QTableWidgetItem("Optionnel" if ing.get('optional') else "")
            if ing.get('optional'):
                opt_item.setForeground(QColor("#8B6555"))
            table.setItem(row, 4, opt_item)

            table.setItem(row, 5, QTableWidgetItem(ing.get('replacement', '')))
            table.setItem(row, 6, QTableWidgetItem(ing.get('quality', '')))

        layout.addWidget(table)
        return container

    def _build_steps_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        steps = self.recipe.get('steps', [])
        if not steps:
            layout.addWidget(QLabel("Aucune etape renseignee."))
            return container

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)

        for step in steps:
            step_frame = QFrame()
            step_frame.setFrameShape(QFrame.StyledPanel)
            step_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #E8D5C0;
                    padding: 5px;
                }
            """)
            step_layout = QVBoxLayout(step_frame)
            step_layout.setSpacing(5)

            # Step header
            header_row = QHBoxLayout()
            num = step.get('step_number', 1)
            num_badge = QLabel(f"Etape {num}")
            num_badge.setStyleSheet("""
                background-color: #C0392B;
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 13px;
            """)
            header_row.addWidget(num_badge)

            if step.get('technique'):
                tech = make_badge(step['technique'], "#ECF0F1", "#2C1810")
                header_row.addWidget(tech)

            if step.get('duration'):
                dur = QLabel(f"{step['duration']} min")
                dur.setStyleSheet("color: #8B6555;")
                header_row.addWidget(dur)

            if step.get('temperature') and step['temperature'] > 0:
                temp = QLabel(f"{step['temperature']}°C")
                temp.setStyleSheet("color: #E74C3C;")
                header_row.addWidget(temp)

            header_row.addStretch()
            step_layout.addLayout(header_row)

            # Description
            desc = QLabel(step.get('description', ''))
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 13px; padding: 5px; line-height: 1.5;")
            step_layout.addWidget(desc)

            scroll_layout.addWidget(step_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return container

    def _build_info_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        group_style = (
            "QGroupBox { border: 2px solid #D4A574; border-radius: 10px; "
            "margin-top: 32px; padding: 16px 12px 12px 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; "
            "left: 12px; top: 6px; background: white; padding: 2px 8px; "
            "color: #2C1810; font-weight: bold; font-size: 13px; }"
        )

        # Equipment
        equipment = self.recipe.get('equipment', [])
        if equipment:
            eq_group = QGroupBox("Equipement necessaire")
            eq_group.setStyleSheet(group_style)
            eq_layout = QHBoxLayout(eq_group)
            eq_layout.setContentsMargins(10, 10, 10, 10)
            for eq in equipment:
                tag = make_badge(eq, "#ECF0F1", "#2C1810")
                eq_layout.addWidget(tag)
            eq_layout.addStretch()
            layout.addWidget(eq_group)

        # Allergens
        allergens = self.recipe.get('allergens', [])
        al_group = QGroupBox("Allergenes")
        al_group.setStyleSheet(group_style)
        al_layout = QHBoxLayout(al_group)
        al_layout.setContentsMargins(10, 10, 10, 10)
        if allergens:
            for al in allergens:
                tag = make_badge(al, "#FADBD8", "#C0392B")
                al_layout.addWidget(tag)
        else:
            al_layout.addWidget(QLabel("Aucun allergene renseigne"))
        al_layout.addStretch()
        layout.addWidget(al_group)

        # Cooking parameters
        cook_group = QGroupBox("Parametres de cuisson")
        cook_group.setStyleSheet(group_style)
        cook_grid = QGridLayout(cook_group)
        cook_grid.setContentsMargins(10, 10, 10, 10)
        cook_grid.setVerticalSpacing(8)
        row = 0
        for label, key, fmt in [
            ("Type de cuisson", "cooking_type", "{}"),
            ("Temperature du four", "oven_temperature", "{}°C"),
            ("Puissance du feu", "fire_power", "{}"),
        ]:
            val = self.recipe.get(key)
            if val and val != 0:
                cook_grid.addWidget(QLabel(label + " :"), row, 0)
                cook_grid.addWidget(QLabel(fmt.format(val)), row, 1)
                row += 1
        if row == 0:
            cook_grid.addWidget(QLabel("Aucun parametre renseigne."), 0, 0)
        layout.addWidget(cook_group)

        # Conservation
        cons_group = QGroupBox("Conservation")
        cons_group.setStyleSheet(group_style)
        cons_grid = QGridLayout(cons_group)
        cons_grid.setContentsMargins(10, 10, 10, 10)
        cons_grid.setVerticalSpacing(8)
        row = 0
        for label, key in [
            ("Refrigerateur", "fridge_duration"),
            ("Congelateur", "freezer_duration"),
            ("Rechauffage", "reheating_method"),
            ("Stockage", "storage_method"),
        ]:
            val = self.recipe.get(key)
            if val:
                cons_grid.addWidget(QLabel(label + " :"), row, 0)
                cons_grid.addWidget(QLabel(str(val)), row, 1)
                row += 1
        if row == 0:
            cons_grid.addWidget(QLabel("Aucune info de conservation renseignee."), 0, 0)
        layout.addWidget(cons_group)

        # Advanced sensory
        adv_group = QGroupBox("Profil sensoriel")
        adv_group.setStyleSheet(group_style)
        adv_grid = QGridLayout(adv_group)
        adv_grid.setContentsMargins(10, 10, 10, 10)
        adv_grid.setVerticalSpacing(8)
        row = 0
        for label, key in [
            ("Profil aromatique", "aromatic_profile"),
            ("Intensite du gout", "taste_intensity"),
            ("Texture", "texture"),
            ("Indice glycemique", "glycemic_index"),
        ]:
            val = self.recipe.get(key)
            if val:
                adv_grid.addWidget(QLabel(label + " :"), row, 0)
                adv_grid.addWidget(QLabel(str(val)), row, 1)
                row += 1
        if row == 0:
            adv_grid.addWidget(QLabel("Aucune info sensorielle renseignee."), 0, 0)
        layout.addWidget(adv_group)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _build_nutrition_tab(self):
        # Conteneur principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        servings           = int(self.recipe.get('servings', 4) or 4)
        carbs              = float(self.recipe.get('carbs', 0) or 0)
        proteins           = float(self.recipe.get('proteins', 0) or 0)
        fats               = float(self.recipe.get('fats', 0) or 0)
        calories_per_serv  = float(self.recipe.get('calories_per_serving', 0) or 0)
        total_macro        = carbs + proteins + fats
        ingredients        = self.recipe.get('ingredients', [])

        # ── 1. MACRONUTRIMENTS ────────────────────────────────────────
        macro_group = QGroupBox("Macronutriments par portion")
        macro_group.setFont(QFont("Arial", 14, QFont.Bold))
        macro_group.setStyleSheet(
            "QGroupBox { border: 2px solid #3498DB; border-radius: 10px; "
            "margin-top: 32px; padding: 16px 12px 12px 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; "
            "top: 6px; background: white; padding: 2px 8px; color: #2980B9; }"
        )
        macro_row = QHBoxLayout(macro_group)
        macro_row.setSpacing(30)
        macro_row.setContentsMargins(10, 10, 10, 10)

        # Camembert
        chart = MacroPieChart(carbs, proteins, fats)
        chart.setMinimumSize(240, 240)
        chart.setMaximumSize(280, 280)
        macro_row.addWidget(chart, 0)

        # Légende
        legend_widget = QWidget()
        legend_vbox = QVBoxLayout(legend_widget)
        legend_vbox.setSpacing(16)
        legend_vbox.setContentsMargins(0, 10, 0, 10)

        if total_macro > 0:
            kcal_macro = carbs * 4 + proteins * 4 + fats * 9
            kcal_lbl = QLabel(f"Total : {total_macro:.1f} g  —  {kcal_macro:.0f} kcal")
            kcal_lbl.setStyleSheet("color: #7F8C8D;")
            kcal_lbl.setFont(QFont("Arial", 12))
            legend_vbox.addWidget(kcal_lbl)

        macro_items = [
            ("Glucides",  carbs,    "#3498DB"),
            ("Protéines", proteins, "#E74C3C"),
            ("Lipides",   fats,     "#F39C12"),
        ]
        for m_name, m_val, m_color in macro_items:
            pct = (m_val / total_macro * 100) if total_macro > 0 else 0

            item_w = QWidget()
            item_w.setStyleSheet(
                f"background-color: white; border-left: 6px solid {m_color}; "
                "border-radius: 6px; padding: 4px 10px;"
            )
            item_h = QHBoxLayout(item_w)
            item_h.setContentsMargins(8, 6, 8, 6)
            item_h.setSpacing(16)

            n_lbl = QLabel(m_name)
            n_lbl.setFont(QFont("Arial", 14, QFont.Bold))
            n_lbl.setMinimumWidth(100)
            item_h.addWidget(n_lbl)

            v_lbl = QLabel(f"{m_val:.1f} g")
            v_lbl.setFont(QFont("Arial", 14))
            v_lbl.setMinimumWidth(70)
            item_h.addWidget(v_lbl)

            p_lbl = QLabel(f"{pct:.0f} %")
            p_lbl.setFont(QFont("Arial", 14, QFont.Bold))
            p_lbl.setStyleSheet(f"color: {m_color};")
            p_lbl.setMinimumWidth(55)
            item_h.addWidget(p_lbl)

            # Barre dessinée proprement via stylesheet gradient
            bar_lbl = QLabel()
            bar_lbl.setFixedHeight(16)
            bar_lbl.setMinimumWidth(160)
            fill = max(1, int(pct))
            bar_lbl.setStyleSheet(
                f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                f"stop:0 {m_color}, stop:{fill/100:.3f} {m_color}, "
                f"stop:{min(fill/100+0.001, 1):.3f} #ECF0F1, stop:1 #ECF0F1); "
                "border-radius: 8px;"
            )
            item_h.addWidget(bar_lbl, 1)

            legend_vbox.addWidget(item_w)

        legend_vbox.addStretch()
        macro_row.addWidget(legend_widget, 1)
        layout.addWidget(macro_group)

        # ── 2. CALCULATEUR CALORIQUE ──────────────────────────────────
        calc_group = QGroupBox("Calculateur : quelle portion pour mon objectif calorique ?")
        calc_group.setFont(QFont("Arial", 14, QFont.Bold))
        calc_group.setStyleSheet(
            "QGroupBox { border: 2px solid #27AE60; border-radius: 10px; "
            "margin-top: 32px; padding: 16px 12px 12px 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; "
            "top: 6px; background: white; padding: 2px 8px; color: #1E8449; }"
        )
        calc_vbox = QVBoxLayout(calc_group)
        calc_vbox.setSpacing(14)
        calc_vbox.setContentsMargins(12, 12, 12, 12)

        # Saisie cible
        input_row = QHBoxLayout()
        input_row.setSpacing(12)
        lbl_obj = QLabel("Objectif calorique :")
        lbl_obj.setFont(QFont("Arial", 14))
        input_row.addWidget(lbl_obj)

        target_spin = QSpinBox()
        target_spin.setRange(50, 9999)
        target_spin.setValue(400)
        target_spin.setSuffix(" kcal")
        target_spin.setFont(QFont("Arial", 15, QFont.Bold))
        target_spin.setFixedWidth(160)
        target_spin.setMinimumHeight(40)
        input_row.addWidget(target_spin)

        calc_btn = QPushButton("  Calculer  ")
        calc_btn.setFont(QFont("Arial", 14, QFont.Bold))
        calc_btn.setMinimumHeight(40)
        calc_btn.setStyleSheet(
            "QPushButton { background-color: #27AE60; color: white; "
            "border-radius: 8px; padding: 6px 20px; }"
            "QPushButton:hover { background-color: #1E8449; }"
        )
        input_row.addWidget(calc_btn)
        input_row.addStretch()
        calc_vbox.addLayout(input_row)

        if calories_per_serv > 0:
            hint = QLabel(
                f"Cette recette contient {calories_per_serv:.0f} kcal / portion  "
                f"(recette pour {servings} personnes)"
            )
        else:
            hint = QLabel("Les calories par portion ne sont pas renseignées dans cette recette.")
            hint.setStyleSheet("color: #E74C3C;")
        hint.setFont(QFont("Arial", 12))
        hint.setStyleSheet("color: #7F8C8D;")
        calc_vbox.addWidget(hint)

        # Résultats (masqués au départ)
        result_widget = QWidget()
        result_widget.setStyleSheet(
            "background-color: #F0FFF4; border: 1px solid #A9DFBF; border-radius: 10px;"
        )
        result_widget.setVisible(False)
        res_vbox = QVBoxLayout(result_widget)
        res_vbox.setContentsMargins(16, 14, 16, 14)
        res_vbox.setSpacing(10)

        res_main = QLabel()
        res_main.setFont(QFont("Arial", 16, QFont.Bold))
        res_main.setStyleSheet("color: #1E8449;")
        res_main.setWordWrap(True)
        res_vbox.addWidget(res_main)

        res_weight = QLabel()
        res_weight.setFont(QFont("Arial", 14))
        res_weight.setWordWrap(True)
        res_vbox.addWidget(res_weight)

        res_macros = QLabel()
        res_macros.setFont(QFont("Arial", 13))
        res_macros.setStyleSheet("color: #555;")
        res_macros.setWordWrap(True)
        res_vbox.addWidget(res_macros)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #A9DFBF;")
        res_vbox.addWidget(sep)

        res_ing_lbl = QLabel("Quantités d'ingrédients pour cet objectif :")
        res_ing_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        res_vbox.addWidget(res_ing_lbl)

        res_table = QTableWidget()
        res_table.setColumnCount(3)
        res_table.setHorizontalHeaderLabels(["Ingrédient", "Quantité", "Unité"])
        res_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        res_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        res_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        res_table.setEditTriggers(QTableWidget.NoEditTriggers)
        res_table.verticalHeader().setVisible(False)
        res_table.setAlternatingRowColors(True)
        res_table.setMinimumHeight(120)
        res_vbox.addWidget(res_table)

        calc_vbox.addWidget(result_widget)

        # Logique calcul
        def _estimate_g_per_serving():
            UNIT_G = {
                'g': 1, 'kg': 1000,
                'ml': 1, 'cl': 10, 'l': 1000,
                'cuillère à café': 5, 'cuillère à soupe': 15,
                'tasse': 240, 'verre': 200,
                'pincée': 1, 'filet': 5,
            }
            total = sum(
                float(i.get('quantity') or 0) * UNIT_G[i.get('unit', '').lower().strip()]
                for i in ingredients
                if i.get('unit', '').lower().strip() in UNIT_G and float(i.get('quantity') or 0) > 0
            )
            return (total / servings) if total > 0 else None

        def _fmt(qty, unit):
            if qty <= 0:
                return '—', unit
            if unit == 'g' and qty >= 1000:
                return f"{qty/1000:.2g}", 'kg'
            if unit == 'ml' and qty >= 1000:
                return f"{qty/1000:.2g}", 'l'
            if unit == 'ml' and qty >= 100:
                return f"{qty/100:.2g}", 'cl'
            if qty == int(qty):
                return str(int(qty)), unit
            return f"{qty:.1f}", unit

        def _do_calc():
            if calories_per_serv <= 0:
                res_main.setText("Calories par portion non renseignées — calcul impossible.")
                res_main.setStyleSheet("color: #E74C3C;")
                res_weight.setText("")
                res_macros.setText("")
                res_ing_lbl.setVisible(False)
                res_table.setVisible(False)
                result_widget.setVisible(True)
                return

            target = target_spin.value()
            ratio = target / calories_per_serv

            pct = ratio * 100
            pct_str = f"{pct:.0f}"
            res_main.setStyleSheet("color: #1E8449;")
            res_main.setText(
                f"Pour {target} kcal  →  {pct_str}% d'une portion individuelle"
                f"  ({calories_per_serv:.0f} kcal × {pct_str}% = {target} kcal)"
            )

            g = _estimate_g_per_serving()
            if g:
                res_weight.setText(
                    f"Poids estimé dans l'assiette : {g * ratio:.0f} g"
                    f"  (base : {g:.0f} g / portion)"
                )
            else:
                res_weight.setText(
                    "Poids estimé : non calculable (certaines unités ne sont pas en g/ml)"
                )

            c2 = carbs * ratio
            p2 = proteins * ratio
            f2 = fats * ratio
            res_macros.setText(
                f"Glucides : {c2:.1f} g   |   Protéines : {p2:.1f} g   |   Lipides : {f2:.1f} g"
            )

            ings = [i for i in ingredients if i.get('ingredient_name')]
            res_table.setRowCount(len(ings))
            for r, ing in enumerate(ings):
                qty_adj = float(ing.get('quantity') or 0) * ratio
                q_str, u_str = _fmt(qty_adj, ing.get('unit') or '')

                res_table.setItem(r, 0, QTableWidgetItem(ing.get('ingredient_name', '').capitalize()))
                qty_item = QTableWidgetItem(q_str)
                qty_item.setFont(QFont("Arial", 13, QFont.Bold))
                qty_item.setForeground(QColor("#1E8449"))
                qty_item.setTextAlignment(Qt.AlignCenter)
                res_table.setItem(r, 1, qty_item)
                res_table.setItem(r, 2, QTableWidgetItem(u_str))

            res_table.setMaximumHeight(len(ings) * 36 + 36)
            res_ing_lbl.setVisible(True)
            res_table.setVisible(True)
            result_widget.setVisible(True)

        calc_btn.clicked.connect(_do_calc)
        layout.addWidget(calc_group)

        # Déclencher le calcul initial avec la valeur par défaut (400 kcal)
        if calories_per_serv > 0:
            _do_calc()

        # ── 3. TABLEAU DÉTAILLÉ ───────────────────────────────────────
        detail_group = QGroupBox(f"Valeurs nutritionnelles complètes  (par portion — {servings} pers.)")
        detail_group.setFont(QFont("Arial", 13, QFont.Bold))
        detail_group.setStyleSheet(
            "QGroupBox { border: 2px solid #E8D5C0; border-radius: 10px; "
            "margin-top: 32px; padding: 16px 12px 12px 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; "
            "top: 6px; background: white; padding: 2px 8px; color: #2C1810; }"
        )
        detail_vbox = QVBoxLayout(detail_group)

        nutrients = [
            ("Calories",  "calories_per_serving", "kcal"),
            ("Glucides",  "carbs",                "g"),
            ("Protéines", "proteins",             "g"),
            ("Lipides",   "fats",                 "g"),
            ("Fibres",    "fiber",                "g"),
            ("Sucre",     "sugar",                "g"),
            ("Sel",       "salt",                 "g"),
        ]
        rows = [(lbl, f"{self.recipe.get(k, 0) or 0} {u}")
                for lbl, k, u in nutrients if (self.recipe.get(k, 0) or 0) > 0]

        if rows:
            tbl = QTableWidget(len(rows), 2)
            tbl.setHorizontalHeaderLabels(["Nutriment", "Par portion"])
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tbl.setEditTriggers(QTableWidget.NoEditTriggers)
            tbl.verticalHeader().setVisible(False)
            tbl.setAlternatingRowColors(True)
            tbl.setMaximumHeight(len(rows) * 36 + 36)
            for i, (lbl, val) in enumerate(rows):
                tbl.setItem(i, 0, QTableWidgetItem(lbl))
                v_item = QTableWidgetItem(val)
                v_item.setFont(QFont("Arial", 13, QFont.Bold))
                tbl.setItem(i, 1, v_item)
            detail_vbox.addWidget(tbl)
        else:
            detail_vbox.addWidget(QLabel("Aucune valeur nutritionnelle renseignée."))

        for lbl, key in [("Vitamines", "vitamins"), ("Minéraux", "minerals")]:
            v = self.recipe.get(key, '')
            if v:
                detail_vbox.addWidget(make_section(lbl))
                detail_vbox.addWidget(QLabel(v))

        layout.addWidget(detail_group)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _build_tips_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)

        tips = self.recipe.get('tips', [])
        grouped = {}
        for tip in tips:
            t = tip.get('tip_type', 'autres')
            grouped.setdefault(t, []).append(tip.get('content', ''))

        type_config = {
            'astuces': ("Astuces du chef", "#FFF9C4", "#F39C12"),
            'erreurs': ("Erreurs a eviter", "#FADBD8", "#E74C3C"),
            'variantes': ("Variantes", "#D5F5E3", "#27AE60"),
            'accompagnements': ("Accompagnements", "#EBF5FB", "#3498DB"),
            'accords': ("Accords mets & boissons", "#F5EEF8", "#8E44AD"),
        }

        has_content = False
        for tip_type, (title, bg, color) in type_config.items():
            items = grouped.get(tip_type, [])
            if items:
                has_content = True
                group = QGroupBox(title)
                group.setStyleSheet(f"""
                    QGroupBox {{
                        background-color: {bg};
                        border: 2px solid {color};
                        border-radius: 8px;
                    }}
                    QGroupBox::title {{
                        color: {color};
                        font-weight: bold;
                        font-size: 13px;
                    }}
                """)
                g_layout = QVBoxLayout(group)
                for item in items:
                    item_label = QLabel(f"• {item}")
                    item_label.setWordWrap(True)
                    item_label.setStyleSheet("font-size: 13px;")
                    g_layout.addWidget(item_label)
                scroll_layout.addWidget(group)

        # Presentation/plating
        for field, label, icon in [
            ('plate_type', "Type d'assiette", ''),
            ('food_arrangement', 'Disposition', ''),
            ('decoration', 'Decoration', ''),
            ('garnish', 'Garniture', ''),
        ]:
            val = self.recipe.get(field, '')
            if val:
                has_content = True
                lbl = QLabel(f"<b>{label} :</b> {val}")
                lbl.setWordWrap(True)
                scroll_layout.addWidget(lbl)

        if not has_content:
            scroll_layout.addWidget(QLabel("Aucun conseil ou variante renseigne."))

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return container

    def _fav_style(self, is_fav: bool) -> str:
        if is_fav:
            return (
                "QPushButton { background-color: #F39C12; color: white; "
                "font-weight: bold; padding: 8px 16px; border-radius: 6px; }"
                "QPushButton:hover { background-color: #D68910; }"
            )
        return (
            "QPushButton { background-color: #555; color: #F5F0E8; "
            "padding: 8px 16px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #F39C12; color: white; }"
        )

    def _toggle_favorite(self):
        recipe_id = self.recipe['id']
        if db_manager.is_favorite_recipe(recipe_id):
            db_manager.remove_favorite_recipe(recipe_id)
            self._fav_btn.setText("☆ Favori")
            self._fav_btn.setStyleSheet(self._fav_style(False))
        else:
            db_manager.add_favorite_recipe(recipe_id)
            self._fav_btn.setText("★ Favori")
            self._fav_btn.setStyleSheet(self._fav_style(True))

    def _edit(self):
        from ui.forms.edit_recipe import EditRecipeDialog
        dialog = EditRecipeDialog(self.recipe, self)
        if dialog.exec_():
            from database import db_manager
            self.recipe = db_manager.get_recipe_by_id(self.recipe['id'])
            self.recipe_edited.emit()
            # Rebuild UI
            for i in reversed(range(self.layout().count())):
                widget = self.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            self._build_ui()
            QMessageBox.information(self, "Succes", "Recette modifiee avec succes !")

    def _delete(self):
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Voulez-vous vraiment supprimer la recette\n« {self.recipe['name']} » ?\n\nCette action est irreversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from database import db_manager
            db_manager.delete_recipe(self.recipe['id'])
            self.recipe_deleted.emit()
            self.close()
