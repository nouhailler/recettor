import os
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QLabel, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QScrollArea, QFrame, QCompleter
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QPixmap, QFont

from database import db_manager
from config import (
    DIFFICULTIES, DISH_TYPES, CATEGORIES, DIETS, SEASONS, ALLERGENS,
    UNITS, COOKING_TYPES, CUISINES, OCCASIONS, TECHNIQUES, EQUIPMENT,
    IMAGES_DIR
)


class AddRecipeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une recette")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        self._image_path = ''
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Nouvelle recette")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2C1810; padding: 10px;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_identification_tab(), "Identification")
        self.tabs.addTab(self._build_time_tab(), "Temps")
        self.tabs.addTab(self._build_ingredients_tab(), "Ingredients")
        self.tabs.addTab(self._build_steps_tab(), "Etapes")
        self.tabs.addTab(self._build_equipment_allergens_tab(), "Equip. & Allergenes")
        self.tabs.addTab(self._build_nutrition_tab(), "Nutrition")
        self.tabs.addTab(self._build_cooking_tab(), "Cuisson & Conservation")
        self.tabs.addTab(self._build_tips_tab(), "Conseils & Tags")
        self.tabs.addTab(self._build_photo_tab(), "Photo")
        layout.addWidget(self.tabs)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary-btn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Enregistrer la recette")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _form_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return scroll

    def _build_identification_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom de la recette (obligatoire)")
        form.addRow("* Nom :", self.name_edit)

        self.other_names_edit = QLineEdit()
        self.other_names_edit.setPlaceholderText("Autres appellations, separees par des virgules")
        form.addRow("Autres noms :", self.other_names_edit)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Courte description de la recette...")
        self.description_edit.setMaximumHeight(80)
        form.addRow("Description :", self.description_edit)

        self.history_edit = QTextEdit()
        self.history_edit.setPlaceholderText("Histoire, anecdote, origine...")
        self.history_edit.setMaximumHeight(80)
        form.addRow("Histoire / Origine :", self.history_edit)

        self.author_edit = QLineEdit()
        form.addRow("Auteur / Chef :", self.author_edit)

        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Livre, site, grand-mere...")
        form.addRow("Source :", self.source_edit)

        self.cuisine_edit = QComboBox()
        self.cuisine_edit.addItem("", "")
        for c in CUISINES:
            self.cuisine_edit.addItem(c, c)
        self.cuisine_edit.setEditable(True)
        form.addRow("Type de cuisine :", self.cuisine_edit)

        self.region_edit = QLineEdit()
        form.addRow("Region :", self.region_edit)

        self.occasion_edit = QComboBox()
        self.occasion_edit.addItem("", "")
        for o in OCCASIONS:
            self.occasion_edit.addItem(o, o)
        self.occasion_edit.setEditable(True)
        form.addRow("Occasion :", self.occasion_edit)

        self.dish_type_edit = QComboBox()
        self.dish_type_edit.addItem("", "")
        for dt in DISH_TYPES:
            self.dish_type_edit.addItem(dt, dt)
        form.addRow("Type de plat :", self.dish_type_edit)

        self.category_edit = QComboBox()
        self.category_edit.addItem("", "")
        for cat in CATEGORIES:
            self.category_edit.addItem(cat, cat)
        self.category_edit.setEditable(True)
        form.addRow("Categorie :", self.category_edit)

        self.diet_edit = QComboBox()
        for d in DIETS:
            self.diet_edit.addItem(d, d)
        form.addRow("Regime alimentaire :", self.diet_edit)

        self.season_edit = QComboBox()
        for s in SEASONS:
            self.season_edit.addItem(s, s)
        form.addRow("Saison ideale :", self.season_edit)

        return self._form_scroll(w)

    def _build_time_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        self.prep_time = QSpinBox()
        self.prep_time.setRange(0, 9999)
        self.prep_time.setSuffix(" min")
        self.prep_time.valueChanged.connect(self._update_total_time)
        form.addRow("Temps de preparation :", self.prep_time)

        self.cook_time = QSpinBox()
        self.cook_time.setRange(0, 9999)
        self.cook_time.setSuffix(" min")
        self.cook_time.valueChanged.connect(self._update_total_time)
        form.addRow("Temps de cuisson :", self.cook_time)

        self.rest_time = QSpinBox()
        self.rest_time.setRange(0, 9999)
        self.rest_time.setSuffix(" min")
        self.rest_time.valueChanged.connect(self._update_total_time)
        form.addRow("Temps de repos :", self.rest_time)

        self.total_time_label = QLabel("0 min")
        self.total_time_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_time_label.setStyleSheet("color: #C0392B;")
        form.addRow("Temps total :", self.total_time_label)

        self.difficulty_edit = QComboBox()
        for d in DIFFICULTIES:
            self.difficulty_edit.addItem(d, d)
        form.addRow("Difficulte :", self.difficulty_edit)

        self.servings_edit = QSpinBox()
        self.servings_edit.setRange(1, 999)
        self.servings_edit.setValue(4)
        self.servings_edit.setSuffix(" personnes")
        form.addRow("Nombre de portions :", self.servings_edit)

        self.cost_edit = QLineEdit()
        self.cost_edit.setPlaceholderText("Ex: euros, euros euros, ou 15 euros")
        form.addRow("Cout estime :", self.cost_edit)

        self.rating_edit = QDoubleSpinBox()
        self.rating_edit.setRange(0, 5)
        self.rating_edit.setSingleStep(0.5)
        self.rating_edit.setSuffix(" / 5")
        form.addRow("Note :", self.rating_edit)

        return self._form_scroll(w)

    def _update_total_time(self):
        total = self.prep_time.value() + self.cook_time.value() + self.rest_time.value()
        h = total // 60
        m = total % 60
        if h > 0:
            self.total_time_label.setText(f"{h}h{m:02d} ({total} min)")
        else:
            self.total_time_label.setText(f"{total} min")

    def _build_ingredients_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 15, 15, 15)

        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("Ajouter un ingredient")
        add_btn.clicked.connect(self._add_ingredient_row)
        remove_btn = QPushButton("Supprimer la selection")
        remove_btn.setObjectName("secondary-btn")
        remove_btn.clicked.connect(self._remove_ingredient_row)
        toolbar.addWidget(add_btn)
        toolbar.addWidget(remove_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(7)
        self.ingredients_table.setHorizontalHeaderLabels([
            "Ingredient *", "Quantite", "Unite", "Preparation", "Optionnel", "Remplacement", "Qualite"
        ])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ingredients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ingredients_table.verticalHeader().setVisible(False)
        layout.addWidget(self.ingredients_table)

        # Add first empty row
        self._add_ingredient_row()
        return w

    def _add_ingredient_row(self):
        row = self.ingredients_table.rowCount()
        self.ingredients_table.insertRow(row)

        # Ingredient name with autocomplete
        name_edit = QLineEdit()
        known = db_manager.get_all_ingredients()
        completer = QCompleter(known)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        name_edit.setCompleter(completer)
        name_edit.setPlaceholderText("Ex: tomate")
        self.ingredients_table.setCellWidget(row, 0, name_edit)

        qty = QDoubleSpinBox()
        qty.setRange(0, 99999)
        qty.setDecimals(1)
        self.ingredients_table.setCellWidget(row, 1, qty)

        unit_combo = QComboBox()
        unit_combo.addItem("")
        for u in UNITS:
            unit_combo.addItem(u)
        unit_combo.setEditable(True)
        self.ingredients_table.setCellWidget(row, 2, unit_combo)

        self.ingredients_table.setItem(row, 3, QTableWidgetItem(""))

        opt_check = QCheckBox()
        opt_widget = QWidget()
        opt_layout = QHBoxLayout(opt_widget)
        opt_layout.setAlignment(Qt.AlignCenter)
        opt_layout.setContentsMargins(0, 0, 0, 0)
        opt_layout.addWidget(opt_check)
        self.ingredients_table.setCellWidget(row, 4, opt_widget)
        opt_widget.setProperty("checkbox", opt_check)

        self.ingredients_table.setItem(row, 5, QTableWidgetItem(""))
        self.ingredients_table.setItem(row, 6, QTableWidgetItem(""))
        self.ingredients_table.setRowHeight(row, 38)

    def _remove_ingredient_row(self):
        rows = set(idx.row() for idx in self.ingredients_table.selectedIndexes())
        for row in sorted(rows, reverse=True):
            self.ingredients_table.removeRow(row)

    def _build_steps_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 15, 15, 15)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("Ajouter une etape")
        add_btn.clicked.connect(self._add_step)
        remove_btn = QPushButton("Supprimer derniere etape")
        remove_btn.setObjectName("secondary-btn")
        remove_btn.clicked.connect(self._remove_last_step)
        toolbar.addWidget(add_btn)
        toolbar.addWidget(remove_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_container)
        self.steps_layout.setSpacing(10)
        self.steps_layout.addStretch()
        scroll.setWidget(self.steps_container)
        layout.addWidget(scroll)

        self._steps = []
        self._add_step()
        return w

    def _add_step(self):
        step_num = len(self._steps) + 1
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #E8D5C0; padding: 5px; }")
        frame_layout = QVBoxLayout(frame)

        header = QHBoxLayout()
        header.addWidget(QLabel(f"Etape {step_num}"))

        dur = QSpinBox()
        dur.setRange(0, 999)
        dur.setSuffix(" min")
        dur.setFixedWidth(100)
        header.addWidget(QLabel("Duree :"))
        header.addWidget(dur)

        temp = QSpinBox()
        temp.setRange(0, 999)
        temp.setSuffix(" C")
        temp.setFixedWidth(100)
        header.addWidget(QLabel("Temp. :"))
        header.addWidget(temp)

        tech = QComboBox()
        tech.addItem("")
        for t in TECHNIQUES:
            tech.addItem(t)
        tech.setEditable(True)
        tech.setFixedWidth(150)
        header.addWidget(QLabel("Technique :"))
        header.addWidget(tech)
        header.addStretch()
        frame_layout.addLayout(header)

        desc = QTextEdit()
        desc.setPlaceholderText(f"Description de l'etape {step_num}...")
        desc.setMinimumHeight(80)
        frame_layout.addWidget(desc)

        # Insert before stretch
        self.steps_layout.insertWidget(self.steps_layout.count() - 1, frame)
        self._steps.append({'frame': frame, 'desc': desc, 'dur': dur, 'temp': temp, 'tech': tech, 'num': step_num})

    def _remove_last_step(self):
        if self._steps:
            step = self._steps.pop()
            step['frame'].deleteLater()

    def _build_equipment_allergens_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Equipment
        eq_group = QGroupBox("Equipement necessaire")
        eq_grid = QGridLayout(eq_group)
        self.equipment_checks = {}
        for i, eq in enumerate(EQUIPMENT):
            cb = QCheckBox(eq)
            eq_grid.addWidget(cb, i // 3, i % 3)
            self.equipment_checks[eq] = cb
        layout.addWidget(eq_group)

        # Other equipment
        other_eq_layout = QHBoxLayout()
        other_eq_layout.addWidget(QLabel("Autre equipement :"))
        self.other_equipment_edit = QLineEdit()
        self.other_equipment_edit.setPlaceholderText("Ex: moule a cake, mandoline... (separes par des virgules)")
        other_eq_layout.addWidget(self.other_equipment_edit)
        layout.addLayout(other_eq_layout)

        # Allergens
        al_group = QGroupBox("Allergenes presents")
        al_grid = QGridLayout(al_group)
        self.allergen_checks = {}
        for i, al in enumerate(ALLERGENS):
            cb = QCheckBox(al)
            al_grid.addWidget(cb, i // 3, i % 3)
            self.allergen_checks[al] = cb
        layout.addWidget(al_group)
        layout.addStretch()
        return w

    def _build_nutrition_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        self.calories_edit = QDoubleSpinBox()
        self.calories_edit.setRange(0, 9999)
        self.calories_edit.setSuffix(" kcal")
        form.addRow("Calories (par portion) :", self.calories_edit)

        self.proteins_edit = QDoubleSpinBox()
        self.proteins_edit.setRange(0, 999)
        self.proteins_edit.setSuffix(" g")
        form.addRow("Proteines :", self.proteins_edit)

        self.carbs_edit = QDoubleSpinBox()
        self.carbs_edit.setRange(0, 999)
        self.carbs_edit.setSuffix(" g")
        form.addRow("Glucides :", self.carbs_edit)

        self.fats_edit = QDoubleSpinBox()
        self.fats_edit.setRange(0, 999)
        self.fats_edit.setSuffix(" g")
        form.addRow("Lipides :", self.fats_edit)

        self.fiber_edit = QDoubleSpinBox()
        self.fiber_edit.setRange(0, 999)
        self.fiber_edit.setSuffix(" g")
        form.addRow("Fibres :", self.fiber_edit)

        self.sugar_edit = QDoubleSpinBox()
        self.sugar_edit.setRange(0, 999)
        self.sugar_edit.setSuffix(" g")
        form.addRow("Sucre :", self.sugar_edit)

        self.salt_edit = QDoubleSpinBox()
        self.salt_edit.setRange(0, 99)
        self.salt_edit.setSuffix(" g")
        form.addRow("Sel :", self.salt_edit)

        self.vitamins_edit = QLineEdit()
        self.vitamins_edit.setPlaceholderText("Ex: Vitamine C, B12...")
        form.addRow("Vitamines :", self.vitamins_edit)

        self.minerals_edit = QLineEdit()
        self.minerals_edit.setPlaceholderText("Ex: Fer, Calcium...")
        form.addRow("Mineraux :", self.minerals_edit)

        return self._form_scroll(w)

    def _build_cooking_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        self.oven_temp_edit = QSpinBox()
        self.oven_temp_edit.setRange(0, 500)
        self.oven_temp_edit.setSuffix(" C")
        form.addRow("Temperature du four :", self.oven_temp_edit)

        self.fire_power_edit = QLineEdit()
        self.fire_power_edit.setPlaceholderText("Ex: feu doux, feu vif, feu moyen")
        form.addRow("Puissance du feu :", self.fire_power_edit)

        self.cooking_type_edit = QComboBox()
        self.cooking_type_edit.addItem("")
        for ct in COOKING_TYPES:
            self.cooking_type_edit.addItem(ct)
        self.cooking_type_edit.setEditable(True)
        form.addRow("Type de cuisson :", self.cooking_type_edit)

        form.addRow(QLabel(""))
        form.addRow(QLabel("Conservation :"))

        self.fridge_dur_edit = QLineEdit()
        self.fridge_dur_edit.setPlaceholderText("Ex: 3 jours, 1 semaine")
        form.addRow("Duree au refrigerateur :", self.fridge_dur_edit)

        self.freezer_dur_edit = QLineEdit()
        self.freezer_dur_edit.setPlaceholderText("Ex: 3 mois")
        form.addRow("Duree au congelateur :", self.freezer_dur_edit)

        self.reheating_edit = QLineEdit()
        self.reheating_edit.setPlaceholderText("Ex: four 180 C 15 min, micro-ondes")
        form.addRow("Methode de rechauffage :", self.reheating_edit)

        self.storage_edit = QLineEdit()
        self.storage_edit.setPlaceholderText("Ex: boite hermetique, film alimentaire")
        form.addRow("Stockage recommande :", self.storage_edit)

        form.addRow(QLabel(""))
        form.addRow(QLabel("Presentation & Dressage :"))

        self.plate_type_edit = QLineEdit()
        self.plate_type_edit.setPlaceholderText("Ex: assiette creuse, planche en bois")
        form.addRow("Type d'assiette :", self.plate_type_edit)

        self.food_arrangement_edit = QLineEdit()
        form.addRow("Disposition des aliments :", self.food_arrangement_edit)

        self.decoration_edit = QLineEdit()
        form.addRow("Decoration :", self.decoration_edit)

        self.garnish_edit = QLineEdit()
        form.addRow("Garniture :", self.garnish_edit)

        return self._form_scroll(w)

    def _build_tips_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        def make_tips_edit(placeholder):
            te = QTextEdit()
            te.setPlaceholderText(placeholder)
            te.setMaximumHeight(80)
            return te

        self.tips_edit = make_tips_edit("Une astuce par ligne...")
        form.addRow("Astuces du chef :", self.tips_edit)

        self.errors_edit = make_tips_edit("Une erreur a eviter par ligne...")
        form.addRow("Erreurs a eviter :", self.errors_edit)

        self.variants_edit = make_tips_edit("Une variante par ligne (vege, express, gastronomique...)")
        form.addRow("Variantes :", self.variants_edit)

        self.accompaniments_edit = make_tips_edit("Un accompagnement par ligne...")
        form.addRow("Accompagnements :", self.accompaniments_edit)

        self.accords_edit = make_tips_edit("Ex: Rose de Provence, biere blonde...")
        form.addRow("Accords mets & boissons :", self.accords_edit)

        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags separes par des virgules (ex: ete, vegetarien, rapide)")
        form.addRow("Tags :", self.tags_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Notes personnelles...")
        form.addRow("Notes :", self.notes_edit)

        self.aromatic_edit = QLineEdit()
        self.aromatic_edit.setPlaceholderText("Ex: Herbace, epice, fume...")
        form.addRow("Profil aromatique :", self.aromatic_edit)

        self.taste_intensity_edit = QLineEdit()
        self.taste_intensity_edit.setPlaceholderText("Ex: Doux, Modere, Intense, Tres releve")
        form.addRow("Intensite du gout :", self.taste_intensity_edit)

        self.texture_edit = QLineEdit()
        self.texture_edit.setPlaceholderText("Ex: Croquant, Cremeux, Fondant, Moelleux")
        form.addRow("Texture :", self.texture_edit)

        self.glycemic_edit = QLineEdit()
        self.glycemic_edit.setPlaceholderText("Ex: Bas, Moyen, Eleve")
        form.addRow("Indice glycemique :", self.glycemic_edit)

        return self._form_scroll(w)

    def _build_photo_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Photo de la recette"))

        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(400, 300)
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setStyleSheet("background-color: #F0E8D8; border-radius: 12px; border: 2px dashed #D4A574;")
        self.photo_preview.setText("Aucune photo selectionnee")
        self.photo_preview.setFont(QFont("Arial", 14))
        layout.addWidget(self.photo_preview)

        btn_row = QHBoxLayout()
        select_btn = QPushButton("Choisir une photo")
        select_btn.clicked.connect(self._select_photo)
        remove_btn = QPushButton("Supprimer la photo")
        remove_btn.setObjectName("secondary-btn")
        remove_btn.clicked.connect(self._remove_photo)
        btn_row.addWidget(select_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("Formats acceptes: JPG, PNG, GIF, BMP, WEBP\nLa photo sera copiee dans le dossier de l'application."))
        layout.addStretch()
        return w

    def _select_photo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selectionner une photo",
            os.path.expanduser("~"),
            "Images (*.jpg *.jpeg *.png *.gif *.bmp *.webp);;Tous (*.*)"
        )
        if filepath:
            self._image_path = filepath
            pix = QPixmap(filepath).scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_preview.setPixmap(pix)
            self.photo_preview.setText("")

    def _remove_photo(self):
        self._image_path = ''
        self.photo_preview.clear()
        self.photo_preview.setText("Aucune photo selectionnee")

    def _collect_data(self):
        data = {
            'name': self.name_edit.text().strip(),
            'other_names': self.other_names_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'history': self.history_edit.toPlainText().strip(),
            'author': self.author_edit.text().strip(),
            'source': self.source_edit.text().strip(),
            'cuisine_type': self.cuisine_edit.currentText(),
            'region': self.region_edit.text().strip(),
            'occasion': self.occasion_edit.currentText(),
            'dish_type': self.dish_type_edit.currentText(),
            'category': self.category_edit.currentText(),
            'diet': self.diet_edit.currentText(),
            'ideal_season': self.season_edit.currentText(),
            'prep_time': self.prep_time.value(),
            'cook_time': self.cook_time.value(),
            'rest_time': self.rest_time.value(),
            'difficulty': self.difficulty_edit.currentText(),
            'servings': self.servings_edit.value(),
            'estimated_cost': self.cost_edit.text().strip(),
            'rating': self.rating_edit.value(),
            'calories_per_serving': self.calories_edit.value(),
            'proteins': self.proteins_edit.value(),
            'carbs': self.carbs_edit.value(),
            'fats': self.fats_edit.value(),
            'fiber': self.fiber_edit.value(),
            'sugar': self.sugar_edit.value(),
            'salt': self.salt_edit.value(),
            'vitamins': self.vitamins_edit.text().strip(),
            'minerals': self.minerals_edit.text().strip(),
            'oven_temperature': self.oven_temp_edit.value(),
            'fire_power': self.fire_power_edit.text().strip(),
            'cooking_type': self.cooking_type_edit.currentText(),
            'fridge_duration': self.fridge_dur_edit.text().strip(),
            'freezer_duration': self.freezer_dur_edit.text().strip(),
            'reheating_method': self.reheating_edit.text().strip(),
            'storage_method': self.storage_edit.text().strip(),
            'plate_type': self.plate_type_edit.text().strip(),
            'food_arrangement': self.food_arrangement_edit.text().strip(),
            'decoration': self.decoration_edit.text().strip(),
            'garnish': self.garnish_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
            'aromatic_profile': self.aromatic_edit.text().strip(),
            'taste_intensity': self.taste_intensity_edit.text().strip(),
            'texture': self.texture_edit.text().strip(),
            'glycemic_index': self.glycemic_edit.text().strip(),
        }

        # Tags
        tags_text = self.tags_edit.text().strip()
        data['tags'] = [t.strip() for t in tags_text.split(',') if t.strip()] if tags_text else []

        # Ingredients
        ingredients = []
        for row in range(self.ingredients_table.rowCount()):
            name_w = self.ingredients_table.cellWidget(row, 0)
            name = name_w.text().strip() if name_w else ''
            if not name:
                continue
            qty_w = self.ingredients_table.cellWidget(row, 1)
            unit_w = self.ingredients_table.cellWidget(row, 2)
            prep_item = self.ingredients_table.item(row, 3)
            opt_w = self.ingredients_table.cellWidget(row, 4)
            rep_item = self.ingredients_table.item(row, 5)
            qual_item = self.ingredients_table.item(row, 6)

            opt_check = opt_w.property("checkbox") if opt_w else None

            ingredients.append({
                'name': name,
                'quantity': qty_w.value() if qty_w else 0,
                'unit': unit_w.currentText() if unit_w else '',
                'preparation': prep_item.text() if prep_item else '',
                'optional': opt_check.isChecked() if opt_check else False,
                'replacement': rep_item.text() if rep_item else '',
                'quality': qual_item.text() if qual_item else ''
            })
        data['ingredients'] = ingredients

        # Steps
        steps = []
        for i, step_data in enumerate(self._steps, 1):
            desc = step_data['desc'].toPlainText().strip()
            if desc:
                steps.append({
                    'step_number': i,
                    'description': desc,
                    'duration': step_data['dur'].value(),
                    'temperature': step_data['temp'].value(),
                    'technique': step_data['tech'].currentText()
                })
        data['steps'] = steps

        # Equipment
        equipment = [eq for eq, cb in self.equipment_checks.items() if cb.isChecked()]
        other_eq = self.other_equipment_edit.text().strip()
        if other_eq:
            equipment.extend([e.strip() for e in other_eq.split(',') if e.strip()])
        data['equipment'] = equipment

        # Allergens
        data['allergens'] = [al for al, cb in self.allergen_checks.items() if cb.isChecked()]

        # Tips
        tips = []
        tip_sources = [
            (self.tips_edit, 'astuces'),
            (self.errors_edit, 'erreurs'),
            (self.variants_edit, 'variantes'),
            (self.accompaniments_edit, 'accompagnements'),
            (self.accords_edit, 'accords'),
        ]
        for te, tip_type in tip_sources:
            text = te.toPlainText().strip()
            if text:
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        tips.append({'tip_type': tip_type, 'content': line})
        data['tips'] = tips

        # Image
        if self._image_path and os.path.exists(self._image_path):
            os.makedirs(IMAGES_DIR, exist_ok=True)
            ext = os.path.splitext(self._image_path)[1]
            safe_name = data['name'].replace(' ', '_').replace('/', '_')[:50]
            dest = os.path.join(IMAGES_DIR, f"{safe_name}{ext}")
            # Avoid overwrite
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(IMAGES_DIR, f"{safe_name}_{counter}{ext}")
                counter += 1
            shutil.copy2(self._image_path, dest)
            data['image_path'] = dest
        else:
            data['image_path'] = ''

        return data

    def _save(self):
        data = self._collect_data()

        if not data['name']:
            QMessageBox.warning(self, "Champ manquant", "Le nom de la recette est obligatoire.")
            self.tabs.setCurrentIndex(0)
            self.name_edit.setFocus()
            return

        try:
            db_manager.add_recipe(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer la recette :\n{e}")
