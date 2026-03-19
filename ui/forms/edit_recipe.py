import os
import json
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from ui.forms.add_recipe import AddRecipeDialog
from database import db_manager
from config import UNITS, TECHNIQUES, EQUIPMENT, ALLERGENS, IMAGES_DIR


class EditRecipeDialog(AddRecipeDialog):
    def __init__(self, recipe, parent=None):
        self.recipe_data = recipe
        super().__init__(parent)
        self.setWindowTitle(f"Modifier : {recipe['name']}")
        self._prefill()

    def _prefill(self):
        r = self.recipe_data

        # Identification tab
        self.name_edit.setText(r.get('name', ''))
        self.other_names_edit.setText(r.get('other_names', ''))
        self.description_edit.setPlainText(r.get('description', ''))
        self.history_edit.setPlainText(r.get('history', ''))
        self.author_edit.setText(r.get('author', ''))
        self.source_edit.setText(r.get('source', ''))

        self._set_combo_text(self.cuisine_edit, r.get('cuisine_type', ''))
        self.region_edit.setText(r.get('region', ''))
        self._set_combo_text(self.occasion_edit, r.get('occasion', ''))
        self._set_combo_text(self.dish_type_edit, r.get('dish_type', ''))
        self._set_combo_text(self.category_edit, r.get('category', ''))
        self._set_combo_text(self.diet_edit, r.get('diet', ''))
        self._set_combo_text(self.season_edit, r.get('ideal_season', ''))

        # Time tab
        self.prep_time.setValue(r.get('prep_time', 0) or 0)
        self.cook_time.setValue(r.get('cook_time', 0) or 0)
        self.rest_time.setValue(r.get('rest_time', 0) or 0)
        self._set_combo_text(self.difficulty_edit, r.get('difficulty', 'Facile'))
        self.servings_edit.setValue(r.get('servings', 4) or 4)
        self.cost_edit.setText(r.get('estimated_cost', ''))
        self.rating_edit.setValue(r.get('rating', 0) or 0)

        # Ingredients - clear existing rows and re-add
        self.ingredients_table.setRowCount(0)

        for ing in r.get('ingredients', []):
            self._add_ingredient_row()
            row = self.ingredients_table.rowCount() - 1

            name_w = self.ingredients_table.cellWidget(row, 0)
            if name_w:
                name_w.setText(ing.get('ingredient_name', ''))

            qty_w = self.ingredients_table.cellWidget(row, 1)
            if qty_w:
                qty_w.setValue(ing.get('quantity', 0) or 0)

            unit_w = self.ingredients_table.cellWidget(row, 2)
            if unit_w:
                unit_w.setCurrentText(ing.get('unit', ''))

            prep_item = self.ingredients_table.item(row, 3)
            if prep_item:
                prep_item.setText(ing.get('preparation', ''))
            else:
                self.ingredients_table.setItem(row, 3, QTableWidgetItem(ing.get('preparation', '')))

            opt_w = self.ingredients_table.cellWidget(row, 4)
            if opt_w:
                cb = opt_w.property("checkbox")
                if cb:
                    cb.setChecked(bool(ing.get('optional', 0)))

            rep_item = self.ingredients_table.item(row, 5)
            if rep_item:
                rep_item.setText(ing.get('replacement', ''))
            else:
                self.ingredients_table.setItem(row, 5, QTableWidgetItem(ing.get('replacement', '')))

            qual_item = self.ingredients_table.item(row, 6)
            if qual_item:
                qual_item.setText(ing.get('quality', ''))
            else:
                self.ingredients_table.setItem(row, 6, QTableWidgetItem(ing.get('quality', '')))

        # Steps - clear existing steps widgets
        while self.steps_layout.count() > 1:  # keep the stretch
            item = self.steps_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._steps = []

        for step in r.get('steps', []):
            self._add_step()
            s = self._steps[-1]
            s['desc'].setPlainText(step.get('description', ''))
            s['dur'].setValue(step.get('duration', 0) or 0)
            s['temp'].setValue(step.get('temperature', 0) or 0)
            s['tech'].setCurrentText(step.get('technique', ''))

        # Equipment & Allergens
        for eq in r.get('equipment', []):
            if eq in self.equipment_checks:
                self.equipment_checks[eq].setChecked(True)

        for al in r.get('allergens', []):
            if al in self.allergen_checks:
                self.allergen_checks[al].setChecked(True)

        # Nutrition
        self.calories_edit.setValue(r.get('calories_per_serving', 0) or 0)
        self.proteins_edit.setValue(r.get('proteins', 0) or 0)
        self.carbs_edit.setValue(r.get('carbs', 0) or 0)
        self.fats_edit.setValue(r.get('fats', 0) or 0)
        self.fiber_edit.setValue(r.get('fiber', 0) or 0)
        self.sugar_edit.setValue(r.get('sugar', 0) or 0)
        self.salt_edit.setValue(r.get('salt', 0) or 0)
        self.vitamins_edit.setText(r.get('vitamins', ''))
        self.minerals_edit.setText(r.get('minerals', ''))

        # Cooking & Conservation
        self.oven_temp_edit.setValue(r.get('oven_temperature', 0) or 0)
        self.fire_power_edit.setText(r.get('fire_power', ''))
        self._set_combo_text(self.cooking_type_edit, r.get('cooking_type', ''))
        self.fridge_dur_edit.setText(r.get('fridge_duration', ''))
        self.freezer_dur_edit.setText(r.get('freezer_duration', ''))
        self.reheating_edit.setText(r.get('reheating_method', ''))
        self.storage_edit.setText(r.get('storage_method', ''))
        self.plate_type_edit.setText(r.get('plate_type', ''))
        self.food_arrangement_edit.setText(r.get('food_arrangement', ''))
        self.decoration_edit.setText(r.get('decoration', ''))
        self.garnish_edit.setText(r.get('garnish', ''))

        # Tips & Tags
        tips_by_type = {}
        for tip in r.get('tips', []):
            t = tip.get('tip_type', '')
            tips_by_type.setdefault(t, []).append(tip.get('content', ''))

        self.tips_edit.setPlainText('\n'.join(tips_by_type.get('astuces', [])))
        self.errors_edit.setPlainText('\n'.join(tips_by_type.get('erreurs', [])))
        self.variants_edit.setPlainText('\n'.join(tips_by_type.get('variantes', [])))
        self.accompaniments_edit.setPlainText('\n'.join(tips_by_type.get('accompagnements', [])))
        self.accords_edit.setPlainText('\n'.join(tips_by_type.get('accords', [])))

        tags_raw = r.get('tags', '[]')
        if isinstance(tags_raw, str):
            try:
                tags = json.loads(tags_raw)
            except Exception:
                tags = []
        else:
            tags = tags_raw or []
        self.tags_edit.setText(', '.join(tags))

        self.notes_edit.setPlainText(r.get('notes', ''))
        self.aromatic_edit.setText(r.get('aromatic_profile', ''))
        self.taste_intensity_edit.setText(r.get('taste_intensity', ''))
        self.texture_edit.setText(r.get('texture', ''))
        self.glycemic_edit.setText(r.get('glycemic_index', ''))

        # Photo
        img_path = r.get('image_path', '')
        if img_path and os.path.exists(img_path):
            self._image_path = img_path
            pix = QPixmap(img_path).scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_preview.setPixmap(pix)
            self.photo_preview.setText("")

    def _set_combo_text(self, combo, text):
        if not text:
            return
        idx = combo.findText(text)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        elif combo.isEditable():
            combo.setCurrentText(text)

    def _save(self):
        data = self._collect_data()

        if not data['name']:
            QMessageBox.warning(self, "Champ manquant", "Le nom de la recette est obligatoire.")
            self.tabs.setCurrentIndex(0)
            self.name_edit.setFocus()
            return

        try:
            db_manager.update_recipe(self.recipe_data['id'], data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de modifier la recette :\n{e}")
